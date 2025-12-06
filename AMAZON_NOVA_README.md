# Amazon Nova Models - Quick Start Guide

## ✅ Both AWS Configuration Errors Are Fixed!

If you were experiencing errors running HELM with Amazon Nova models, both issues have been resolved:

1. ✅ **NoRegionError** - Fixed (command syntax)
2. ✅ **ValidationException** - Fixed (inference profiles)

---

## Quick Start

### Run a Benchmark (Easy Way)

```bash
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5
```

That's it! The script handles everything.

### Run a Benchmark (Manual Way)

```bash
# 1. Set AWS region
export AWS_REGION=us-west-2

# 2. Run HELM
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

---

## Verify the Fix

```bash
./test_nova_inference_profile.sh
```

All tests should pass! ✓

---

## What Was Fixed?

### Error 1: NoRegionError
**Problem:** Command used `!AWS_REGION=...` (wrong for bash/shell)  
**Solution:** Use `AWS_REGION=...` or `export AWS_REGION=...`

### Error 2: ValidationException
**Problem:** Nova models required inference profile IDs  
**Solution:** Configuration updated to use `us.amazon.nova-pro-v1:0` automatically

**You don't need to change anything!** The fix is automatic when you use the model name `amazon/nova-pro-v1:0`.

---

## Available Models

- `amazon/nova-pro-v1:0` - Best performance
- `amazon/nova-lite-v1:0` - Balanced (fast & cost-effective)
- `amazon/nova-micro-v1:0` - Fastest & most economical

---

## Documentation

### Start Here
📄 [AWS_BEDROCK_FIX.md](AWS_BEDROCK_FIX.md) - Quick reference for both errors

### Complete Guides
📄 [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md) - Complete technical documentation  
📄 [COMPLETE_FIX_SUMMARY.md](COMPLETE_FIX_SUMMARY.md) - Executive summary  
📄 [CORRECTED_NOVA_COMMAND.md](CORRECTED_NOVA_COMMAND.md) - Command examples

### Files Changed
📄 [FILES_CHANGED_NOVA_FIX.txt](FILES_CHANGED_NOVA_FIX.txt) - Complete list of changes  
📄 [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) - Technical implementation details

---

## Troubleshooting

### "NoRegionError: You must specify a region"
**Solution:**
```bash
export AWS_REGION=us-west-2
```

### "ValidationException: ... on-demand throughput isn't supported"
**Solution:** Already fixed! Run the verification test:
```bash
./test_nova_inference_profile.sh
```

### Still Having Issues?
See the complete troubleshooting guide:
📄 [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md#troubleshooting)

---

## Examples

### Different Models
```bash
# Nova Pro
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5

# Nova Lite
./run_nova_with_fixes.sh amazon/nova-lite-v1:0 anatomy 10

# Nova Micro
./run_nova_with_fixes.sh amazon/nova-micro-v1:0 computer_science 20
```

### Different Regions
```bash
# US West
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# US East
export AWS_REGION=us-east-1
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

---

## Prerequisites

1. **AWS Credentials:** Run `aws configure` to set up
2. **AWS Region:** Set `AWS_REGION` environment variable
3. **Model Access:** Ensure Nova models are enabled in your AWS account

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                  AMAZON NOVA QUICK START                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Easy Way:                                                   │
│  ./run_nova_with_fixes.sh amazon/nova-pro-v1:0 subject 5    │
│                                                              │
│  Manual Way:                                                 │
│  export AWS_REGION=us-west-2                                 │
│  helm-run --run-entries mmlu:subject=clinical_knowledge,\   │
│    model=amazon/nova-pro-v1:0 --suite quick-test \          │
│    --max-eval-instances 5                                    │
│                                                              │
│  Verify:                                                     │
│  ./test_nova_inference_profile.sh                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Status:** ✅ READY TO USE - Both errors fixed and tested

**Need Help?** See [AWS_BEDROCK_FIX.md](AWS_BEDROCK_FIX.md) or [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md)
