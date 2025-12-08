"""
Model Pricing Module

This module provides functionality to calculate costs for model invocations based on
input and output token counts. It supports all models available in the system, including
Bedrock models.

Usage:
    from helm.benchmark.model_pricing import ModelPricingRegistry, calculate_cost

    # Get pricing for a specific model
    pricing = ModelPricingRegistry.get_pricing("amazon/nova-pro-v1:0")
    
    # Calculate cost
    cost = calculate_cost("amazon/nova-pro-v1:0", input_tokens=1000, output_tokens=500)
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class ModelPricing:
    """Represents pricing information for a model."""

    model_name: str
    input_price_per_million: float
    output_price_per_million: float
    notes: Optional[str] = None

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


class ModelPricingRegistry:
    """Registry for model pricing information."""

    _pricing_data: Dict[str, ModelPricing] = {}
    _loaded: bool = False

    @classmethod
    def _load_pricing_data(cls) -> None:
        """Load pricing data from the JSON file."""
        if cls._loaded:
            return

        # Get the path to the pricing JSON file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pricing_file = os.path.join(current_dir, "model_pricing.json")

        if not os.path.exists(pricing_file):
            raise FileNotFoundError(f"Model pricing file not found at: {pricing_file}")

        with open(pricing_file, "r") as f:
            data = json.load(f)

        for model_data in data.get("models", []):
            pricing = ModelPricing(
                model_name=model_data["model_name"],
                input_price_per_million=model_data["input_price_per_million"],
                output_price_per_million=model_data["output_price_per_million"],
                notes=model_data.get("notes"),
            )
            cls._pricing_data[pricing.model_name] = pricing

        cls._loaded = True

    @classmethod
    def get_pricing(cls, model_name: str) -> Optional[ModelPricing]:
        """
        Get pricing information for a specific model.

        Args:
            model_name: The model name (e.g., "amazon/nova-pro-v1:0")

        Returns:
            ModelPricing object if found, None otherwise
        """
        cls._load_pricing_data()
        return cls._pricing_data.get(model_name)

    @classmethod
    def list_all_models(cls) -> List[str]:
        """
        List all models with pricing information.

        Returns:
            List of model names
        """
        cls._load_pricing_data()
        return sorted(cls._pricing_data.keys())

    @classmethod
    def get_all_pricing(cls) -> Dict[str, ModelPricing]:
        """
        Get all pricing information.

        Returns:
            Dictionary mapping model names to ModelPricing objects
        """
        cls._load_pricing_data()
        return cls._pricing_data.copy()

    @classmethod
    def search_models(cls, search_term: str) -> List[str]:
        """
        Search for models by name.

        Args:
            search_term: Search term to match against model names (case-insensitive)

        Returns:
            List of matching model names
        """
        cls._load_pricing_data()
        search_lower = search_term.lower()
        return sorted([name for name in cls._pricing_data.keys() if search_lower in name.lower()])


def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """
    Calculate the cost for model invocation.

    Args:
        model_name: The model name (e.g., "amazon/nova-pro-v1:0")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Total cost in USD, or None if model pricing not found
    """
    pricing = ModelPricingRegistry.get_pricing(model_name)
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
