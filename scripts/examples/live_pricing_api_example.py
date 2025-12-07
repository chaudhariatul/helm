#!/usr/bin/env python3
"""
Example script demonstrating the Live Pricing API usage.

This script shows various ways to use the Live Pricing API for
calculating model invocation costs with current pricing data.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from helm.benchmark.model_pricing_api import (
    LivePricingClient,
    PricingAPIError,
    calculate_cost_live,
    format_cost,
)

# Also import static pricing for fallback
from helm.benchmark.model_pricing import calculate_cost as calculate_cost_static


def example_1_basic_usage():
    """Example 1: Basic usage - fetch pricing and calculate cost."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)
    
    client = LivePricingClient()
    model_name = "amazon/nova-pro-v1:0"
    
    try:
        # Fetch live pricing
        pricing = client.get_live_pricing(model_name)
        
        if pricing:
            print(f"\n✓ Successfully fetched pricing for {model_name}")
            print(f"  Input:  ${pricing.input_price_per_million:.2f} per 1M tokens")
            print(f"  Output: ${pricing.output_price_per_million:.2f} per 1M tokens")
            print(f"  Source: {pricing.source}")
            
            # Calculate cost
            cost = pricing.calculate_cost(10000, 5000)
            print(f"\nCost for 10,000 input + 5,000 output tokens: {format_cost(cost)}")
        else:
            print(f"\n✗ Live pricing not available for {model_name}")
            
    except PricingAPIError as e:
        print(f"\n✗ API Error: {e}")


def example_2_with_fallback():
    """Example 2: Using fallback to static pricing."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Fallback to Static Pricing")
    print("=" * 70)
    
    client = LivePricingClient()
    model_name = "amazon/nova-lite-v1:0"
    input_tokens = 50000
    output_tokens = 25000
    
    try:
        # Try live pricing first
        pricing = client.get_live_pricing(model_name)
        
        if pricing:
            cost = pricing.calculate_cost(input_tokens, output_tokens)
            print(f"\n✓ Using live pricing")
            print(f"  Cost: {format_cost(cost)} (from {pricing.source})")
        else:
            # Fallback to static pricing
            print(f"\n⚠ Live pricing not available, falling back to static pricing")
            cost = calculate_cost_static(model_name, input_tokens, output_tokens)
            if cost:
                print(f"  Cost: {format_cost(cost)} (from static data)")
            else:
                print(f"  ✗ No pricing available")
                
    except PricingAPIError as e:
        print(f"\n⚠ API Error: {e}")
        print(f"  Falling back to static pricing...")
        cost = calculate_cost_static(model_name, input_tokens, output_tokens)
        if cost:
            print(f"  Cost: {format_cost(cost)} (from static data)")


def example_3_multiple_models():
    """Example 3: Compare costs across multiple models."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Compare Costs Across Multiple Models")
    print("=" * 70)
    
    client = LivePricingClient()
    models = [
        "amazon/nova-micro-v1:0",
        "amazon/nova-lite-v1:0",
        "amazon/nova-pro-v1:0",
        "amazon/nova-premier-v1:0",
    ]
    
    input_tokens = 100000
    output_tokens = 50000
    
    print(f"\nCost comparison for {input_tokens:,} input + {output_tokens:,} output tokens:\n")
    print(f"{'Model':<30} {'Cost':>15} {'Source':<20}")
    print("-" * 70)
    
    for model in models:
        try:
            pricing = client.get_live_pricing(model)
            if pricing:
                cost = pricing.calculate_cost(input_tokens, output_tokens)
                source = pricing.source
            else:
                # Try static pricing
                cost = calculate_cost_static(model, input_tokens, output_tokens)
                source = "static_fallback"
            
            if cost:
                print(f"{model:<30} {format_cost(cost):>15} {source:<20}")
            else:
                print(f"{model:<30} {'N/A':>15} {'unavailable':<20}")
                
        except PricingAPIError:
            # Try static pricing on error
            cost = calculate_cost_static(model, input_tokens, output_tokens)
            if cost:
                print(f"{model:<30} {format_cost(cost):>15} {'static_fallback':<20}")
            else:
                print(f"{model:<30} {'ERROR':>15} {'error':<20}")


