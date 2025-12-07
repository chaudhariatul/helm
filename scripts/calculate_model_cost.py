#!/usr/bin/env python3
"""
Model Cost Calculator CLI Tool

This script calculates the estimated cost for model invocation based on input and output token counts.
It supports all models available in the system, including Bedrock models.

Usage:
    # Calculate cost for a specific invocation
    python scripts/calculate_model_cost.py --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500

    # List all available models
    python scripts/calculate_model_cost.py --list-models

    # Search for models
    python scripts/calculate_model_cost.py --search nova

    # Show detailed pricing for a model
    python scripts/calculate_model_cost.py --model amazon/nova-pro-v1:0 --show-pricing

    # Interactive mode
    python scripts/calculate_model_cost.py --interactive
"""

import argparse
import os
import sys
from typing import Optional

# Add the src directory to the path so we can import helm modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from helm.benchmark.model_pricing import (
    ModelPricingRegistry,
    calculate_cost,
    format_cost,
    ModelPricing,
)


def print_cost_breakdown(
    model_name: str, input_tokens: int, output_tokens: int, pricing: ModelPricing, total_cost: float
) -> None:
    """Print a detailed cost breakdown."""
    input_cost = input_tokens * pricing.input_price_per_token
    output_cost = output_tokens * pricing.output_price_per_token

    print("\n" + "=" * 70)
    print(f"Model: {model_name}")
    if pricing.notes:
        print(f"Description: {pricing.notes}")
    print("=" * 70)
    print(f"\nInput tokens:  {input_tokens:,}")
    print(f"Output tokens: {output_tokens:,}")
    print(f"Total tokens:  {input_tokens + output_tokens:,}")
    print(f"\nPricing:")
    print(f"  Input:  ${pricing.input_price_per_million:.2f} per 1M tokens")
    print(f"  Output: ${pricing.output_price_per_million:.2f} per 1M tokens")
    print(f"\nCost breakdown:")
    print(f"  Input cost:  {format_cost(input_cost)}")
    print(f"  Output cost: {format_cost(output_cost)}")
    print(f"  {'─' * 40}")
    print(f"  Total cost:  {format_cost(total_cost)}")
    print("=" * 70 + "\n")


def list_all_models() -> None:
    """List all models with pricing information."""
    models = ModelPricingRegistry.list_all_models()

    if not models:
        print("No models found in pricing database.")
        return

    print("\nAvailable models with pricing information:")
    print("=" * 70)

    # Group models by organization
    by_org = {}
    for model in models:
        org = model.split("/")[0] if "/" in model else "other"
        if org not in by_org:
            by_org[org] = []
        by_org[org].append(model)

    for org in sorted(by_org.keys()):
        print(f"\n{org.upper()}:")
        for model in by_org[org]:
            pricing = ModelPricingRegistry.get_pricing(model)
            print(f"  • {model}")
            if pricing and pricing.notes:
                print(f"    {pricing.notes}")

    print("\n" + "=" * 70)
    print(f"Total: {len(models)} models")
    print("=" * 70 + "\n")


def show_model_pricing(model_name: str) -> bool:
    """Show detailed pricing information for a model."""
    pricing = ModelPricingRegistry.get_pricing(model_name)

    if pricing is None:
        print(f"Error: No pricing information found for model '{model_name}'")
        print("\nUse --list-models to see available models")
        print(f"Or --search <term> to search for models")
        return False

    print("\n" + "=" * 70)
    print(f"Model: {pricing.model_name}")
    if pricing.notes:
        print(f"Description: {pricing.notes}")
    print("=" * 70)
    print(f"\nPricing (USD):")
    print(f"  Input:  ${pricing.input_price_per_million:.2f} per 1M tokens")
    print(f"  Output: ${pricing.output_price_per_million:.2f} per 1M tokens")
    print(f"\nPer-token rates:")
    print(f"  Input:  ${pricing.input_price_per_token:.8f} per token")
    print(f"  Output: ${pricing.output_price_per_token:.8f} per token")

    # Show example costs
    print(f"\nExample costs:")
    for input_tokens, output_tokens in [(1000, 1000), (10000, 5000), (100000, 50000)]:
        cost = pricing.calculate_cost(input_tokens, output_tokens)
        print(
            f"  {input_tokens:>6,} input + {output_tokens:>6,} output = {format_cost(cost)}"
        )

    print("=" * 70 + "\n")
    return True


