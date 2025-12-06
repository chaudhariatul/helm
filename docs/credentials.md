# Credentials

## Credentials file

You should create a `credentials.conf` file in your local configuration folder, which is `./prod_env/` by default, unless you have overridden it using the `--local-path` flag to `helm-run`. This file should be in HOCON format. Example:

```
platformOneApiKey: sk-abcdefgh
platformTneApiKey: sk-ijklmnop
```

Here are the keys that must be set for to access these platforms:

- AI21: `ai21ApiKey`
- Aleph Alpha: `AlephAlphaApiKey`
- Anthropic: `anthropicApiKey`
- AWS Bedrock: None, but see Additional Setup below
- Cohere: `cohereApiKey`
- Google: `googleProjectId`, `googleLocation`, also see Additional Setup below
- GooseAI: `gooseApiKey`
- Hugging Face Hub: None, but see Additional Setup below
- Mistral AI: `mistralaiApiKey`
- OpenAI: `openaiApiKey`, `openApiOrgId`
- Perspective: `perspectiveApiKey`
- Writer: `writerApiKey`

## Additional setup

### AWS Bedrock

AWS Bedrock models (including Amazon Nova, Titan, and third-party models available on Bedrock) require AWS credentials and region configuration.

#### Authentication

You need to configure AWS credentials. Choose one of the following methods:

1. **AWS CLI Configuration** (Recommended):
   ```bash
   aws configure
   ```
   This will create `~/.aws/credentials` and `~/.aws/config` files with your AWS access key, secret key, and default region.

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

3. **IAM Role** (for EC2 instances or containers):
   If running on an EC2 instance with an IAM role attached, credentials will be automatically obtained.

#### Region Configuration

AWS Bedrock models require a region to be specified. You must set the `AWS_REGION` or `AWS_DEFAULT_REGION` environment variable:

```bash
export AWS_REGION=us-west-2
```

Or set it inline when running helm-run:

```bash
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Important**: The `!` prefix (used in Jupyter notebooks) should NOT be used in shell/terminal commands. Use the inline format above or export the variable first.

Available regions for Bedrock vary by model. Common regions include:
- `us-east-1` (US East - N. Virginia)
- `us-west-2` (US West - Oregon)
- `eu-central-1` (Europe - Frankfurt)

For model-specific region availability, refer to the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html).

#### Example Usage

```bash
# Set region and run benchmark
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Or use inline environment variable
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

See `scripts/examples/run_bedrock_models.sh` for more examples.

### Google

You will need to install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install). Then, as the user that will be running `helm-run`, run:

```
gcloud auth application-default login
gcloud auth application-default set-quota-project 123456789012
```

Replace `123456789012` with your actual _numeric_ project ID.

### Hugging Face Hub

If you are attempting to access models that are private, restricted, or require signing an agreement (e.g. Llama 2) through Hugging Face, you need to be authenticated to Hugging Face through the CLI. As the user that will be running `helm-run`, run:

```
huggingface-cli login
```

Refer to [Hugging Face's documentation](https://huggingface.co/docs/huggingface_hub/en/quick-start#login-command) for more information.