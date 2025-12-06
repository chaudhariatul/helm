# Amazon Nova on HELM - START HERE

## 🎉 Both Errors Are Fixed!

You can now run HELM benchmarks with Amazon Nova models successfully.

---

## Quick Start (30 seconds)

### Option 1: Use the Convenience Script (Easiest)

```bash
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5
```

### Option 2: Manual Command

```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### Option 3: Inline

```bash
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

---

## Verify Everything Works

```bash
./test_nova_inference_profile.sh
```

All tests should pass ✓

---

## What Was Fixed?

### Error 1: NoRegionError ✅
- **Was:** `!AWS_REGION=us-west-2 helm-run ...` (❌ wrong)
- **Now:** `AWS_REGION=us-west-2 helm-run ...` (✅ correct)

### Error 2: ValidationException ✅
- **Was:** Direct model ID `amazon.nova-pro-v1:0` (❌ rejected by AWS)
- **Now:** Inference profile `us.amazon.nova-pro-v1:0` (✅ automatic)

---

## Available Models

- `amazon/nova-pro-v1:0` - Best performance
- `amazon/nova-lite-v1:0` - Balanced
- `amazon/nova-micro-v1:0` - Fastest & economical

---

## Need More Info?

### For Users
📄 **[AMAZON_NOVA_README.md](AMAZON_NOVA_README.md)** - Quick start guide  
📄 **[AWS_BEDROCK_FIX.md](AWS_BEDROCK_FIX.md)** - Quick reference  
📄 **[CORRECTED_NOVA_COMMAND.md](CORRECTED_NOVA_COMMAND.md)** - Command examples

### For Technical Details
📄 **[AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md)** - Complete guide  
📄 **[COMPLETE_FIX_SUMMARY.md](COMPLETE_FIX_SUMMARY.md)** - Executive summary  
📄 **[TASK_COMPLETION_SUMMARY.md](TASK_COMPLETION_SUMMARY.md)** - What was done

---

## Prerequisites

1. **AWS Credentials**
   ```bash
   aws configure
   ```

2. **AWS Region**
   ```bash
   export AWS_REGION=us-west-2
   ```

3. **Nova Models Enabled** in your AWS account

---

## Quick Reference

```
┌────────────────────────────────────────────────────┐
│          FASTEST WAY TO GET STARTED                │
├────────────────────────────────────────────────────┤
│                                                     │
│  1. Run this command:                               │
│     ./run_nova_with_fixes.sh \                      │
│       amazon/nova-pro-v1:0 \                        │
│       clinical_knowledge 5                          │
│                                                     │
│  2. That's it! ✓                                    │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

**Status:** ✅ READY TO USE

**Need Help?** See [AMAZON_NOVA_README.md](AMAZON_NOVA_README.md)
