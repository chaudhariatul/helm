"""
Amazon Bedrock Client for AWS Bedrock API integration.

This client provides comprehensive integration with AWS Bedrock API for Amazon Nova 2 models,
with enhanced logging, retry logic, and error handling specifically designed for MedHELM benchmarks.
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from helm.common.cache import CacheConfig
from helm.clients.client import CachingClient, truncate_and_tokenize_response_text
from helm.common.hierarchical_logger import hlog, hexception
from helm.common.request import Request, RequestResult, GeneratedOutput, wrap_request_time
from helm.clients.bedrock_utils import get_bedrock_client_v1
from helm.proxy.retry import NonRetriableException
from helm.tokenizers.tokenizer import Tokenizer


# Model ID mapping: HELM model name -> Bedrock model ID
MODEL_ID_MAPPING = {
    "amazon/nova-lite-v1:0": "us.amazon.nova-lite-v1:0",
    "amazon/nova-pro-v1:0": "us.amazon.nova-pro-v1:0",
    "amazon/nova-2-lite-v1:0": "us.amazon.nova-2-lite-v1:0",
    "amazon/nova-2-pro-v1:0": "us.amazon.nova-2-pro-v1:0",
    "amazon/nova-2-sonic-v1:0": "us.amazon.nova-2-sonic-v1:0",
}

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_TIMEOUT = 120  # seconds

# Finish reason mapping
FINISH_REASON_MAPPING = {
    "end_turn": "endoftext",
    "max_tokens": "length",
    "stop_sequence": "stop",
    "content_filtered": "content_filter",
}


class _ContentBlock(TypedDict):
    """Type definition for content blocks in messages."""
    text: str


class _Message(TypedDict):
    """Type definition for messages in the conversation."""
    role: str
    content: List[_ContentBlock]


class AmazonBedrockClient(CachingClient):
    """
    Amazon Bedrock Client for AWS Bedrock API integration.
    
    This client provides comprehensive integration with AWS Bedrock API, including:
    - AWS credential handling (environment variables, credential files, IAM roles)
    - Model ID mapping for Amazon Nova models
    - Request formatting with parameter mapping
    - Response parsing with token usage extraction
    - Retry logic with exponential backoff
    - Comprehensive logging for monitoring and debugging
    
    Attributes:
        tokenizer: Tokenizer instance for text tokenization
        tokenizer_name: Name of the tokenizer to use
        bedrock_client: Boto3 Bedrock client instance
        bedrock_model_id: Optional override for Bedrock model ID
        max_retries: Maximum number of retry attempts
        base_delay: Base delay for exponential backoff (seconds)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        cache_config: CacheConfig,
        tokenizer: Tokenizer,
        tokenizer_name: str,
        assumed_role: Optional[str] = None,
        region: Optional[str] = None,
        bedrock_model_id: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the Amazon Bedrock Client.
        
        Args:
            cache_config: Cache configuration for request caching
            tokenizer: Tokenizer instance for text tokenization
            tokenizer_name: Name of the tokenizer to use
            assumed_role: Optional AWS IAM role ARN to assume
            region: Optional AWS region (defaults to AWS_REGION or us-east-1)
            bedrock_model_id: Optional override for Bedrock model ID
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay for exponential backoff in seconds (default: 1.0)
            timeout: Request timeout in seconds (default: 120)
        """
        super().__init__(cache_config=cache_config)
        self.tokenizer = tokenizer
        self.tokenizer_name = tokenizer_name
        self.bedrock_model_id = bedrock_model_id
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.timeout = timeout
        
        # Initialize Bedrock client with credential handling
        hlog(f"Initializing AmazonBedrockClient with region={region}, assumed_role={assumed_role}")
        try:
            self.bedrock_client = get_bedrock_client_v1(
                assumed_role=assumed_role or os.environ.get("BEDROCK_ASSUME_ROLE", None),
                region=region,
                read_timeout=timeout,
                connect_timeout=timeout,
                max_attempts=max_retries,
            )
            hlog("AmazonBedrockClient: Successfully initialized Bedrock client")
        except Exception as e:
            hexception(e)
            raise NonRetriableException(f"Failed to initialize Bedrock client: {str(e)}")

    def _get_model_id(self, helm_model_name: str) -> str:
        """
        Map HELM model name to Bedrock model ID.
        
        Args:
            helm_model_name: HELM model name (e.g., "amazon/nova-lite-v1:0")
            
        Returns:
            Bedrock model ID (e.g., "us.amazon.nova-lite-v1:0")
        """
        if self.bedrock_model_id:
            return self.bedrock_model_id
            
        model_id = MODEL_ID_MAPPING.get(helm_model_name, helm_model_name)
        hlog(f"Model ID mapping: {helm_model_name} -> {model_id}")
        return model_id

    def _get_messages_from_request(self, request: Request) -> List[_Message]:
        """
        Convert HELM request to Bedrock messages format.
        
        Args:
            request: HELM request object
            
        Returns:
            List of messages in Bedrock format
            
        Raises:
            ValueError: If both prompt and messages are set, or if multimodal_prompt is used
        """
        if request.prompt and request.messages:
            raise ValueError(f"Only one of `prompt` and `messages` may be set in request: {request}")
        if request.multimodal_prompt:
            raise ValueError(f"`multimodal_prompt` is not supported in request: {request}")

        if request.messages:
            return [
                {"role": message["role"], "content": [{"text": message["content"]}]} 
                for message in request.messages
            ]
        else:
            return [{"role": "user", "content": [{"text": request.prompt}]}]

    def _format_request(self, request: Request) -> Dict[str, Any]:
        """
        Format HELM request to Bedrock API format.
        
        Converts HELM Request to Bedrock converse API format with parameter mapping:
        - temperature -> inferenceConfig.temperature
        - top_p -> inferenceConfig.topP
        - max_tokens -> inferenceConfig.maxTokens
        - stop_sequences -> inferenceConfig.stopSequences
        
        Args:
            request: HELM request object
            
        Returns:
            Dictionary with Bedrock API request parameters
        """
        model_id = self._get_model_id(request.model)
        messages = self._get_messages_from_request(request)
        
        # Build inference configuration
        inference_config: Dict[str, Any] = {
            "temperature": request.temperature,
            "maxTokens": request.max_tokens,
            "topP": request.top_p,
        }
        
        # Add stop sequences if provided
        if request.stop_sequences:
            inference_config["stopSequences"] = request.stop_sequences
        
        bedrock_request = {
            "modelId": model_id,
            "inferenceConfig": inference_config,
            "messages": messages,
        }
        
        hlog(f"Formatted request for model {model_id}: "
             f"temp={request.temperature}, max_tokens={request.max_tokens}, top_p={request.top_p}")
        
        return bedrock_request

    def _parse_response(self, response: Dict[str, Any], request: Request) -> List[GeneratedOutput]:
        """
        Parse Bedrock API response to HELM format.
        
        Extracts:
        - Generated text from output.message.content[0].text
        - Token usage from usage.inputTokens and usage.outputTokens
        - Finish reason from stopReason
        
        Args:
            response: Bedrock API response
            request: Original HELM request
            
        Returns:
            List of GeneratedOutput objects
        """
        completions: List[GeneratedOutput] = []
        
        # Extract output text
        raw_completion = response["output"]
        output_text = raw_completion["message"]["content"][0]["text"]
        
        # Extract finish reason
        finish_reason = FINISH_REASON_MAPPING.get(
            response["stopReason"],
            response["stopReason"]
        )
        
        # Extract token usage
        usage = response.get("usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        total_tokens = input_tokens + output_tokens
        
        hlog(f"Response: {len(output_text)} chars, "
             f"input_tokens={input_tokens}, output_tokens={output_tokens}, "
             f"finish_reason={finish_reason}")
        
        # Truncate and tokenize the response text
        completion = truncate_and_tokenize_response_text(
            output_text.lstrip(),
            request,
            self.tokenizer,
            self.tokenizer_name,
            original_finish_reason=finish_reason
        )
        
        completions.append(completion)
        return completions

    def _make_request_with_retry(self, bedrock_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make request to Bedrock API with exponential backoff retry logic.
        
        Retry strategy:
        - Max retries: configured via max_retries (default: 3)
        - Base delay: configured via base_delay (default: 1.0s)
        - Exponential backoff: delay = base_delay * (2 ** attempt)
        - Max total time: configured via timeout (default: 120s)
        
        Args:
            bedrock_request: Formatted Bedrock API request
            
        Returns:
            Bedrock API response
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                # Check if we've exceeded total timeout
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    raise Exception(f"Request timeout after {elapsed:.2f}s (limit: {self.timeout}s)")
                
                hlog(f"Making request attempt {attempt + 1}/{self.max_retries}")
                response = self.bedrock_client.converse(**bedrock_request)
                hlog(f"Request successful on attempt {attempt + 1}")
                return response
                
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                hlog(f"Request attempt {attempt + 1} failed: {error_msg}")
                
                # Check if this is a non-retriable error
                if "ValidationException" in error_msg or "ResourceNotFoundException" in error_msg:
                    hexception(e)
                    raise NonRetriableException(f"Non-retriable error: {error_msg}")
                
                # If this was the last attempt, raise the exception
                if attempt == self.max_retries - 1:
                    hexception(e)
                    raise
                
                # Calculate delay with exponential backoff
                delay = self.base_delay * (2 ** attempt)
                hlog(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        # This should never be reached, but just in case
        if last_exception:
            hexception(last_exception)
            raise last_exception
        raise Exception("Failed to make request after all retry attempts")

    def make_request(self, request: Request) -> RequestResult:
        """
        Main entry point for making requests to Amazon Bedrock.
        
        This method:
        1. Formats the HELM request to Bedrock API format
        2. Checks cache for existing response
        3. Makes the request with retry logic if not cached
        4. Parses the response and extracts metadata
        5. Returns a RequestResult with completions and metadata
        
        Args:
            request: HELM request object
            
        Returns:
            RequestResult with success status, completions, and metadata
        """
        # Format request
        bedrock_request = self._format_request(request)
        cache_key = CachingClient.make_cache_key(bedrock_request, request)
        
        # Log request details
        hlog(f"Processing request for model={request.model}, "
             f"prompt_length={len(request.prompt) if request.prompt else 0}")
        
        # Define the request function with timing
        def do_it() -> Dict[Any, Any]:
            request_start = time.time()
            try:
                response = self._make_request_with_retry(bedrock_request)
                latency = time.time() - request_start
                hlog(f"Request completed in {latency:.3f}s")
                return response
            except Exception as e:
                latency = time.time() - request_start
                hlog(f"Request failed after {latency:.3f}s")
                raise
        
        # Try to get from cache or make request
        try:
            response, cached = self.cache.get(cache_key, wrap_request_time(do_it))
            
            if cached:
                hlog("Response retrieved from cache")
            
            # Parse response
            completions = self._parse_response(response, request)
            
            # Extract timing information
            # For cached responses, use stored timing; for new requests, extract from response
            if cached:
                request_time = response.get("request_time", 0)
                request_datetime = response.get("request_datetime", int(datetime.now().timestamp()))
            else:
                # Extract latency from response metadata
                latency_ms = response.get("metrics", {}).get("latencyMs", 0)
                request_time = latency_ms / 1000.0 if latency_ms > 0 else response.get("request_time", 0)
                
                # Parse datetime from HTTP headers
                date_str = response.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("date")
                if date_str:
                    try:
                        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
                        request_datetime = int(dt.timestamp())
                    except Exception:
                        request_datetime = int(datetime.now().timestamp())
                else:
                    request_datetime = int(datetime.now().timestamp())
            
            hlog(f"Request completed: cached={cached}, "
                 f"request_time={request_time:.3f}s, "
                 f"num_completions={len(completions)}")
            
            return RequestResult(
                success=True,
                cached=cached,
                request_time=request_time,
                request_datetime=request_datetime,
                completions=completions,
                embedding=[],
            )
            
        except NonRetriableException as e:
            # Non-retriable errors should be returned immediately
            error_msg = str(e)
            hlog(f"Non-retriable error: {error_msg}")
            return RequestResult(
                success=False,
                cached=False,
                error=error_msg,
                completions=[],
                embedding=[],
            )
            
        except Exception as e:
            # All other errors
            hexception(e)
            error_msg = str(e)
            hlog(f"Request failed with error: {error_msg}")
            return RequestResult(
                success=False,
                cached=False,
                error=error_msg,
                completions=[],
                embedding=[],
            )
