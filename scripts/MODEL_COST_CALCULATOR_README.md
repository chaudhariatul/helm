# Model Cost Calculator

A comprehensive tool for calculating the cost of model invocations based on input and output token counts. This tool supports all models available in the HELM system, including the newly added Amazon Bedrock models (Nova, Titan, etc.), as well as models from OpenAI, Anthropic, Google, Meta, Cohere, and AI21.

## Features

- **Cost Calculation**: Calculate exact costs based on input and output token counts
- **Model Search**: Search for models by name or keyword
- **Pricing Information**: View detailed pricing for any supported model
- **Interactive Mode**: Run the tool interactively for multiple calculations
- **Extensive Model Support**: Support for 32+ models including:
  - Amazon Bedrock models (Nova family, Titan, Mistral, Llama)
  - OpenAI models (GPT-4, GPT-3.5, O1)
  - Anthropic Claude models
  - Google Gemini models
  - Meta Llama models
  - Cohere and AI21 models

## Installation

No additional installation is required beyond the standard HELM dependencies. The tool is located in the `scripts/` directory and uses the `helm.benchmark.model_pricing` module.

## Usage

### Command Line Interface

#### Calculate Cost for a Model

```bash
python scripts/calculate_model_cost.py --model amazon/nova-pro-v1:0 --input-tokens 10000 --output-tokens 5000
```

Output:
```
Cost: $0.0240
```

#### Verbose Cost Breakdown

Add `--verbose` or `-v` flag for detailed breakdown:

```bash
python scripts/calculate_model_cost.py --model amazon/nova-pro-v1:0 --input-tokens 50000 --output-tokens 25000 --verbose
```

Output:
```
======================================================================
Model: amazon/nova-pro-v1:0
Description: Balanced accuracy, speed, and cost
======================================================================

Input tokens:  50,000
Output tokens: 25,000
Total tokens:  75,000

Pricing:
  Input:  $0.80 per 1M tokens
  Output: $3.20 per 1M tokens

Cost breakdown:
  Input cost:  $0.0400
  Output cost: $0.0800
  ────────────────────────────────────────
  Total cost:  $0.1200
======================================================================
```

#### List All Available Models

```bash
python scripts/calculate_model_cost.py --list-models
```

#### Search for Models

```bash
python scripts/calculate_model_cost.py --search nova
```

Output shows all models matching "nova" with their pricing.

#### Show Pricing Details

```bash
python scripts/calculate_model_cost.py --model amazon/nova-pro-v1:0 --show-pricing
```

#### Interactive Mode

```bash
python scripts/calculate_model_cost.py --interactive
```

Commands available in interactive mode:
- `list` - List all available models
- `search <term>` - Search for models
- `pricing <model>` - Show pricing for a model
- `calc` - Calculate cost (prompts for inputs)
- `help` - Show help
- `quit` - Exit

### Python API

You can also use the model pricing module directly in Python code:

```python
from helm.benchmark.model_pricing import (
    ModelPricingRegistry,
    calculate_cost,
    format_cost,
)

# Get pricing information for a model
pricing = ModelPricingRegistry.get_pricing("amazon/nova-pro-v1:0")
print(f"Input: ${pricing.input_price_per_million}/1M tokens")
print(f"Output: ${pricing.output_price_per_million}/1M tokens")

# Calculate cost directly
cost = calculate_cost("amazon/nova-pro-v1:0", input_tokens=10000, output_tokens=5000)
print(f"Total cost: {format_cost(cost)}")

# Search for models
models = ModelPricingRegistry.search_models("nova")
print(f"Found {len(models)} Nova models")

# List all models
all_models = ModelPricingRegistry.list_all_models()
```

## Supported Models

### Amazon Bedrock Models

#### Nova Models
- `amazon/nova-premier-v1:0` - Most capable Nova model
- `amazon/nova-pro-v1:0` - Balanced accuracy, speed, and cost
- `amazon/nova-lite-v1:0` - Low-cost multimodal model
- `amazon/nova-micro-v1:0` - Text-only, low latency
- `amazon/nova-2-pro-v1:0` - Advanced reasoning model
- `amazon/nova-2-lite-v1:0` - Fast, cost-effective reasoning
- `amazon/nova-2-sonic-v1:0` - Lightweight with fast response

#### Titan Models
- `amazon/titan-text-lite-v1` - Lightweight Titan
- `amazon/titan-text-express-v1` - Express Titan

