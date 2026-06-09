# Installer Notes

## Low-VRAM Wan2GP Installer

`install_wan2gp_bernini_lowvram.bat` is the recommended route for consumer NVIDIA cards.

1. Shows a compatibility disclaimer and requires acknowledgement.
2. Detects Git, Python 3.11, curl, optional aria2, NVIDIA GPU, and CUDA visibility.
3. Clones `deepbeepmeep/Wan2GP` into `vendor\Wan2GP` and checks out the pinned commit recorded in the batch file.
4. Creates `.venv-wan2gp` with Python 3.11.
5. Installs PyTorch CUDA 13.0, Wan2GP requirements, Triton Windows, SageAttention, FlashAttention, and GGUF CUDA kernels.
6. Writes `vendor\Wan2GP\wgp_config.json` with Bernini selected, int8 transformer/text encoder quantization, and memory profile `4` by default.
7. Verifies CUDA and a supported Sage/Flash attention mode unless `WANGP_ALLOW_SDPA=1` is set.
8. Downloads the Wan2GP Bernini int8 model files into `vendor\Wan2GP\ckpts`.
9. Writes `logs\WAN2GP_INSTALL_SUMMARY.txt` and launch instructions.

## Native Installer

`install.bat` is retained as the native ByteDance reference path.

1. Shows a compatibility disclaimer and requires acknowledgement.
2. Detects Git, Python 3.11, curl, optional aria2, NVIDIA GPU, and CUDA visibility.
3. Creates `.venv` with Python 3.11.
4. Clones `bytedance/Bernini` into `vendor\Bernini` and checks out the pinned commit recorded in `install.bat`.
5. Installs upstream requirements.
6. Attempts to install and verify FlashAttention-3 on Hopper or FlashAttention-2 on other CUDA GPUs.
7. Downloads the selected model profile into `models\`.
8. Patches local model config files so runtime loads local files instead of silently downloading.
9. Writes `config\model_profile.cmd`, `logs\INSTALL_SUMMARY.txt`, and launch instructions.

## Fast Attention Policy

Native Bernini checks attention backends in this order:

1. `flash_attn_interface` for FlashAttention-3.
2. `flash_attn` for FlashAttention-2.
3. PyTorch SDPA fallback.

This installer treats FlashAttention-2 or FlashAttention-3 as required unless `BERNINI_ALLOW_SDPA=1` is set before install. That keeps failures visible when the goal is a CUDA/fast-attention-ready build.

Wan2GP checks Sage/Flash attention through `tools\verify_wan2gp_env.py`. The low-VRAM installer treats Sage/Flash as required unless `WANGP_ALLOW_SDPA=1` is set before install.

## Existing Models

When a model file already exists, `tools\download_models.py` asks whether to replace it, skip it, replace all, or skip all. Partial curl downloads are kept with a `.part` suffix. Partial aria2 downloads are resumed by aria2 on the next run.

## Uninstall

Delete the cloned repo folder. By default that is:

```text
D:\apps2review\bernini\bernini
```

The installer keeps venvs, caches, models, and outputs inside that folder.

