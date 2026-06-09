# Bernini Model Sources

This document records every model location used or considered by the installer. Downloads are performed with direct HTTPS URLs through `aria2c.exe` when present and `curl.exe` otherwise. The `hf` CLI is not used.

## Wan2GP Low-VRAM Profile

`install_wan2gp_bernini_lowvram.bat` downloads these files directly into `vendor\Wan2GP\ckpts`. Wan2GP's default checkpoint search paths are `ckpts` and `.`, so the files are visible without using its Hugging Face downloader.

| Source | File | Target | Purpose |
| --- | --- | --- | --- |
| https://huggingface.co/DeepBeepMeep/Wan2.2 | `bernini_r_wan2.2_high_quanto_bf16_int8.safetensors` | `vendor\Wan2GP\ckpts\bernini_r_wan2.2_high_quanto_bf16_int8.safetensors` | Bernini high-noise transformer, int8 |
| https://huggingface.co/DeepBeepMeep/Wan2.2 | `bernini_r_wan2.2_low_quanto_bf16_int8.safetensors` | `vendor\Wan2GP\ckpts\bernini_r_wan2.2_low_quanto_bf16_int8.safetensors` | Bernini low-noise transformer, int8 |
| https://huggingface.co/DeepBeepMeep/Wan2.1/tree/main/umt5-xxl | `models_t5_umt5-xxl-enc-quanto_int8.safetensors` plus tokenizer files | `vendor\Wan2GP\ckpts\umt5-xxl\` | Wan UMT5 text encoder/tokenizer |
| https://huggingface.co/DeepBeepMeep/Wan2.1 | `Wan2.1_VAE.safetensors` and `Wan2.1_VAE_upscale2x_imageonly_real_v1.safetensors` | `vendor\Wan2GP\ckpts\` | Wan VAE and optional upsampler |
| https://huggingface.co/DeepBeepMeep/Wan2.1/tree/main/xlm-roberta-large | CLIP/reference encoder safetensors plus tokenizer files | `vendor\Wan2GP\ckpts\xlm-roberta-large\` | Reference-image encoder assets used by Wan-family modes |

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
- Wan2GP runtime: https://github.com/deepbeepmeep/Wan2GP
- FlashAttention: https://github.com/Dao-AILab/flash-attention
- VeOmni optional multi-GPU dependency: https://github.com/ByteDance-Seed/VeOmni
- Wan2GP SageAttention Windows wheel: https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post4/sageattention-2.2.0+cu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl
- Wan2GP FlashAttention Windows wheel: https://github.com/deepbeepmeep/kernels/releases/download/Flash2/flash_attn-2.8.3-cp311-cp311-win_amd64.whl
- Wan2GP GGUF CUDA kernels wheel: https://github.com/deepbeepmeep/kernels/releases/download/GGUF_Kernels/llamacpp_gguf_cuda-1.0.2+torch210cu13py311-cp311-cp311-win_amd64.whl
