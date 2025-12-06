# Corrected Command Format for Amazon Nova Models

## The Original Command (WITH ERRORS)

```bash
!AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Problems:**
1. ❌ `!` prefix causes NoRegionError (Jupyter-only syntax)
2. ❌ Model configuration caused ValidationException (needed inference profile)

---

## The Corrected Command (ALL FIXES APPLIED)

### Method 1: Export Environment Variable (Recommended)

```bash
# Set the region first
export AWS_REGION=us-west-2

# Then run HELM (inference profile used automatically)
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Advantages:**
- Region persists for multiple commands
- Clear and explicit
- Works for entire shell session

---

### Method 2: Inline Environment Variable

```bash
# Set region inline (inference profile used automatically)
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Advantages:**
- Single command
- No persistent environment changes
- Good for one-off executions

---

### Method 3: Use Convenience Script

```bash
# Script handles region setting and uses inference profile automatically
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5
```

**Advantages:**
- Simplest to use
- Validates AWS credentials
- Shows detailed configuration
- Includes error checking

---

## What Changed Behind the Scenes

### Fix 1: Region Configuration
- **Before:** `!AWS_REGION=...` (wrong syntax)
- **After:** `AWS_REGION=...` or `export AWS_REGION=...` (correct syntax)

### Fix 2: Inference Profile (Automatic)
- **Before:** Model ID `amazon.nova-pro-v1:0` (rejected by AWS)
- **After:** Inference profile `us.amazon.nova-pro-v1:0` (configured automatically)

**You don't need to change the model name!** Just use `amazon/nova-pro-v1:0` as usual.

---

## Examples for All Nova Models

### Nova Pro (Best Performance)
```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### Nova Lite (Balanced)
```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=anatomy,model=amazon/nova-lite-v1:0 --suite quick-test --max-eval-instances 10
```

### Nova Micro (Fast & Cost-Effective)
```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=computer_science,model=amazon/nova-micro-v1:0 --suite quick-test --max-eval-instances 20
```

---

## Different Subjects

```bash
export AWS_REGION=us-west-2

# Clinical knowledge
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Anatomy
helm-run --run-entries mmlu:subject=anatomy,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Computer science
helm-run --run-entries mmlu:subject=computer_science,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# College medicine
helm-run --run-entries mmlu:subject=college_medicine,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

---

## Different Regions

### US West (Oregon) - Recommended
```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### US East (N. Virginia)
```bash
export AWS_REGION=us-east-1
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### EU (Frankfurt) - If Nova is available
```bash
export AWS_REGION=eu-central-1
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Note:** The `us.amazon.nova-pro-v1:0` inference profile works from any region. The AWS_REGION just specifies which Bedrock API endpoint to connect to.

---

## Batch Commands

```bash
# Set region once for multiple commands
export AWS_REGION=us-west-2

# Run multiple benchmarks
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
helm-run --run-entries mmlu:subject=anatomy,model=amazon/nova-lite-v1:0 --suite quick-test --max-eval-instances 10
helm-run --run-entries mmlu:subject=computer_science,model=amazon/nova-micro-v1:0 --suite quick-test --max-eval-instances 20
```

---

## In Jupyter Notebooks

If you're using a Jupyter notebook, the `!` prefix is correct, but you need to persist it:

```python
# Set environment variable in notebook
import os
os.environ['AWS_REGION'] = 'us-west-2'

# Then run helm
!helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

Or:
```python
# Use inline (must persist with %env magic)
%env AWS_REGION=us-west-2

# Then run helm
!helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

---

## Verification

### Verify AWS Region is Set
```bash
echo $AWS_REGION
# Should output: us-west-2 (or your chosen region)
```

### Verify Configuration
```bash
./test_nova_inference_profile.sh
# Should show all tests passing
```

### Test with Actual Benchmark
```bash
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5
# Should run without errors
```

---

## Error Messages You Should NOT See

✅ **FIXED - You should NOT see these anymore:**

```
❌ botocore.exceptions.NoRegionError: You must specify a region.
```

```
❌ botocore.errorfactory.ValidationException: An error occurred (ValidationException) 
   when calling the Converse operation: Invocation of model ID amazon.nova-pro-v1:0 
   with on-demand throughput isn't supported.
```

✅ **If you still see these errors:**
1. Check you're using the corrected command format (no `!` prefix)
2. Verify region is set: `echo $AWS_REGION`
3. Run verification: `./test_nova_inference_profile.sh`
4. See troubleshooting: [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│           AMAZON NOVA COMMAND QUICK REFERENCE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ❌ WRONG:                                                   │
│  !AWS_REGION=us-west-2 helm-run --run-entries ...           │
│                                                              │
│  ✅ CORRECT:                                                 │
│  export AWS_REGION=us-west-2                                 │
│  helm-run --run-entries ...                                  │
│                                                              │
│  OR:                                                         │
│  AWS_REGION=us-west-2 helm-run --run-entries ...            │
│                                                              │
│  OR:                                                         │
│  ./run_nova_with_fixes.sh amazon/nova-pro-v1:0 subject 5    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Models: amazon/nova-pro-v1:0                                │
│          amazon/nova-lite-v1:0                               │
│          amazon/nova-micro-v1:0                              │
│                                                              │
│  Inference profiles: Used automatically ✓                    │
│                                                              │
│  Regions: us-west-2 (recommended)                            │
│           us-east-1                                          │
│           eu-central-1 (if available)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Documentation

- **Quick Start:** [AWS_BEDROCK_FIX.md](AWS_BEDROCK_FIX.md)
- **Technical Details:** [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md)
- **Complete Summary:** [COMPLETE_FIX_SUMMARY.md](COMPLETE_FIX_SUMMARY.md)
- **Credentials Setup:** [docs/credentials.md](docs/credentials.md)

---

**Status:** ✅ BOTH ERRORS FIXED - Ready to use!