def search_models(search_term: str) -> None:
    """Search for models by name."""
    matches = ModelPricingRegistry.search_models(search_term)

    if not matches:
        print(f"No models found matching '{search_term}'")
        return

    print(f"\nModels matching '{search_term}':")
    print("=" * 70)
    for model in matches:
        pricing = ModelPricingRegistry.get_pricing(model)
        print(f"\n• {model}")
        if pricing:
            print(f"  Input:  ${pricing.input_price_per_million:.2f}/1M tokens")
            print(f"  Output: ${pricing.output_price_per_million:.2f}/1M tokens")
            if pricing.notes:
                print(f"  {pricing.notes}")
    print("\n" + "=" * 70 + "\n")


def interactive_mode() -> None:
    """Run in interactive mode."""
    print("\n" + "=" * 70)
    print("Model Cost Calculator - Interactive Mode")
    print("=" * 70)
    print("\nType 'help' for commands, 'quit' to exit")

    while True:
        try:
            print("\n" + "-" * 70)
            cmd = input("Command> ").strip()

            if not cmd:
                continue

            if cmd.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if cmd.lower() in ["help", "h", "?"]:
                print("\nAvailable commands:")
                print("  list              - List all available models")
                print("  search <term>     - Search for models")
                print("  pricing <model>   - Show pricing for a model")
                print("  calc              - Calculate cost (interactive)")
                print("  help              - Show this help")
                print("  quit              - Exit")
                continue

            if cmd.lower().startswith("list"):
                list_all_models()
                continue

            if cmd.lower().startswith("search "):
                term = cmd[7:].strip()
                if term:
                    search_models(term)
                else:
                    print("Usage: search <term>")
                continue

            if cmd.lower().startswith("pricing "):
                model = cmd[8:].strip()
                if model:
                    show_model_pricing(model)
                else:
                    print("Usage: pricing <model>")
                continue

            if cmd.lower() in ["calc", "calculate"]:
                print("\nCalculate Model Invocation Cost")
                print("-" * 40)

                model_name = input("Model name: ").strip()
                if not model_name:
                    print("Error: Model name is required")
                    continue

                try:
                    input_tokens = int(input("Input tokens: ").strip())
                    output_tokens = int(input("Output tokens: ").strip())
                except ValueError:
                    print("Error: Token counts must be integers")
                    continue

                if input_tokens < 0 or output_tokens < 0:
                    print("Error: Token counts must be non-negative")
                    continue

                pricing = ModelPricingRegistry.get_pricing(model_name)
                if pricing is None:
                    print(f"Error: No pricing information found for '{model_name}'")
                    print("Use 'list' to see available models")
                    continue

                cost = pricing.calculate_cost(input_tokens, output_tokens)
                print_cost_breakdown(model_name, input_tokens, output_tokens, pricing, cost)
                continue

            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit.")
        except EOFError:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate model invocation costs based on token usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate cost for a specific model
  %(prog)s --model amazon/nova-pro-v1:0 --input-tokens 1000 --output-tokens 500

  # List all available models
  %(prog)s --list-models

  # Search for models containing "nova"
  %(prog)s --search nova

  # Show pricing for a specific model
  %(prog)s --model amazon/nova-pro-v1:0 --show-pricing

  # Interactive mode
  %(prog)s --interactive
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
        "--list-models", "-l", action="store_true", help="List all available models with pricing"
    )

    parser.add_argument(
        "--search", "-s", type=str, help="Search for models by name"
    )

    parser.add_argument(
        "--show-pricing", "-p", action="store_true", help="Show detailed pricing for the specified model"
    )

    parser.add_argument(
        "--interactive", "-I", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed cost breakdown"
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        interactive_mode()
        return 0

    # List models
    if args.list_models:
        list_all_models()
        return 0

    # Search models
    if args.search:
        search_models(args.search)
        return 0

    # Show pricing for a model
    if args.show_pricing:
        if not args.model:
            print("Error: --model is required with --show-pricing")
            return 1
        return 0 if show_model_pricing(args.model) else 1

    # Calculate cost
    if args.model and args.input_tokens is not None and args.output_tokens is not None:
        if args.input_tokens < 0 or args.output_tokens < 0:
            print("Error: Token counts must be non-negative")
            return 1

        pricing = ModelPricingRegistry.get_pricing(args.model)

        if pricing is None:
            print(f"Error: No pricing information found for model '{args.model}'")
            print("\nUse --list-models to see available models")
            print(f"Or --search <term> to search for models")
            return 1

        cost = pricing.calculate_cost(args.input_tokens, args.output_tokens)

        if args.verbose:
            print_cost_breakdown(args.model, args.input_tokens, args.output_tokens, pricing, cost)
        else:
            print(f"Cost: {format_cost(cost)}")

        return 0

    # No valid action specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