#### Other Bedrock Models
- `mistralai/amazon-mistral-7b-instruct-v0:2` - Mistral 7B on Bedrock
- `meta/llama3-70b-instruct` - Llama 3 70B on Bedrock
- `meta/llama3-8b-instruct` - Llama 3 8B on Bedrock

### OpenAI Models
- `openai/gpt-4o` - GPT-4 Optimized
- `openai/gpt-4o-mini` - Smaller, faster GPT-4 variant
- `openai/gpt-4-turbo` - GPT-4 Turbo with 128K context
- `openai/gpt-4` - GPT-4 8K context
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo
- `openai/o1` - Reasoning model
- `openai/o1-mini` - Smaller reasoning model

### Anthropic Claude Models
- `anthropic/claude-3-opus` - Most capable Claude 3
- `anthropic/claude-3-sonnet` - Balanced Claude 3
- `anthropic/claude-3-haiku` - Fast and compact
- `anthropic/claude-3.5-sonnet` - Enhanced Claude 3.5
- `anthropic/claude-2.1` - Claude 2.1
- `anthropic/claude-2` - Claude 2

### Google Models
- `google/gemini-1.5-pro` - Gemini 1.5 Pro
- `google/gemini-1.5-flash` - Gemini 1.5 Flash
- `google/gemini-pro` - Gemini Pro

### Other Models
- Cohere Command R and Command R Plus
- AI21 Jurassic-2 models

## Examples

### Compare Costs Across Models

```bash
# Compare Nova models
for model in amazon/nova-micro-v1:0 amazon/nova-lite-v1:0 amazon/nova-pro-v1:0; do
    echo -n "$model: "
    python scripts/calculate_model_cost.py --model $model --input-tokens 100000 --output-tokens 50000
done
```

### Calculate Monthly Budget

```python
from helm.benchmark.model_pricing import calculate_cost

# Estimate monthly cost
daily_input_tokens = 1_000_000
daily_output_tokens = 500_000
days_per_month = 30

daily_cost = calculate_cost("amazon/nova-pro-v1:0", daily_input_tokens, daily_output_tokens)
monthly_cost = daily_cost * days_per_month

print(f"Daily cost: ${daily_cost:.2f}")
print(f"Monthly cost: ${monthly_cost:.2f}")
```

## Pricing Data

Pricing information is stored in `src/helm/benchmark/model_pricing.json` and can be easily updated as prices change. The file includes:
- Model name
- Input price per million tokens (USD)
- Output price per million tokens (USD)
- Notes/description

All prices are in USD and based on standard on-demand pricing as of December 2024.

## Updating Pricing

To update pricing information:

1. Edit `src/helm/benchmark/model_pricing.json`
2. Add or modify entries in the `models` array
3. Each entry should have:
   - `model_name`: Full model identifier
   - `input_price_per_million`: Cost per 1M input tokens
   - `output_price_per_million`: Cost per 1M output tokens
   - `notes`: Optional description

Example:
```json
{
  "model_name": "new-provider/new-model",
  "input_price_per_million": 1.00,
  "output_price_per_million": 2.00,
  "notes": "Description of the model"
}
```

## Tips

1. **Token Estimation**: Use tokenizers to estimate token counts for your text:
   - Generally, 1 token ≈ 4 characters or ≈ 0.75 words
   - Use model-specific tokenizers for accurate counts

2. **Cost Optimization**:
   - Use smaller models (micro, lite) for simple tasks
   - Reserve larger models (pro, premier) for complex reasoning
   - Compare costs before choosing a model

3. **Batch Processing**: For large workloads, consider:
   - Batch API endpoints (often 50% cheaper)
   - Reserved capacity for predictable workloads

## Troubleshooting

### Model Not Found

If you get "No pricing information found for model":
1. Check the model name spelling: `python scripts/calculate_model_cost.py --list-models`
2. Search for similar models: `python scripts/calculate_model_cost.py --search <keyword>`
3. Add pricing to `model_pricing.json` if the model is new

### Import Errors

If you encounter import errors when using the Python API:
```python
import sys
sys.path.insert(0, 'src')  # Add src to path
from helm.benchmark.model_pricing import calculate_cost
```

## Contributing

To add support for new models:
1. Add pricing information to `src/helm/benchmark/model_pricing.json`
2. Test the addition: `python scripts/calculate_model_cost.py --model <new-model> --show-pricing`
3. Update this README if adding a new model provider

## License

This tool is part of the HELM project and follows the same license.