def example_4_cache_management():
    """Example 4: Cache management."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Cache Management")
    print("=" * 70)
    
    # Create client with custom cache TTL
    client = LivePricingClient(cache_ttl_minutes=30)
    model_name = "amazon/nova-pro-v1:0"
    
    print(f"\n1. First call - fetches from API:")
    try:
        pricing = client.get_live_pricing(model_name, use_cache=False)
        if pricing:
            print(f"   ✓ Fetched pricing (source: {pricing.source})")
        else:
            print(f"   ⚠ Pricing not available")
    except PricingAPIError as e:
        print(f"   ✗ Error: {e}")
    
    print(f"\n2. Second call - uses cache:")
    try:
        pricing = client.get_live_pricing(model_name, use_cache=True)
        if pricing:
            print(f"   ✓ Retrieved pricing (likely from cache)")
        else:
            print(f"   ⚠ Pricing not available")
    except PricingAPIError as e:
        print(f"   ✗ Error: {e}")
    
    print(f"\n3. Clear cache for specific model:")
    client.clear_cache(model_name)
    print(f"   ✓ Cache cleared for {model_name}")
    
    print(f"\n4. Clear all cache:")
    client.clear_cache()
    print(f"   ✓ All cache cleared")


def example_5_error_handling():
    """Example 5: Robust error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Robust Error Handling")
    print("=" * 70)
    
    client = LivePricingClient()
    models = [
        "amazon/nova-pro-v1:0",     # Bedrock model
        "openai/gpt-4o",             # OpenAI (no public API)
        "anthropic/claude-3-opus",   # Anthropic direct (no public API)
        "invalid/model-name",        # Invalid model
    ]
    
    for model in models:
        print(f"\nTrying model: {model}")
        try:
            pricing = client.get_live_pricing(model)
            
            if pricing:
                cost = pricing.calculate_cost(10000, 5000)
                print(f"  ✓ Live pricing available: {format_cost(cost)}")
            else:
                print(f"  ⚠ Live pricing not available")
                # Try static fallback
                cost = calculate_cost_static(model, 10000, 5000)
                if cost:
                    print(f"  ✓ Static pricing available: {format_cost(cost)}")
                else:
                    print(f"  ✗ No pricing data available")
                    
        except PricingAPIError as e:
            print(f"  ✗ API Error: {str(e)[:80]}...")
            # Try static fallback
            cost = calculate_cost_static(model, 10000, 5000)
            if cost:
                print(f"  ✓ Static fallback: {format_cost(cost)}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {str(e)[:80]}...")


def example_6_convenience_function():
    """Example 6: Using the convenience function."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Using Convenience Function")
    print("=" * 70)
    
    model_name = "amazon/nova-lite-v1:0"
    input_tokens = 25000
    output_tokens = 10000
    
    print(f"\nCalculating cost for {model_name}:")
    print(f"  Input tokens: {input_tokens:,}")
    print(f"  Output tokens: {output_tokens:,}")
    
    try:
        # Simple one-liner
        cost = calculate_cost_live(model_name, input_tokens, output_tokens)
        
        if cost:
            print(f"\n✓ Cost: {format_cost(cost)}")
        else:
            print(f"\n⚠ Live pricing not available")
            # Try static
            cost = calculate_cost_static(model_name, input_tokens, output_tokens)
            if cost:
                print(f"✓ Cost (static): {format_cost(cost)}")
                
    except PricingAPIError as e:
        print(f"\n✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("LIVE PRICING API - USAGE EXAMPLES")
    print("=" * 70)
    print("\nNote: Some examples may show errors if AWS credentials are not")
    print("configured. This is expected and demonstrates the fallback behavior.")
    
    # Run examples
    example_1_basic_usage()
    example_2_with_fallback()
    example_3_multiple_models()
    example_4_cache_management()
    example_5_error_handling()
    example_6_convenience_function()
    
    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nFor more information, see:")
    print("  - scripts/LIVE_PRICING_API_README.md")
    print("  - Run: python scripts/calculate_model_cost_live.py --help")
    print()


if __name__ == "__main__":
    main()
