"""
Unit tests for the model_pricing module.
"""

import pytest
from helm.benchmark.model_pricing import (
    ModelPricing,
    ModelPricingRegistry,
    calculate_cost,
    format_cost,
)


class TestModelPricing:
    """Test the ModelPricing class."""

    def test_price_per_token(self):
        """Test price per token calculation."""
        pricing = ModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0,
        )
        assert pricing.input_price_per_token == 1.0 / 1_000_000
        assert pricing.output_price_per_token == 2.0 / 1_000_000

    def test_calculate_cost(self):
        """Test cost calculation."""
        pricing = ModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0,
        )

        # Test with 1000 input tokens and 500 output tokens
        cost = pricing.calculate_cost(1000, 500)
        expected = (1000 * 1.0 / 1_000_000) + (500 * 2.0 / 1_000_000)
        assert abs(cost - expected) < 1e-10

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        pricing = ModelPricing(
            model_name="test/model",
            input_price_per_million=1.0,
            output_price_per_million=2.0,
        )
        assert pricing.calculate_cost(0, 0) == 0.0

    def test_calculate_cost_large_numbers(self):
        """Test cost calculation with large token counts."""
        pricing = ModelPricing(
            model_name="test/model",
            input_price_per_million=10.0,
            output_price_per_million=30.0,
        )

        # 1 million tokens each
        cost = pricing.calculate_cost(1_000_000, 1_000_000)
        expected = 10.0 + 30.0  # Should be exactly $40
        assert abs(cost - expected) < 1e-10


class TestModelPricingRegistry:
    """Test the ModelPricingRegistry class."""

    def test_load_pricing_data(self):
        """Test that pricing data loads successfully."""
        models = ModelPricingRegistry.list_all_models()
        assert len(models) > 0, "Should have at least one model"

    def test_get_pricing_nova_model(self):
        """Test getting pricing for a Nova model."""
        pricing = ModelPricingRegistry.get_pricing("amazon/nova-pro-v1:0")
        assert pricing is not None
        assert pricing.model_name == "amazon/nova-pro-v1:0"
        assert pricing.input_price_per_million > 0
        assert pricing.output_price_per_million > 0

    def test_get_pricing_nonexistent_model(self):
        """Test getting pricing for a model that doesn't exist."""
        pricing = ModelPricingRegistry.get_pricing("nonexistent/model")
        assert pricing is None

    def test_search_models(self):
        """Test model search functionality."""
        # Search for Nova models
        results = ModelPricingRegistry.search_models("nova")
        assert len(results) > 0
        assert all("nova" in model.lower() for model in results)

    def test_search_models_case_insensitive(self):
        """Test that model search is case-insensitive."""
        results_lower = ModelPricingRegistry.search_models("nova")
        results_upper = ModelPricingRegistry.search_models("NOVA")
        assert results_lower == results_upper

    def test_get_all_pricing(self):
        """Test getting all pricing information."""
        all_pricing = ModelPricingRegistry.get_all_pricing()
        assert len(all_pricing) > 0
        assert isinstance(all_pricing, dict)
        for model_name, pricing in all_pricing.items():
            assert isinstance(pricing, ModelPricing)
            assert pricing.model_name == model_name


class TestCalculateCost:
    """Test the calculate_cost convenience function."""

    def test_calculate_cost_success(self):
        """Test successful cost calculation."""
        cost = calculate_cost("amazon/nova-pro-v1:0", 1000, 500)
        assert cost is not None
        assert cost > 0

    def test_calculate_cost_nonexistent_model(self):
        """Test cost calculation for nonexistent model."""
        cost = calculate_cost("nonexistent/model", 1000, 500)
        assert cost is None


class TestFormatCost:
    """Test the format_cost function."""

    def test_format_small_cost(self):
        """Test formatting very small costs."""
        formatted = format_cost(0.000123)
        assert "$" in formatted
        assert "0.000123" in formatted

    def test_format_medium_cost(self):
        """Test formatting medium costs."""
        formatted = format_cost(0.1234)
        assert "$" in formatted
        assert "0.1234" in formatted

    def test_format_large_cost(self):
        """Test formatting large costs."""
        formatted = format_cost(123.456)
        assert "$" in formatted
        assert "123.46" in formatted

    def test_format_zero_cost(self):
        """Test formatting zero cost."""
        formatted = format_cost(0.0)
        assert "$" in formatted
        assert "0.00" in formatted


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_nova_pro_pricing(self):
        """Test Nova Pro pricing calculation."""
        pricing = ModelPricingRegistry.get_pricing("amazon/nova-pro-v1:0")
        assert pricing is not None

        # According to AWS, Nova Pro is $0.80 per 1M input tokens, $3.20 per 1M output tokens
        assert pricing.input_price_per_million == 0.80
        assert pricing.output_price_per_million == 3.20

        # Calculate cost for 10,000 input and 5,000 output tokens
        cost = pricing.calculate_cost(10_000, 5_000)
        expected = (10_000 * 0.80 / 1_000_000) + (5_000 * 3.20 / 1_000_000)
        assert abs(cost - expected) < 1e-10

    def test_nova_micro_pricing(self):
        """Test Nova Micro pricing calculation."""
        pricing = ModelPricingRegistry.get_pricing("amazon/nova-micro-v1:0")
        assert pricing is not None

        # Nova Micro should be cheaper than Nova Pro
        nova_pro = ModelPricingRegistry.get_pricing("amazon/nova-pro-v1:0")
        assert pricing.input_price_per_million < nova_pro.input_price_per_million
        assert pricing.output_price_per_million < nova_pro.output_price_per_million

    def test_compare_models(self):
        """Test comparing costs across different models."""
        input_tokens = 100_000
        output_tokens = 50_000

        models_to_compare = [
            "amazon/nova-micro-v1:0",
            "amazon/nova-lite-v1:0",
            "amazon/nova-pro-v1:0",
        ]

        costs = []
        for model in models_to_compare:
            cost = calculate_cost(model, input_tokens, output_tokens)
            assert cost is not None
            costs.append(cost)

        # Verify that costs increase with model capability
        # (micro < lite < pro)
        assert costs[0] < costs[1] < costs[2]

    def test_bedrock_vs_openai(self):
        """Test that we have pricing for both Bedrock and OpenAI models."""
        # Check Bedrock model
        bedrock_pricing = ModelPricingRegistry.get_pricing("amazon/nova-pro-v1:0")
        assert bedrock_pricing is not None

        # Check OpenAI model
        openai_pricing = ModelPricingRegistry.get_pricing("openai/gpt-4o")
        assert openai_pricing is not None

        # Both should have positive prices
        assert bedrock_pricing.input_price_per_million > 0
        assert openai_pricing.input_price_per_million > 0
