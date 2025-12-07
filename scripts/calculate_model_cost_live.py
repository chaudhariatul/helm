#!/usr/bin/env python3
"""
Model Cost Calculator with Live Pricing API

This script calculates the estimated cost for model invocation using live pricing
fetched from AWS Bedrock Pricing API and other pricing sources. It provides an
alternative to the static JSON-based pricing calculator.

Features:
- Fetches current pricing from AWS Pricing API for Bedrock models
- Caches pricing data to reduce API calls
- Falls back to static pricing if live pricing is unavailable
- Supports all Bedrock models and others with live pricing APIs
- Handles API failures gracefully with informative error messages

Usage:
    # Calculate cost using live pricing
    python scripts/calculate_model_cost_live.py --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500

    # Force refresh pricing (bypass cache)
    python scripts/calculate_model_cost_live.py --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500 --no-cache

    # Show supported providers
    python scripts/calculate_model_cost_live.py --show-providers

    # Compare with static pricing
    python scripts/calculate_model_cost_live.py --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500 --compare
"""

import argparse
import os
import sys
from typing import Optional

# Add the src directory to the path so we can import helm modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from helm.benchmark.model_pricing_api import (
    LivePricingClient,
    PricingAPIError,
    LiveModelPricing,
    format_cost,
)

# Import static pricing for fallback and comparison
from helm.benchmark.model_pricing import (
    ModelPricingRegistry,
    calculate_cost as calculate_cost_static,
)


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"ERROR: {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"WARNING: {message}")


def print_pricing_details(pricing: LiveModelPricing) -> None:
    """Print detailed pricing information."""
    print("\n" + "=" * 70)
    print(f"Model: {pricing.model_name}")
    if pricing.notes:
        print(f"Description: {pricing.notes}")
    print(f"Source: {pricing.source}")
    if pricing.fetched_at:
        print(f"Fetched at: {pricing.fetched_at}")
    print("=" * 70)
    print(f"\nPricing (USD):")
    print(f"  Input:  ${pricing.input_price_per_million:.6f} per 1M tokens")
    print(f"  Output: ${pricing.output_price_per_million:.6f} per 1M tokens")
    print(f"\nPer-token rates:")
    print(f"  Input:  ${pricing.input_price_per_token:.10f} per token")
    print(f"  Output: ${pricing.output_price_per_token:.10f} per token")


def print_cost_breakdown(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    pricing: LiveModelPricing,
    total_cost: float
) -> None:
    """Print a detailed cost breakdown."""
    input_cost = input_tokens * pricing.input_price_per_token
    output_cost = output_tokens * pricing.output_price_per_token

    print("\n" + "=" * 70)
    print(f"Model: {model_name}")
    if pricing.notes:
        print(f"Description: {pricing.notes}")
    print(f"Pricing Source: {pricing.source}")
    if pricing.fetched_at:
        print(f"Fetched at: {pricing.fetched_at}")
    print("=" * 70)
    print(f"\nToken Usage:")
    print(f"  Input tokens:  {input_tokens:,}")
    print(f"  Output tokens: {output_tokens:,}")
    print(f"  Total tokens:  {input_tokens + output_tokens:,}")
    print(f"\nPricing Rates:")
    print(f"  Input:  ${pricing.input_price_per_million:.6f} per 1M tokens")
    print(f"  Output: ${pricing.output_price_per_million:.6f} per 1M tokens")
    print(f"\nCost Breakdown:")
    print(f"  Input cost:  {format_cost(input_cost)}")
    print(f"  Output cost: {format_cost(output_cost)}")
    print(f"  {'─' * 40}")
    print(f"  Total cost:  {format_cost(total_cost)}")
    print("=" * 70 + "\n")


