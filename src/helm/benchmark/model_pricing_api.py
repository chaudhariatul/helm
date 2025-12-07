"""
Model Pricing API Client Module

This module provides functionality to fetch live pricing information from AWS Pricing API
and other pricing sources for various AI models including AWS Bedrock models.

Usage:
    from helm.benchmark.model_pricing_api import LivePricingClient
    
    client = LivePricingClient()
    pricing = client.get_live_pricing("amazon/nova-pro-v1:0")
    if pricing:
        cost = pricing.calculate_cost(1000, 500)
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime, timedelta

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class LiveModelPricing:
    """Represents live pricing information for a model."""

    model_name: str
    input_price_per_million: float
    output_price_per_million: float
    notes: Optional[str] = None
    source: str = "live_api"
    fetched_at: Optional[str] = None

    @property
    def input_price_per_token(self) -> float:
        """Return the price per input token."""
        return self.input_price_per_million / 1_000_000

    @property
    def output_price_per_token(self) -> float:
        """Return the price per output token."""
        return self.output_price_per_million / 1_000_000

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the total cost for the given token counts.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD
        """
        input_cost = input_tokens * self.input_price_per_token
        output_cost = output_tokens * self.output_price_per_token
        return input_cost + output_cost


class PricingAPIError(Exception):
    """Exception raised when pricing API operations fail."""
    pass


