# Bernini Model Sources

This document records every model location used or considered by the installer. Downloads are performed with direct HTTPS URLs through `aria2c.exe` when present and `curl.exe` otherwise. The `hf` CLI is not used.

## Native Profiles

| Profile | Source | Target | Native Status | Notes |
| --- | --- | --- | --- | --- |
| `official-diffusers` | https://huggingface.co/ByteDance/Bernini-R-Diffusers | `models\ByteDance\Bernini-R-Diffusers` | Supported | Recommended by ByteDance. The repo bundles VAE, UMT5 text encoder, tokenizer, scheduler, and Bernini transformer weights. The installer patches `config.json` so `wan22_base` points to the local directory. |
| `neuregex-fp8` | https://huggingface.co/neuregex/Bernini-R-fp8 | `models\neuregex\Bernini-R-fp8` | Experimental native | Self-contained FP8 Diffusers-layout bundle. The model card states it is packaged for `ComfyUI-BerniniR` and measured to run in 24 GB there. Native upstream Bernini may cast or reject FP8 weights depending on loader behavior. |
| `kijai-fp8-separate` | https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini and https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers | `models\Kijai\WanVideo_comfy_fp8_scaled\Bernini` and `models\Wan-AI\Wan2.2-T2V-A14B-Diffusers` | Experimental native | Downloads the e4m3fn scaled HIGH/LOW safetensors into separate high/low folders so upstream `--high_noise_ckpt` and `--low_noise_ckpt` can target one checkpoint each. |
| `abiray-fp8-separate` | https://huggingface.co/Abiray/Wan22_Bernini_FP8_Scaled and https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers | `models\Abiray\Wan22_Bernini_FP8_Scaled` and `models\Wan-AI\Wan2.2-T2V-A14B-Diffusers` | Experimental native | Alternate e4m3fn scaled HIGH/LOW safetensors derived from ByteDance/Bernini-R. |

## Smaller ComfyUI-Oriented Models

These are documented because they are smaller and relevant to Bernini replication, but the native ByteDance scripts do not load GGUF directly.

| Source | Files | Status |
| --- | --- | --- |
| https://huggingface.co/neuregex/Bernini-R-GGUF | High/low Q4_K_M, Q5_K_M, Q8_0 `.gguf` pairs | ComfyUI-only unless a GGUF loader is added to the native app. The model card recommends ComfyUI-BerniniR plus city96/ComfyUI-GGUF. |
| https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini | HIGH/LOW fp8 and mxfp8 safetensors | ComfyUI-oriented. The installer uses the e4m3fn scaled pair for the `kijai-fp8-separate` native experiment. |

## Upstream Runtime Sources

- Bernini code: https://github.com/bytedance/Bernini
- FlashAttention: https://github.com/Dao-AILab/flash-attention
- VeOmni optional multi-GPU dependency: https://github.com/ByteDance-Seed/VeOmni