def compare_pricing(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    live_pricing: Optional[LiveModelPricing],
    live_cost: Optional[float]
) -> None:
    """Compare live pricing with static pricing."""
    print("\n" + "=" * 70)
    print("PRICING COMPARISON: Live API vs Static Data")
    print("=" * 70)
    
    # Get static pricing
    static_pricing = ModelPricingRegistry.get_pricing(model_name)
    static_cost = None
    if static_pricing:
        static_cost = static_pricing.calculate_cost(input_tokens, output_tokens)
    
    print(f"\nModel: {model_name}")
    print(f"Input tokens: {input_tokens:,}")
    print(f"Output tokens: {output_tokens:,}")
    print("\n" + "-" * 70)
    
    # Live pricing
    print("\nLIVE PRICING (from API):")
    if live_pricing:
        print(f"  Input rate:  ${live_pricing.input_price_per_million:.6f} per 1M tokens")
        print(f"  Output rate: ${live_pricing.output_price_per_million:.6f} per 1M tokens")
        print(f"  Total cost:  {format_cost(live_cost) if live_cost else 'N/A'}")
        print(f"  Source:      {live_pricing.source}")
    else:
        print("  NOT AVAILABLE")
    
    print("\n" + "-" * 70)
    
    # Static pricing
    print("\nSTATIC PRICING (from JSON file):")
    if static_pricing:
        print(f"  Input rate:  ${static_pricing.input_price_per_million:.6f} per 1M tokens")
        print(f"  Output rate: ${static_pricing.output_price_per_million:.6f} per 1M tokens")
        print(f"  Total cost:  {format_cost(static_cost) if static_cost else 'N/A'}")
        print(f"  Source:      static JSON")
    else:
        print("  NOT AVAILABLE")
    
    # Show difference
    if live_cost is not None and static_cost is not None:
        difference = live_cost - static_cost
        percent_diff = (difference / static_cost * 100) if static_cost > 0 else 0
        
        print("\n" + "-" * 70)
        print("\nDIFFERENCE:")
        print(f"  Absolute: {format_cost(abs(difference))} {'(live is higher)' if difference > 0 else '(static is higher)' if difference < 0 else '(same)'}")
        print(f"  Relative: {abs(percent_diff):.2f}% {'(live is higher)' if difference > 0 else '(static is higher)' if difference < 0 else '(same)'}")
        
        if abs(percent_diff) > 10:
            print(f"\n  ⚠️  WARNING: Pricing differs by more than 10%!")
            print(f"      Consider updating the static pricing data.")
    
    print("=" * 70 + "\n")


