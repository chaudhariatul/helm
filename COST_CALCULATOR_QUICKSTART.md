# Model Cost Calculator - Quick Start Guide

## What is it?

A tool to calculate the cost of model invocations based on input and output token counts. Supports 32+ models including all Amazon Bedrock models (Nova, Titan, etc.).

## Quick Examples

### Calculate Cost (Simple)

```bash
python scripts/calculate_model_cost.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000
```

Output: `Cost: $0.0240`

### Calculate Cost (Detailed)

```bash
python scripts/calculate_model_cost.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000 \
  --verbose
```

### List All Models

```bash
python scripts/calculate_model_cost.py --list-models
```

### Search for Models

```bash
python scripts/calculate_model_cost.py --search nova
python scripts/calculate_model_cost.py --search gpt
python scripts/calculate_model_cost.py --search claude
```

### Show Model Pricing

```bash
python scripts/calculate_model_cost.py --model amazon/nova-pro-v1:0 --show-pricing
```

### Interactive Mode

```bash
python scripts/calculate_model_cost.py --interactive
```

Then use commands: `list`, `search nova`, `calc`, `help`, `quit`

## Python API

```python
import sys
sys.path.insert(0, 'src')

from helm.benchmark.model_pricing import calculate_cost, format_cost

# Calculate cost
cost = calculate_cost("amazon/nova-pro-v1:0", 10000, 5000)
print(f"Cost: {format_cost(cost)}")  # Cost: $0.0240
```

## Common Models

### Amazon Bedrock Nova Models
- `amazon/nova-micro-v1:0` - Cheapest, text-only
- `amazon/nova-lite-v1:0` - Low-cost multimodal
- `amazon/nova-pro-v1:0` - Balanced
- `amazon/nova-premier-v1:0` - Most capable

### OpenAI Models
- `openai/gpt-3.5-turbo` - Fast and cheap
- `openai/gpt-4o-mini` - Smaller GPT-4
- `openai/gpt-4o` - GPT-4 Optimized

### Anthropic Claude Models
- `anthropic/claude-3-haiku` - Fast and compact
- `anthropic/claude-3-sonnet` - Balanced
- `anthropic/claude-3-opus` - Most capable

## Cost Comparison (100K input + 50K output tokens)

| Model | Cost |
|-------|------|
| Nova Micro | $0.01 |
| Nova Lite | $0.02 |
| GPT-3.5 Turbo | $0.13 |
| Nova Pro | $0.24 |
| GPT-4o | $0.75 |

## Full Documentation

See `scripts/MODEL_COST_CALCULATOR_README.md` for complete documentation.

## Adding New Models

Edit `src/helm/benchmark/model_pricing.json`:

```json
{
  "model_name": "provider/model-name",
  "input_price_per_million": 1.00,
  "output_price_per_million": 2.00,
  "notes": "Model description"
}
```

## Help

```bash
python scripts/calculate_model_cost.py --help
```
