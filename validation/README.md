# Validation & Hardware Testing

This folder contains notebooks used to validate AMD MI300X + ROCm compatibility

## Contents

### AMD_ROCm_validation.ipynb

**Purpose:** Hardware validation notebook to test AMD MI300X GPU and ROCm framework compatibility.

**What it does:**
- Verifies ROCm installation and GPU detection
- Tests PyTorch + ROCm integration (192GB HBM detection)
- Validates OpenEnv framework compatibility on AMD hardware
- Benchmarks training speed (Llama 3.1 8B: 40-80 tok/s vs GPT-OSS 20B: 3-8 tok/s)
- Tests GRPO reinforcement learning pipeline on simple 2048 game

**Key optimizations tested:**
- BF16 precision (instead of 4-bit quantization)
- LoRA rank 16 (vs default rank 4)
- Batch size 4 with gradient accumulation 4
- ROCm-specific environment variables
- Standard AdamW optimizer (bitsandbytes 8-bit not available on ROCm)

**Status:** ✅ Validation complete - all optimizations migrated to main MAROONED training pipeline.

---

**Note:** This is NOT the main project submission. For the actual MAROONED multi-agent environment and training, see:
- Main training: `notebooks/Train_Marooned_RL.ipynb`
- Environment code: `marooned_env/`
- Development phases: `notebooks/phase*.ipynb`
