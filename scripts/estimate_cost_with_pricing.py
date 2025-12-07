#!/usr/bin/env python3
"""
Enhanced cost estimation script that provides actual dollar costs.

This script extends the functionality of estimate_cost.py by calculating actual costs
in USD based on token counts and model pricing.

Usage:
    python3 scripts/estimate_cost_with_pricing.py benchmark_output/runs/<Name of the run suite>
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from helm.benchmark.model_pricing import ModelPricingRegistry, format_cost


@dataclass
class ModelCost:
    total_num_prompt_tokens: int = 0
    total_num_completion_tokens: int = 0
    total_num_instances: int = 0

    @property
    def total_tokens(self) -> int:
        return self.total_num_prompt_tokens + self.total_num_completion_tokens

    def add_prompt_tokens(self, num_tokens: int):
        self.total_num_prompt_tokens += num_tokens

    def add_num_completion_tokens(self, num_tokens: int):
        self.total_num_completion_tokens += num_tokens

    def add_num_instances(self, num_instances: int):
        self.total_num_instances += num_instances

    def calculate_dollar_cost(self, model_name: str) -> float:
        """Calculate the dollar cost for this model based on pricing data."""
        pricing = ModelPricingRegistry.get_pricing(model_name)
        if pricing is None:
            return 0.0

        input_cost = self.total_num_prompt_tokens * pricing.input_price_per_token
        output_cost = self.total_num_completion_tokens * pricing.output_price_per_token
        return input_cost + output_cost


class CostCalculator:
    def __init__(self, run_suite_path: str):
        self._run_suite_path: str = run_suite_path

    def aggregate(self) -> Dict[str, ModelCost]:
        """Sums up the estimated number of tokens."""
        models_to_costs: Dict[str, ModelCost] = defaultdict(ModelCost)

        for run_dir in os.listdir(self._run_suite_path):
            run_path: str = os.path.join(self._run_suite_path, run_dir)

            if not os.path.isdir(run_path):
                continue

            run_spec_path: str = os.path.join(run_path, "run_spec.json")
            if not os.path.isfile(run_spec_path):
                continue

            # Extract the model name
            with open(run_spec_path) as f:
                run_spec = json.load(f)
                model: str = run_spec["adapter_spec"]["model"]
                cost: ModelCost = models_to_costs[model]

            metrics_path: str = os.path.join(run_path, "stats.json")
            with open(metrics_path) as f:
                metrics: List[Dict] = json.load(f)
                if len(metrics) == 0:
                    continue

                num_prompt_tokens: int = -1
                num_completion_tokens: int = -1
                num_instances: int = -1

                for metric in metrics:
                    metric_name: str = metric["name"]["name"]

                    # Don't count perturbations
                    if "perturbation" in metric["name"]:
                        continue

                    if metric_name == "num_prompt_tokens":
                        num_prompt_tokens = metric["sum"]
                    elif metric_name == "num_completion_tokens":
                        num_completion_tokens = metric["sum"]
                    elif metric_name == "num_instances":
                        num_instances = metric["sum"]

                assert (
                    num_prompt_tokens >= 0 and num_completion_tokens >= 0 and num_instances >= 0
                ), f"invalid metrics: {metrics}"
                cost.add_prompt_tokens(num_prompt_tokens * num_instances)
                cost.add_num_completion_tokens(num_completion_tokens * num_instances)
                cost.add_num_instances(num_instances)

        return models_to_costs


def print_cost_summary(model_costs: Dict[str, ModelCost], show_pricing: bool = True):
    """Print a summary of costs with optional pricing information."""
    grand_total_prompt_tokens: int = 0
    grand_total_completion_tokens: int = 0
    grand_total_num_instances: int = 0
    grand_total_cost: float = 0.0

    print("\n" + "=" * 90)
    print("Model Cost Estimation with Pricing")
    print("=" * 90)

    models_with_pricing = []
    models_without_pricing = []

    for model_name, model_cost in model_costs.items():
        pricing = ModelPricingRegistry.get_pricing(model_name)
        if pricing:
            models_with_pricing.append((model_name, model_cost))
        else:
            models_without_pricing.append((model_name, model_cost))

    # Print models with pricing
    if models_with_pricing:
        print("\nModels with pricing information:")
        print("-" * 90)
        for model_name, model_cost in models_with_pricing:
            dollar_cost = model_cost.calculate_dollar_cost(model_name)
            pricing = ModelPricingRegistry.get_pricing(model_name)

            print(f"\n{model_name}")
            print(f"  Tokens: {model_cost.total_num_prompt_tokens:,} input + "
                  f"{model_cost.total_num_completion_tokens:,} output = "
                  f"{model_cost.total_tokens:,} total")
            print(f"  Instances: {model_cost.total_num_instances:,}")

            if show_pricing and pricing:
                print(f"  Pricing: ${pricing.input_price_per_million:.2f}/1M input, "
                      f"${pricing.output_price_per_million:.2f}/1M output")
                print(f"  Estimated cost: {format_cost(dollar_cost)}")

            grand_total_prompt_tokens += model_cost.total_num_prompt_tokens
            grand_total_completion_tokens += model_cost.total_num_completion_tokens
            grand_total_num_instances += model_cost.total_num_instances
            grand_total_cost += dollar_cost

    # Print models without pricing
    if models_without_pricing:
        print("\n" + "-" * 90)
        print("Models without pricing information (add to model_pricing.json):")
        print("-" * 90)
        for model_name, model_cost in models_without_pricing:
            print(f"\n{model_name}")
            print(f"  Tokens: {model_cost.total_num_prompt_tokens:,} input + "
                  f"{model_cost.total_num_completion_tokens:,} output = "
                  f"{model_cost.total_tokens:,} total")
            print(f"  Instances: {model_cost.total_num_instances:,}")

            grand_total_prompt_tokens += model_cost.total_num_prompt_tokens
            grand_total_completion_tokens += model_cost.total_num_completion_tokens
            grand_total_num_instances += model_cost.total_num_instances

    # Print grand totals
    print("\n" + "=" * 90)
    print("Grand Totals:")
    print(f"  Total prompt tokens: {grand_total_prompt_tokens:,}")
    print(f"  Total completion tokens: {grand_total_completion_tokens:,}")
    print(f"  Total tokens: {grand_total_prompt_tokens + grand_total_completion_tokens:,}")
    print(f"  Total instances: {grand_total_num_instances:,}")

    if show_pricing and grand_total_cost > 0:
        print(f"  Total estimated cost: {format_cost(grand_total_cost)}")
        print(f"\n  Note: Cost estimate only includes models with pricing information.")

    print("=" * 90 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Estimate token usage and costs for a run suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("run_suite_path", type=str, help="Path to runs folder")
    parser.add_argument(
        "--no-pricing",
        action="store_true",
        help="Don't show pricing information (only token counts)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.run_suite_path):
        print(f"Error: Path does not exist: {args.run_suite_path}")
        sys.exit(1)

    calculator = CostCalculator(args.run_suite_path)
    model_costs: Dict[str, ModelCost] = calculator.aggregate()

    if not model_costs:
        print(f"No model costs found in {args.run_suite_path}")
        sys.exit(0)

    print_cost_summary(model_costs, show_pricing=not args.no_pricing)
