"""
Unit tests for the model_pricing_api module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from helm.benchmark.model_pricing_api import (
    LiveModelPricing,
    LivePricingClient,
    PricingAPIError,
    calculate_cost_live,
    format_cost,
)


class TestLiveModelPricing(unittest.TestCase):
    """Test the LiveModelPricing dataclass."""

    def test_create_pricing(self):
        """Test creating a LiveModelPricing object."""
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0,
            notes="Test model",
            source="test_api"
        )
        
        self.assertEqual(pricing.model_name, "test/model")
        self.assertEqual(pricing.input_price_per_million, 1.0)
        self.assertEqual(pricing.output_price_per_million, 2.0)
        self.assertEqual(pricing.notes, "Test model")
        self.assertEqual(pricing.source, "test_api")

    def test_price_per_token(self):
        """Test per-token price calculation."""
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        
        self.assertEqual(pricing.input_price_per_token, 1.0 / 1_000_000)
        self.assertEqual(pricing.output_price_per_token, 2.0 / 1_000_000)

    def test_calculate_cost(self):
        """Test cost calculation."""
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        
        # 1000 input tokens + 500 output tokens
        cost = pricing.calculate_cost(1000, 500)
        expected = (1000 * 1.0 / 1_000_000) + (500 * 2.0 / 1_000_000)
        self.assertAlmostEqual(cost, expected)

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        
        cost = pricing.calculate_cost(0, 0)
        self.assertEqual(cost, 0.0)


class TestLivePricingClient(unittest.TestCase):
    """Test the LivePricingClient class."""

    def test_init(self):
        """Test client initialization."""
        client = LivePricingClient()
        self.assertIsNotNone(client)
        self.assertEqual(len(client._cache), 0)

    def test_cache_behavior(self):
        """Test caching functionality."""
        client = LivePricingClient(cache_ttl_minutes=1)
        
        # Initially cache should be empty
        self.assertFalse(client._is_cache_valid("test/model"))
        
        # Add to cache
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        client._add_to_cache("test/model", pricing)
        
        # Should be valid now
        self.assertTrue(client._is_cache_valid("test/model"))
        
        # Should retrieve from cache
        cached = client._get_from_cache("test/model")
        self.assertIsNotNone(cached)
        self.assertEqual(cached.model_name, "test/model")

    def test_cache_expiration(self):
        """Test cache expiration."""
        client = LivePricingClient(cache_ttl_minutes=1)
        
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        
        # Add to cache with old timestamp
        old_time = datetime.now() - timedelta(minutes=2)
        client._cache["test/model"] = (pricing, old_time)
        
        # Should be expired
        self.assertFalse(client._is_cache_valid("test/model"))
        cached = client._get_from_cache("test/model")
        self.assertIsNone(cached)

    def test_clear_cache(self):
        """Test cache clearing."""
        client = LivePricingClient()
        
        pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        client._add_to_cache("test/model", pricing)
        
        # Clear specific model
        client.clear_cache("test/model")
        self.assertFalse(client._is_cache_valid("test/model"))
        
        # Add again
        client._add_to_cache("test/model", pricing)
        client._add_to_cache("other/model", pricing)
        
        # Clear all
        client.clear_cache()
        self.assertEqual(len(client._cache), 0)

    def test_parse_bedrock_model_id(self):
        """Test parsing Bedrock model IDs."""
        client = LivePricingClient()
        
        # Valid Bedrock models
        result = client._parse_bedrock_model_id("amazon/nova-pro-v1:0")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "amazon")
        
        result = client._parse_bedrock_model_id("anthropic/claude-3-opus")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "anthropic")
        
        # Non-Bedrock model
        result = client._parse_bedrock_model_id("openai/gpt-4")
        self.assertIsNone(result)
        
        # Invalid format
        result = client._parse_bedrock_model_id("invalid-model")
        self.assertIsNone(result)

    @patch('helm.benchmark.model_pricing_api.BOTO3_AVAILABLE', False)
    def test_get_live_pricing_no_boto3(self):
        """Test behavior when boto3 is not available."""
        client = LivePricingClient()
        
        with self.assertRaises(PricingAPIError):
            client._fetch_bedrock_pricing("amazon/nova-pro-v1:0")

    @patch('helm.benchmark.model_pricing_api.BOTO3_AVAILABLE', True)
    @patch('helm.benchmark.model_pricing_api.boto3')
    def test_get_live_pricing_with_cache(self, mock_boto3):
        """Test getting live pricing with cache."""
        client = LivePricingClient()
        
        # Add to cache
        pricing = LiveModelPricing(
            model_name="amazon/nova-pro-v1:0",
            input_price_per_million=0.8,
            output_price_per_million=3.2,
            source="test_cache"
        )
        client._add_to_cache("amazon/nova-pro-v1:0", pricing)
        
        # Should return cached pricing without calling API
        result = client.get_live_pricing("amazon/nova-pro-v1:0")
        self.assertIsNotNone(result)
        self.assertEqual(result.source, "test_cache")
        mock_boto3.client.assert_not_called()

    @patch('helm.benchmark.model_pricing_api.BOTO3_AVAILABLE', True)
    @patch('helm.benchmark.model_pricing_api.boto3')
    def test_fetch_bedrock_pricing_api_error(self, mock_boto3):
        """Test handling of AWS API errors."""
        from botocore.exceptions import ClientError
        
        # Mock boto3 client to raise ClientError
        mock_pricing_client = Mock()
        mock_pricing_client.get_products.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'GetProducts'
        )
        mock_boto3.client.return_value = mock_pricing_client
        
        client = LivePricingClient()
        
        with self.assertRaises(PricingAPIError) as context:
            client._fetch_bedrock_pricing("amazon/nova-pro-v1:0")
        
        self.assertIn("AccessDenied", str(context.exception))

    def test_get_supported_providers(self):
        """Test getting supported providers."""
        client = LivePricingClient()
        providers = client.get_supported_providers()
        self.assertIsInstance(providers, list)
        
        # Should include AWS providers if boto3 is available
        try:
            import boto3
            self.assertGreater(len(providers), 0)
        except ImportError:
            self.assertEqual(len(providers), 0)


class TestCalculateCostLive(unittest.TestCase):
    """Test the calculate_cost_live function."""

    @patch('helm.benchmark.model_pricing_api.LivePricingClient')
    def test_calculate_cost_live_success(self, mock_client_class):
        """Test successful cost calculation."""
        # Mock the pricing
        mock_pricing = LiveModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0
        )
        
        mock_client = Mock()
        mock_client.get_live_pricing.return_value = mock_pricing
        mock_client_class.return_value = mock_client
        
        cost = calculate_cost_live("test/model", 1000, 500)
        
        expected = (1000 * 1.0 / 1_000_000) + (500 * 2.0 / 1_000_000)
        self.assertAlmostEqual(cost, expected)

    @patch('helm.benchmark.model_pricing_api.LivePricingClient')
    def test_calculate_cost_live_no_pricing(self, mock_client_class):
        """Test when pricing is not available."""
        mock_client = Mock()
        mock_client.get_live_pricing.return_value = None
        mock_client_class.return_value = mock_client
        
        cost = calculate_cost_live("test/model", 1000, 500)
        self.assertIsNone(cost)


class TestFormatCost(unittest.TestCase):
    """Test the format_cost function."""

    def test_format_very_small_cost(self):
        """Test formatting very small costs."""
        result = format_cost(0.000001)
        self.assertEqual(result, "$0.000001")

    def test_format_small_cost(self):
        """Test formatting small costs."""
        result = format_cost(0.0123)
        self.assertEqual(result, "$0.0123")

    def test_format_medium_cost(self):
        """Test formatting medium costs."""
        result = format_cost(0.5678)
        self.assertEqual(result, "$0.5678")

    def test_format_large_cost(self):
        """Test formatting large costs."""
        result = format_cost(123.456)
        self.assertEqual(result, "$123.46")

    def test_format_zero_cost(self):
        """Test formatting zero cost."""
        result = format_cost(0.0)
        self.assertEqual(result, "$0.000000")


if __name__ == "__main__":
    unittest.main()
