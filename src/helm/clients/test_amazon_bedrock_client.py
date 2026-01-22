"""
Unit tests for AmazonBedrockClient.

Tests cover:
- Initialization with various credential configurations
- Model ID mapping
- Request formatting
- Response parsing
- Retry logic with exponential backoff
- Error handling for retriable and non-retriable errors
- Logging and monitoring
"""

import os
import time
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from helm.common.cache_backend_config import BlackHoleCacheBackendConfig
from helm.common.request import Request, RequestResult
from helm.clients.amazon_bedrock_client import (
    AmazonBedrockClient,
    MODEL_ID_MAPPING,
    FINISH_REASON_MAPPING,
)
from helm.proxy.retry import NonRetriableException


@pytest.fixture
def mock_tokenizer():
    """Create a mock tokenizer for testing."""
    tokenizer = MagicMock()
    tokenizer.tokenize = MagicMock(return_value=MagicMock(raw_tokens=["test", "tokens"]))
    tokenizer.decode = MagicMock(return_value=MagicMock(text="test"))
    return tokenizer


@pytest.fixture
def cache_config():
    """Create a cache config for testing."""
    return BlackHoleCacheBackendConfig().get_cache_config("test")


@pytest.fixture
def mock_bedrock_client():
    """Create a mock Bedrock client."""
    client = MagicMock()
    client._endpoint = "https://bedrock-runtime.us-east-1.amazonaws.com"
    return client


