# Bernini Native Windows Installer

Windows/NVIDIA installer wrapper for [bytedance/Bernini](https://github.com/bytedance/Bernini). The repo stays small: it clones upstream Bernini during install, creates a Python 3.11 venv, installs the pinned CUDA/PyTorch stack, verifies CUDA and fast attention, downloads the selected model profile with `aria2c.exe` when available and `curl.exe` otherwise, then launches the upstream Gradio demo.

No PowerShell and no `hf` CLI are used by the installer.

## Quick Start

From the parent installer folder:

```bat
install_bernini_native.bat
```

Manual clone:

```bat
git clone https://github.com/gjnave/bernini-native-windows.git
cd bernini-native-windows
install.bat
run.bat
```

## Requirements

- Windows with an NVIDIA CUDA GPU.
- Current NVIDIA driver.
- Python 3.11 available through the Windows `py` launcher.
- Git for Windows.
- `curl.exe` in PATH.
- Optional: `aria2c.exe` in PATH for faster/resumable model downloads.
- CUDA toolkit and Visual Studio build tools are needed if fast attention must be built locally.

Bernini upstream recommends Hopper GPUs for FlashAttention-3. Other CUDA GPUs try FlashAttention-2, then PyTorch SDPA. This installer requires FlashAttention-2 or FlashAttention-3 by default because this build is meant to prove the fast attention path. Set `BERNINI_ALLOW_SDPA=1` before running `install.bat` if you intentionally accept the slower SDPA fallback.

## Model Profiles

The installer menu offers:

- `official-diffusers`: ByteDance's self-contained Bernini-R Diffusers layout. Best native compatibility; H100/A100-class VRAM is the realistic target.
- `neuregex-fp8`: self-contained FP8 Diffusers-layout bundle. Smaller and 24 GB ComfyUI-proven, but native Bernini FP8 behavior is experimental.
- `kijai-fp8-separate`: FP8 high/low checkpoints plus local Wan2.2 base. Experimental for native Bernini.
- `abiray-fp8-separate`: alternate FP8 high/low checkpoints plus local Wan2.2 base. Experimental for native Bernini.

Model source URLs and compatibility notes are in [docs/MODEL_SOURCES.md](docs/MODEL_SOURCES.md).

## Layout

```text
.venv\                 Python environment
vendor\Bernini\         cloned upstream Bernini repo
models\                 downloaded model files
config\model_profile.cmd selected launch profile
outputs\               Gradio output
logs\                  install breadcrumbs
```

## Launch

```bat
run.bat
```

Pass upstream Gradio arguments after `run.bat`:

```bat
run.bat --port 7861 --share
```

The launcher sets local cache folders and `HF_HUB_OFFLINE=1` by default after install so runtime does not silently redownload model files. Set `BERNINI_ALLOW_ONLINE=1` if you intentionally want upstream libraries to reach the network.