class LivePricingClient:
    """Client for fetching live pricing information from various APIs."""

    def __init__(self, cache_ttl_minutes: int = 60):
        """
        Initialize the live pricing client.
        
        Args:
            cache_ttl_minutes: Time-to-live for cached pricing data in minutes (default: 60)
        """
        self._cache: Dict[str, tuple[LiveModelPricing, datetime]] = {}
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._pricing_client = None
        self._bedrock_client = None
        
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available. Live pricing from AWS will not work.")

    def _get_aws_pricing_client(self):
        """Get or create AWS Pricing API client."""
        if self._pricing_client is None and BOTO3_AVAILABLE:
            try:
                # AWS Pricing API is only available in us-east-1 and ap-south-1
                self._pricing_client = boto3.client('pricing', region_name='us-east-1')
            except Exception as e:
                logger.error(f"Failed to create AWS Pricing client: {e}")
                raise PricingAPIError(f"Failed to initialize AWS Pricing API client: {e}")
        return self._pricing_client

    def _get_bedrock_client(self):
        """Get or create AWS Bedrock client."""
        if self._bedrock_client is None and BOTO3_AVAILABLE:
            try:
                self._bedrock_client = boto3.client('bedrock', region_name='us-east-1')
            except Exception as e:
                logger.warning(f"Failed to create Bedrock client: {e}")
        return self._bedrock_client

    def _is_cache_valid(self, model_name: str) -> bool:
        """Check if cached pricing data is still valid."""
        if model_name not in self._cache:
            return False
        
        _, cached_time = self._cache[model_name]
        return datetime.now() - cached_time < self._cache_ttl

    def _get_from_cache(self, model_name: str) -> Optional[LiveModelPricing]:
        """Get pricing from cache if valid."""
        if self._is_cache_valid(model_name):
            pricing, _ = self._cache[model_name]
            logger.info(f"Retrieved pricing for {model_name} from cache")
            return pricing
        return None

    def _add_to_cache(self, model_name: str, pricing: LiveModelPricing) -> None:
        """Add pricing to cache."""
        self._cache[model_name] = (pricing, datetime.now())

    def _parse_bedrock_model_id(self, model_name: str) -> Optional[tuple[str, str]]:
        """
        Parse a model name into provider and model ID for Bedrock.
        
        Args:
            model_name: Model name (e.g., "amazon/nova-pro-v1:0")
            
        Returns:
            Tuple of (provider, model_id) or None if not a Bedrock model
        """
        # Map of common provider prefixes
        bedrock_providers = {
            'amazon': 'amazon',
            'anthropic': 'anthropic',
            'meta': 'meta',
            'mistralai': 'mistral',
            'cohere': 'cohere',
            'ai21': 'ai21',
        }
        
        if '/' in model_name:
            provider_prefix, model_part = model_name.split('/', 1)
            provider = bedrock_providers.get(provider_prefix.lower())
            if provider:
                return provider, model_name
        
        return None

    def _fetch_bedrock_pricing(self, model_name: str) -> Optional[LiveModelPricing]:
        """
        Fetch pricing for Bedrock models from AWS Pricing API.
        
        Args:
            model_name: Model name (e.g., "amazon/nova-pro-v1:0")
            
        Returns:
            LiveModelPricing object or None if pricing not found
        """
        if not BOTO3_AVAILABLE:
            raise PricingAPIError("boto3 is required for fetching live pricing from AWS")

        try:
            pricing_client = self._get_aws_pricing_client()
            
            # Parse model name to extract provider and model ID
            parsed = self._parse_bedrock_model_id(model_name)
            if not parsed:
                logger.warning(f"Could not parse Bedrock model name: {model_name}")
                return None
            
            provider, model_id = parsed
            
            # Search for the specific model in AWS Pricing API
            # Note: AWS Pricing API structure for Bedrock models
            filters = [
                {
                    'Type': 'TERM_MATCH',
                    'Field': 'ServiceCode',
                    'Value': 'AmazonBedrock'
                }
            ]
            
            try:
                response = pricing_client.get_products(
                    ServiceCode='AmazonBedrock',
                    Filters=filters,
                    MaxResults=100
                )
                
                # Parse pricing data from response
                input_price = None
                output_price = None
                
                for price_item in response.get('PriceList', []):
                    price_data = json.loads(price_item)
                    
                    # Check if this is the model we're looking for
                    product = price_data.get('product', {})
                    attributes = product.get('attributes', {})
                    
                    # Match model by various attributes
                    model_id_attr = attributes.get('modelId', '')
                    
                    # Check if this matches our model
                    if model_name.lower() in model_id_attr.lower() or model_id.lower() in model_id_attr.lower():
                        # Extract pricing from terms
                        terms = price_data.get('terms', {})
                        on_demand = terms.get('OnDemand', {})
                        
                        for term_key, term_data in on_demand.items():
                            price_dimensions = term_data.get('priceDimensions', {})
                            for dim_key, dim_data in price_dimensions.items():
                                description = dim_data.get('description', '').lower()
                                price_per_unit = float(dim_data.get('pricePerUnit', {}).get('USD', 0))
                                
                                if 'input' in description and 'token' in description:
                                    # Convert to per million tokens
                                    input_price = price_per_unit * 1_000_000
                                elif 'output' in description and 'token' in description:
                                    output_price = price_per_unit * 1_000_000
                
                if input_price is not None and output_price is not None:
                    return LiveModelPricing(
                        model_name=model_name,
                        input_price_per_million=input_price,
                        output_price_per_million=output_price,
                        notes=f"Fetched from AWS Pricing API for Bedrock",
                        source="aws_pricing_api",
                        fetched_at=datetime.now().isoformat()
                    )
                
                logger.warning(f"Could not find complete pricing data for {model_name} in AWS Pricing API")
                return None
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                logger.error(f"AWS Pricing API error ({error_code}): {error_message}")
                raise PricingAPIError(f"AWS Pricing API returned error: {error_code} - {error_message}")
                
        except BotoCoreError as e:
            logger.error(f"Boto3 core error: {e}")
            raise PricingAPIError(f"Failed to connect to AWS services: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching Bedrock pricing: {e}")
            raise PricingAPIError(f"Unexpected error: {e}")

    def _fetch_openai_pricing(self, model_name: str) -> Optional[LiveModelPricing]:
        """
        Fetch pricing for OpenAI models.
        
        Note: OpenAI doesn't provide a public pricing API, so this uses known pricing data.
        In a production system, you might scrape their pricing page or use a third-party service.
        
        Args:
            model_name: Model name (e.g., "openai/gpt-4o")
            
        Returns:
            LiveModelPricing object or None if not found
        """
        # Since OpenAI doesn't have a public pricing API, we'll return None
        # to indicate that live pricing is not available
        logger.warning(f"OpenAI does not provide a public pricing API for {model_name}")
        return None

    def _fetch_anthropic_pricing(self, model_name: str) -> Optional[LiveModelPricing]:
        """
        Fetch pricing for Anthropic models.
        
        Note: Anthropic doesn't provide a public pricing API currently.
        
        Args:
            model_name: Model name (e.g., "anthropic/claude-3-opus")
            
        Returns:
            LiveModelPricing object or None if not found
        """
        logger.warning(f"Anthropic does not provide a public pricing API for {model_name}")
        return None

    def get_live_pricing(
        self,
        model_name: str,
        use_cache: bool = True
    ) -> Optional[LiveModelPricing]:
        """
        Fetch live pricing information for a model.
        
        Args:
            model_name: Model name (e.g., "amazon/nova-pro-v1:0")
            use_cache: Whether to use cached pricing if available (default: True)
            
        Returns:
            LiveModelPricing object or None if pricing not available
            
        Raises:
            PricingAPIError: If API call fails
        """
        # Check cache first
        if use_cache:
            cached = self._get_from_cache(model_name)
            if cached:
                return cached

        try:
            # Determine which API to use based on model provider
            pricing = None
            
            if model_name.startswith(('amazon/', 'anthropic/', 'meta/', 'mistralai/', 'cohere/', 'ai21/')):
                # Try Bedrock pricing
                pricing = self._fetch_bedrock_pricing(model_name)
            elif model_name.startswith('openai/'):
                pricing = self._fetch_openai_pricing(model_name)
            elif model_name.startswith('anthropic/'):
                pricing = self._fetch_anthropic_pricing(model_name)
            else:
                logger.warning(f"Unknown model provider for {model_name}")
                return None
            
            # Cache the result if found
            if pricing:
                self._add_to_cache(model_name, pricing)
            
            return pricing
            
        except PricingAPIError:
            # Re-raise pricing API errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching live pricing for {model_name}: {e}")
            raise PricingAPIError(f"Failed to fetch pricing: {e}")

    def get_supported_providers(self) -> List[str]:
        """
        Get a list of providers that support live pricing.
        
        Returns:
            List of provider names
        """
        providers = []
        
        if BOTO3_AVAILABLE:
            providers.extend([
                'amazon (via AWS Pricing API)',
                'anthropic (via AWS Bedrock Pricing API)',
                'meta (via AWS Bedrock Pricing API)',
                'mistralai (via AWS Bedrock Pricing API)',
                'cohere (via AWS Bedrock Pricing API)',
                'ai21 (via AWS Bedrock Pricing API)',
            ])
        
        return providers

    def clear_cache(self, model_name: Optional[str] = None) -> None:
        """
        Clear cached pricing data.
        
        Args:
            model_name: Specific model to clear, or None to clear all cache
        """
        if model_name:
            if model_name in self._cache:
                del self._cache[model_name]
                logger.info(f"Cleared cache for {model_name}")
        else:
            self._cache.clear()
            logger.info("Cleared all pricing cache")


def calculate_cost_live(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    use_cache: bool = True
) -> Optional[float]:
    """
    Calculate the cost for model invocation using live pricing.

    Args:
        model_name: The model name (e.g., "amazon/nova-pro-v1:0")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        use_cache: Whether to use cached pricing if available

    Returns:
        Total cost in USD, or None if pricing not available

    Raises:
        PricingAPIError: If API call fails
    """
    client = LivePricingClient()
    pricing = client.get_live_pricing(model_name, use_cache=use_cache)
    if pricing is None:
        return None
    return pricing.calculate_cost(input_tokens, output_tokens)


def format_cost(cost: float) -> str:
    """
    Format a cost value for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        # For very small costs, show more decimal places
        return f"${cost:.6f}"
    elif cost < 1:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"