class TestAmazonBedrockClientInit:
    """Test client initialization."""

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_init_default_params(self, mock_get_client, mock_tokenizer, cache_config):
        """Test initialization with default parameters."""
        mock_get_client.return_value = MagicMock()
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        assert client.tokenizer == mock_tokenizer
        assert client.tokenizer_name == "test_tokenizer"
        assert client.max_retries == 3
        assert client.base_delay == 1.0
        assert client.timeout == 120
        assert client.bedrock_model_id is None

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_init_with_custom_params(self, mock_get_client, mock_tokenizer, cache_config):
        """Test initialization with custom parameters."""
        mock_get_client.return_value = MagicMock()
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
            assumed_role="arn:aws:iam::123456789:role/test-role",
            region="us-west-2",
            bedrock_model_id="custom.model.id",
            max_retries=5,
            base_delay=2.0,
            timeout=300,
        )
        
        assert client.bedrock_model_id == "custom.model.id"
        assert client.max_retries == 5
        assert client.base_delay == 2.0
        assert client.timeout == 300
        
        # Verify client was initialized with correct params
        mock_get_client.assert_called_once()
        call_kwargs = mock_get_client.call_args.kwargs
        assert call_kwargs["region"] == "us-west-2"
        assert call_kwargs["read_timeout"] == 300
        assert call_kwargs["max_attempts"] == 5

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_init_with_env_assumed_role(self, mock_get_client, mock_tokenizer, cache_config, monkeypatch):
        """Test initialization with assumed role from environment variable."""
        mock_get_client.return_value = MagicMock()
        monkeypatch.setenv("BEDROCK_ASSUME_ROLE", "arn:aws:iam::123456789:role/env-role")
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        # Verify assumed role from env was used
        call_kwargs = mock_get_client.call_args.kwargs
        assert call_kwargs["assumed_role"] == "arn:aws:iam::123456789:role/env-role"

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_init_failure_raises_non_retriable(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that client initialization failure raises NonRetriableException."""
        mock_get_client.side_effect = Exception("Failed to initialize")
        
        with pytest.raises(NonRetriableException, match="Failed to initialize Bedrock client"):
            AmazonBedrockClient(
                cache_config=cache_config,
                tokenizer=mock_tokenizer,
                tokenizer_name="test_tokenizer",
            )


class TestModelIDMapping:
    """Test model ID mapping functionality."""

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_model_id_mapping(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that model IDs are correctly mapped."""
        mock_get_client.return_value = MagicMock()
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        # Test all mapped model IDs
        for helm_name, bedrock_id in MODEL_ID_MAPPING.items():
            assert client._get_model_id(helm_name) == bedrock_id

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_model_id_passthrough(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that unmapped model IDs are passed through."""
        mock_get_client.return_value = MagicMock()
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        # Test unmapped model ID
        custom_id = "custom.model.id"
        assert client._get_model_id(custom_id) == custom_id

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_model_id_override(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that bedrock_model_id parameter overrides mapping."""
        mock_get_client.return_value = MagicMock()
        override_id = "override.model.id"
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
            bedrock_model_id=override_id,
        )
        
        # Should always return override, regardless of input
        assert client._get_model_id("amazon/nova-lite-v1:0") == override_id
        assert client._get_model_id("any-other-model") == override_id


class TestRequestFormatting:
    """Test request formatting functionality."""

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_format_request_with_prompt(self, mock_get_client, mock_tokenizer, cache_config):
        """Test formatting request with a simple prompt."""
        mock_get_client.return_value = MagicMock()
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Hello, world!",
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
        )
        
        formatted = client._format_request(request)
        
        assert formatted["modelId"] == "us.amazon.nova-2-lite-v1:0"
        assert formatted["inferenceConfig"]["temperature"] == 0.7
        assert formatted["inferenceConfig"]["maxTokens"] == 100
        assert formatted["inferenceConfig"]["topP"] == 0.9
        assert len(formatted["messages"]) == 1
        assert formatted["messages"][0]["role"] == "user"
        assert formatted["messages"][0]["content"][0]["text"] == "Hello, world!"

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_format_request_with_messages(self, mock_get_client, mock_tokenizer, cache_config):
        """Test formatting request with messages."""
        mock_get_client.return_value = MagicMock()
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = Request(
            model="amazon/nova-2-pro-v1:0",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
            ],
            temperature=0.5,
            max_tokens=200,
            top_p=0.95,
        )
        
        formatted = client._format_request(request)
        
        assert formatted["modelId"] == "us.amazon.nova-2-pro-v1:0"
        assert len(formatted["messages"]) == 3
        assert formatted["messages"][0]["role"] == "user"
        assert formatted["messages"][1]["role"] == "assistant"
        assert formatted["messages"][2]["role"] == "user"

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_format_request_with_stop_sequences(self, mock_get_client, mock_tokenizer, cache_config):
        """Test formatting request with stop sequences."""
        mock_get_client.return_value = MagicMock()
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Tell me a story",
            temperature=0.8,
            max_tokens=500,
            top_p=1.0,
            stop_sequences=["\n\n", "THE END"],
        )
        
        formatted = client._format_request(request)
        
        assert "stopSequences" in formatted["inferenceConfig"]
        assert formatted["inferenceConfig"]["stopSequences"] == ["\n\n", "THE END"]

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_format_request_both_prompt_and_messages_raises(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that having both prompt and messages raises ValueError."""
        mock_get_client.return_value = MagicMock()
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Hello",
            messages=[{"role": "user", "content": "Hello"}],
        )
        
        with pytest.raises(ValueError, match="Only one of `prompt` and `messages` may be set"):
            client._format_request(request)


class TestResponseParsing:
    """Test response parsing functionality."""

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_parse_response_basic(self, mock_get_client, mock_tokenizer, cache_config):
        """Test parsing a basic response."""
        mock_get_client.return_value = MagicMock()
        mock_tokenizer.tokenize.return_value = MagicMock(
            raw_tokens=["Hello", ",", " world", "!"]
        )
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        response = {
            "output": {
                "message": {
                    "content": [{"text": "Hello, world!"}]
                }
            },
            "stopReason": "end_turn",
            "usage": {
                "inputTokens": 10,
                "outputTokens": 4,
            },
        }
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Say hello",
            max_tokens=100,
        )
        
        completions = client._parse_response(response, request)
        
        assert len(completions) == 1
        assert completions[0].text == "Hello, world!"

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_parse_response_finish_reason_mapping(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that finish reasons are correctly mapped."""
        mock_get_client.return_value = MagicMock()
        mock_tokenizer.tokenize.return_value = MagicMock(raw_tokens=["test"])
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = Request(model="amazon/nova-2-lite-v1:0", prompt="test", max_tokens=100)
        
        # Test each finish reason mapping
        for bedrock_reason, helm_reason in FINISH_REASON_MAPPING.items():
            response = {
                "output": {
                    "message": {
                        "content": [{"text": "test"}]
                    }
                },
                "stopReason": bedrock_reason,
                "usage": {"inputTokens": 1, "outputTokens": 1},
            }
            
            completions = client._parse_response(response, request)
            # The finish_reason is set by truncate_and_tokenize_response_text
            # based on the original_finish_reason parameter
            assert len(completions) == 1


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    @patch("helm.clients.amazon_bedrock_client.time.sleep")
    def test_retry_success_on_second_attempt(self, mock_sleep, mock_get_client, mock_tokenizer, cache_config):
        """Test that retry succeeds on second attempt."""
        mock_bedrock = MagicMock()
        mock_get_client.return_value = mock_bedrock
        
        # Fail once, then succeed
        mock_bedrock.converse.side_effect = [
            Exception("Temporary error"),
            {
                "output": {"message": {"content": [{"text": "Success"}]}},
                "stopReason": "end_turn",
                "usage": {"inputTokens": 10, "outputTokens": 5},
                "metrics": {"latencyMs": 100},
            },
        ]
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = {"modelId": "test", "messages": [], "inferenceConfig": {}}
        response = client._make_request_with_retry(request)
        
        assert response is not None
        assert mock_bedrock.converse.call_count == 2
        # Should sleep once after first failure
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(1.0)  # base_delay * (2 ** 0) = 1.0

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    @patch("helm.clients.amazon_bedrock_client.time.sleep")
    def test_retry_exponential_backoff(self, mock_sleep, mock_get_client, mock_tokenizer, cache_config):
        """Test exponential backoff delays."""
        mock_bedrock = MagicMock()
        mock_get_client.return_value = mock_bedrock
        
        # Fail twice, then succeed
        mock_bedrock.converse.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            {
                "output": {"message": {"content": [{"text": "Success"}]}},
                "stopReason": "end_turn",
                "usage": {"inputTokens": 10, "outputTokens": 5},
            },
        ]
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
            base_delay=2.0,
        )
        
        request = {"modelId": "test", "messages": [], "inferenceConfig": {}}
        response = client._make_request_with_retry(request)
        
        assert response is not None
        assert mock_sleep.call_count == 2
        # Check exponential backoff: 2.0 * (2 ** 0) = 2.0, 2.0 * (2 ** 1) = 4.0
        assert mock_sleep.call_args_list[0][0][0] == 2.0
        assert mock_sleep.call_args_list[1][0][0] == 4.0

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_retry_fails_after_max_attempts(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that retry fails after max attempts."""
        mock_bedrock = MagicMock()
        mock_get_client.return_value = mock_bedrock
        
        # Always fail
        mock_bedrock.converse.side_effect = Exception("Permanent error")
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
            max_retries=3,
        )
        
        request = {"modelId": "test", "messages": [], "inferenceConfig": {}}
        
        with pytest.raises(Exception, match="Permanent error"):
            client._make_request_with_retry(request)
        
        assert mock_bedrock.converse.call_count == 3

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_non_retriable_error_raises_immediately(self, mock_get_client, mock_tokenizer, cache_config):
        """Test that non-retriable errors raise immediately without retry."""
        mock_bedrock = MagicMock()
        mock_get_client.return_value = mock_bedrock
        
        # Validation error should not be retried
        mock_bedrock.converse.side_effect = Exception("ValidationException: Invalid parameter")
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = {"modelId": "test", "messages": [], "inferenceConfig": {}}
        
        with pytest.raises(NonRetriableException, match="Non-retriable error"):
            client._make_request_with_retry(request)
        
        # Should only try once
        assert mock_bedrock.converse.call_count == 1


class TestMakeRequest:
    """Test the main make_request method."""

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_make_request_success(self, mock_get_client, mock_tokenizer, cache_config):
        """Test successful request."""
        mock_bedrock = MagicMock()
        mock_get_client.return_value = mock_bedrock
        
        mock_bedrock.converse.return_value = {
            "output": {
                "message": {
                    "content": [{"text": "Hello, world!"}]
                }
            },
            "stopReason": "end_turn",
            "usage": {
                "inputTokens": 10,
                "outputTokens": 4,
            },
            "metrics": {
                "latencyMs": 250,
            },
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "date": "Mon, 22 Jan 2026 20:00:00 GMT"
                }
            },
        }
        
        mock_tokenizer.tokenize.return_value = MagicMock(
            raw_tokens=["Hello", ",", " world", "!"]
        )
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
        )
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Say hello",
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        assert result.cached is False
        assert len(result.completions) == 1
        assert result.completions[0].text == "Hello, world!"
        assert result.error is None

    @patch("helm.clients.amazon_bedrock_client.get_bedrock_client_v1")
    def test_make_request_error(self, mock_get_client, mock_tokenizer, cache_config):
        """Test request with error."""
        mock_bedrock = MagicMock()
        mock_get_client.return_value = mock_bedrock
        
        mock_bedrock.converse.side_effect = Exception("Service error")
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=mock_tokenizer,
            tokenizer_name="test_tokenizer",
            max_retries=1,
        )
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Test",
        )
        
        result = client.make_request(request)
        
        assert result.success is False
        assert result.cached is False
        assert len(result.completions) == 0
        assert "Service error" in result.error