def show_supported_providers(client: LivePricingClient) -> None:
    """Show supported pricing providers."""
    providers = client.get_supported_providers()
    
    print("\n" + "=" * 70)
    print("SUPPORTED PROVIDERS FOR LIVE PRICING")
    print("=" * 70)
    
    if not providers:
        print("\nNo providers available for live pricing.")
        print("Make sure boto3 is installed for AWS Pricing API support.")
    else:
        print("\nThe following providers support live pricing fetching:\n")
        for provider in providers:
            print(f"  • {provider}")
    
    print("\n" + "=" * 70)
    print("\nNOTE: For providers without live pricing APIs, the tool will")
    print("return informative errors and can fallback to static pricing.")
    print("=" * 70 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate model invocation costs using live pricing APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate cost using live pricing
  %(prog)s --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500

  # Show detailed breakdown
  %(prog)s --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500 --verbose

  # Force refresh pricing (bypass cache)
  %(prog)s --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500 --no-cache

  # Compare with static pricing
  %(prog)s --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500 --compare

  # Show supported providers
  %(prog)s --show-providers

  # Use static pricing as fallback on API failure
  %(prog)s --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500 --fallback

Note:
  - Live pricing requires boto3 and AWS credentials configured
  - Pricing data is cached for 60 minutes by default
  - Use --no-cache to force fresh pricing fetch
        """,
    )

    parser.add_argument(
        "--model", "-m", type=str, help="Model name (e.g., amazon/nova-pro-v1:0)"
    )

    parser.add_argument(
        "--input-tokens", "-i", type=int, help="Number of input tokens"
    )

    parser.add_argument(
        "--output-tokens", "-o", type=int, help="Number of output tokens"
    )

    parser.add_argument(
        "--no-cache", action="store_true", help="Bypass cache and fetch fresh pricing"
    )

    parser.add_argument(
        "--cache-ttl", type=int, default=60, help="Cache time-to-live in minutes (default: 60)"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed cost breakdown"
    )

    parser.add_argument(
        "--compare", "-c", action="store_true", help="Compare live pricing with static pricing"
    )

    parser.add_argument(
        "--fallback", "-f", action="store_true", 
        help="Use static pricing as fallback if live pricing fails"
    )

    parser.add_argument(
        "--show-providers", action="store_true", help="Show supported pricing providers"
    )

    parser.add_argument(
        "--show-pricing", "-p", action="store_true", help="Show detailed pricing for the specified model"
    )

    args = parser.parse_args()

    # Initialize client
    try:
        client = LivePricingClient(cache_ttl_minutes=args.cache_ttl)
    except Exception as e:
        print_error(f"Failed to initialize pricing client: {e}")
        return 1

    # Show supported providers
    if args.show_providers:
        show_supported_providers(client)
        return 0

    # Validate required arguments for cost calculation
    if not args.show_providers and not args.show_pricing:
        if not args.model:
            print_error("--model is required")
            parser.print_help()
            return 1

    # Show pricing for a model
    if args.show_pricing:
        if not args.model:
            print_error("--model is required with --show-pricing")
            return 1

        try:
            pricing = client.get_live_pricing(args.model, use_cache=not args.no_cache)
            
            if pricing is None:
                print_warning(f"Live pricing not available for '{args.model}'")
                
                if args.fallback:
                    print("\nAttempting to use static pricing as fallback...")
                    static_pricing = ModelPricingRegistry.get_pricing(args.model)
                    if static_pricing:
                        print("\n✓ Found static pricing data")
                        print(f"\nInput:  ${static_pricing.input_price_per_million:.6f} per 1M tokens")
                        print(f"Output: ${static_pricing.output_price_per_million:.6f} per 1M tokens")
                        print(f"Source: static JSON file")
                        return 0
                    else:
                        print_error(f"No static pricing available for '{args.model}' either")
                        return 1
                else:
                    print("\nTry using --fallback to use static pricing instead")
                    return 1
            
            print_pricing_details(pricing)
            
            # Show example costs
            print(f"\nExample costs:")
            for input_tok, output_tok in [(1000, 1000), (10000, 5000), (100000, 50000)]:
                cost = pricing.calculate_cost(input_tok, output_tok)
                print(f"  {input_tok:>6,} input + {output_tok:>6,} output = {format_cost(cost)}")
            print()
            
            return 0
            
        except PricingAPIError as e:
            print_error(f"Failed to fetch pricing: {e}")
            if args.fallback:
                print("\nAttempting to use static pricing as fallback...")
                static_pricing = ModelPricingRegistry.get_pricing(args.model)
                if static_pricing:
                    print("✓ Using static pricing data")
                    print(f"\nInput:  ${static_pricing.input_price_per_million:.6f} per 1M tokens")
                    print(f"Output: ${static_pricing.output_price_per_million:.6f} per 1M tokens")
                    return 0
            return 1

    # Calculate cost
    if args.model and args.input_tokens is not None and args.output_tokens is not None:
        if args.input_tokens < 0 or args.output_tokens < 0:
            print_error("Token counts must be non-negative")
            return 1

        try:
            # Fetch live pricing
            pricing = client.get_live_pricing(args.model, use_cache=not args.no_cache)
            cost = None
            
            if pricing is None:
                print_warning(f"Live pricing not available for '{args.model}'")
                
                if args.fallback:
                    print("\nAttempting to use static pricing as fallback...")
                    cost = calculate_cost_static(args.model, args.input_tokens, args.output_tokens)
                    if cost is not None:
                        print(f"✓ Using static pricing data\n")
                        if args.verbose:
                            static_pricing = ModelPricingRegistry.get_pricing(args.model)
                            if static_pricing:
                                # Create a LiveModelPricing from static for consistent display
                                from helm.benchmark.model_pricing_api import LiveModelPricing
                                pricing = LiveModelPricing(
                                    model_name=static_pricing.model_name,
                                    input_price_per_million=static_pricing.input_price_per_million,
                                    output_price_per_million=static_pricing.output_price_per_million,
                                    notes=static_pricing.notes,
                                    source="static_json_fallback"
                                )
                                print_cost_breakdown(args.model, args.input_tokens, args.output_tokens, pricing, cost)
                        else:
                            print(f"Cost: {format_cost(cost)} (using static pricing)")
                        return 0
                    else:
                        print_error(f"No static pricing available for '{args.model}' either")
                        return 1
                else:
                    print("\nReasons live pricing may be unavailable:")
                    print("  • Model provider doesn't offer a public pricing API")
                    print("  • AWS credentials not configured (for Bedrock models)")
                    print("  • Network connectivity issues")
                    print("\nTry using --fallback to use static pricing instead")
                    return 1
            else:
                cost = pricing.calculate_cost(args.input_tokens, args.output_tokens)

            # Display results
            if args.compare:
                compare_pricing(args.model, args.input_tokens, args.output_tokens, pricing, cost)
            elif args.verbose:
                print_cost_breakdown(args.model, args.input_tokens, args.output_tokens, pricing, cost)
            else:
                print(f"Cost: {format_cost(cost)}")
                if pricing.source:
                    print(f"(using {pricing.source})")

            return 0

        except PricingAPIError as e:
            print_error(f"Pricing API error: {e}")
            print("\nDetails:")
            print(f"  • API call failed while fetching pricing for '{args.model}'")
            print(f"  • Error: {e}")
            
            if args.fallback:
                print("\nAttempting to use static pricing as fallback...")
                cost = calculate_cost_static(args.model, args.input_tokens, args.output_tokens)
                if cost is not None:
                    print(f"✓ Using static pricing data")
                    print(f"\nCost: {format_cost(cost)} (using static pricing)")
                    return 0
                else:
                    print_error(f"No static pricing available for '{args.model}' either")
            else:
                print("\nTry using --fallback to use static pricing on API failures")
            
            return 1
            
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return 1

    # No valid action specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
