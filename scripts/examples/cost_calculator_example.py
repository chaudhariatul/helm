#!/usr/bin/env python3
"""
Example script demonstrating how to use the Model Cost Calculator.

This script shows various ways to use the model_pricing module for cost estimation.
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from helm.benchmark.model_pricing import (
    ModelPricingRegistry,
    calculate_cost,
    format_cost,
)


def example_1_basic_cost_calculation():
    """Example 1: Basic cost calculation for a single model."""
    print("=" * 70)
    print("Example 1: Basic Cost Calculation")
    print("=" * 70)

    model = "amazon/nova-pro-v1:0"
    input_tokens = 10000
    output_tokens = 5000

    cost = calculate_cost(model, input_tokens, output_tokens)
    print(f"\nModel: {model}")
    print(f"Input tokens: {input_tokens:,}")
    print(f"Output tokens: {output_tokens:,}")
    print(f"Total cost: {format_cost(cost)}\n")


def example_2_compare_models():
    """Example 2: Compare costs across multiple models."""
    print("=" * 70)
    print("Example 2: Compare Costs Across Models")
    print("=" * 70)

    input_tokens = 100_000
    output_tokens = 50_000

    models = [
        "amazon/nova-micro-v1:0",
        "amazon/nova-lite-v1:0",
        "amazon/nova-pro-v1:0",
        "openai/gpt-3.5-turbo",
        "openai/gpt-4o",
    ]

    print(f"\nCost comparison for {input_tokens:,} input + {output_tokens:,} output tokens:\n")

    results = []
    for model in models:
        cost = calculate_cost(model, input_tokens, output_tokens)
        if cost is not None:
            results.append((model, cost))

    # Sort by cost
    results.sort(key=lambda x: x[1])

    for model, cost in results:
        print(f"  {model:45s} {format_cost(cost):>12s}")
    print()


def example_3_detailed_pricing():
    """Example 3: Get detailed pricing information."""
    print("=" * 70)
    print("Example 3: Detailed Pricing Information")
    print("=" * 70)

    model_name = "amazon/nova-pro-v1:0"
    pricing = ModelPricingRegistry.get_pricing(model_name)

    if pricing:
        print(f"\nModel: {pricing.model_name}")
        print(f"Description: {pricing.notes}")
        print(f"\nPricing:")
        print(f"  Input:  ${pricing.input_price_per_million:.2f} per 1M tokens")
        print(f"  Output: ${pricing.output_price_per_million:.2f} per 1M tokens")
        print(f"\nPer-token rates:")
        print(f"  Input:  ${pricing.input_price_per_token:.8f} per token")
        print(f"  Output: ${pricing.output_price_per_token:.8f} per token")
        print()


def example_4_search_models():
    """Example 4: Search for models by keyword."""
    print("=" * 70)
    print("Example 4: Search Models")
    print("=" * 70)

    keywords = ["nova", "gpt", "claude"]

    for keyword in keywords:
        models = ModelPricingRegistry.search_models(keyword)
        print(f"\nModels matching '{keyword}': {len(models)} found")
        for model in models[:3]:  # Show first 3
            pricing = ModelPricingRegistry.get_pricing(model)
            if pricing:
                print(f"  • {model}")
                print(f"    Input: ${pricing.input_price_per_million:.2f}/1M, "
                      f"Output: ${pricing.output_price_per_million:.2f}/1M")


def example_5_monthly_budget():
    """Example 5: Estimate monthly budget."""
    print("=" * 70)
    print("Example 5: Monthly Budget Estimation")
    print("=" * 70)

    model = "amazon/nova-pro-v1:0"
    daily_input_tokens = 1_000_000
    daily_output_tokens = 500_000
    days_per_month = 30

    daily_cost = calculate_cost(model, daily_input_tokens, daily_output_tokens)
    monthly_cost = daily_cost * days_per_month

    print(f"\nModel: {model}")
    print(f"Daily usage: {daily_input_tokens:,} input + {daily_output_tokens:,} output tokens")
    print(f"Daily cost: {format_cost(daily_cost)}")
    print(f"Monthly cost (30 days): {format_cost(monthly_cost)}")
    print()


def example_6_cost_breakdown():
    """Example 6: Detailed cost breakdown."""
    print("=" * 70)
    print("Example 6: Detailed Cost Breakdown")
    print("=" * 70)

    model_name = "amazon/nova-pro-v1:0"
    input_tokens = 50_000
    output_tokens = 25_000

    pricing = ModelPricingRegistry.get_pricing(model_name)

    if pricing:
        input_cost = input_tokens * pricing.input_price_per_token
        output_cost = output_tokens * pricing.output_price_per_token
        total_cost = input_cost + output_cost

        print(f"\nModel: {model_name}")
        print(f"\nToken counts:")
        print(f"  Input:  {input_tokens:,} tokens")
        print(f"  Output: {output_tokens:,} tokens")
        print(f"  Total:  {input_tokens + output_tokens:,} tokens")
        print(f"\nCost breakdown:")
        print(f"  Input:  {input_tokens:,} × ${pricing.input_price_per_token:.8f} = {format_cost(input_cost)}")
        print(f"  Output: {output_tokens:,} × ${pricing.output_price_per_token:.8f} = {format_cost(output_cost)}")
        print(f"  " + "─" * 60)
        print(f"  Total: {format_cost(total_cost)}")
        print()


def example_7_find_cheapest_model():
    """Example 7: Find the cheapest model for a given workload."""
    print("=" * 70)
    print("Example 7: Find Cheapest Model")
    print("=" * 70)

    input_tokens = 100_000
    output_tokens = 50_000

    all_models = ModelPricingRegistry.list_all_models()
    costs = []

    for model in all_models:
        cost = calculate_cost(model, input_tokens, output_tokens)
        if cost is not None:
            costs.append((model, cost))

    # Sort by cost
    costs.sort(key=lambda x: x[1])

    print(f"\nTop 5 cheapest models for {input_tokens:,} input + {output_tokens:,} output tokens:\n")
    for i, (model, cost) in enumerate(costs[:5], 1):
        pricing = ModelPricingRegistry.get_pricing(model)
        print(f"{i}. {model}")
        print(f"   Cost: {format_cost(cost)}")
        if pricing and pricing.notes:
            print(f"   {pricing.notes}")
        print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Model Cost Calculator - Usage Examples")
    print("=" * 70)
    print()

    examples = [
        example_1_basic_cost_calculation,
        example_2_compare_models,
        example_3_detailed_pricing,
        example_4_search_models,
        example_5_monthly_budget,
        example_6_cost_breakdown,
        example_7_find_cheapest_model,
    ]

    for example in examples:
        example()
        input("Press Enter to continue to next example...")
        print("\n")

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
