# Bernini Windows Installers

Windows/NVIDIA installers for [bytedance/Bernini](https://github.com/bytedance/Bernini), with two paths:

- `install_wan2gp_bernini_lowvram.bat`: recommended practical path for lower VRAM. It installs [Wan2GP](https://github.com/deepbeepmeep/Wan2GP), configures Bernini-R, uses int8 Bernini weights, checks CUDA and Sage/Flash attention, and predownloads the model files with `aria2c.exe` when available and `curl.exe` otherwise.
- `install.bat`: native ByteDance reference path. It keeps upstream Bernini behavior close to the official repo, but consumer-card VRAM is not guaranteed.

No PowerShell and no `hf` CLI are used by the installer.

## Quick Start

Recommended low-VRAM bootstrap from the parent installer folder:

```bat
install_bernini_lowvram.bat
```

Native reference bootstrap from the parent installer folder:

```bat
install_bernini_native.bat
```

Manual low-VRAM clone:

```bat
git clone https://github.com/gjnave/bernini-native-windows.git
cd bernini-native-windows
install_wan2gp_bernini_lowvram.bat
RUN_GUI.bat
```

To immediately prove generation works after install, double-click:

```bat
run_bernini_smoke.bat
```

It verifies CUDA/fast attention, checks missing model files, renders a five-frame Bernini MP4, and opens `outputs-wan2gp\smoke`.

## Requirements

- Windows with an NVIDIA CUDA GPU.
- Current NVIDIA driver.
- Python 3.11 available through the Windows `py` launcher.
- Git for Windows.
- `curl.exe` in PATH.
- Optional: `aria2c.exe` in PATH for faster/resumable model downloads.
- CUDA toolkit and Visual Studio build tools are needed if fast attention must be built locally.

The Wan2GP low-VRAM path installs PyTorch CUDA 13.0, Triton Windows, SageAttention, FlashAttention, and GGUF CUDA kernels from direct wheel URLs. It verifies CUDA and requires a supported Sage/Flash mode unless `WANGP_ALLOW_SDPA=1` is set.

The native path tries FlashAttention-3 on Hopper or FlashAttention-2 on other CUDA GPUs, then PyTorch SDPA. It requires FlashAttention-2 or FlashAttention-3 unless `BERNINI_ALLOW_SDPA=1` is set.

## Low-VRAM Direction

The native ByteDance path is no longer treated as guaranteed for consumer VRAM. The recommended target is Wan2GP because it has first-class Bernini support, int8 checkpoint selection, memory offload profiles, and a web UI that already knows how to run Bernini-R.

Wan2GP memory profile defaults:

- Profile `4`: default low-RAM/low-VRAM target, intended for 12 GB+ VRAM.
- Profile `4.5`: slightly slower, lower VRAM variant.
- Profile `5`: failsafe for very low VRAM, slower.
- Profile `3`: faster 24 GB path for RTX 3090/4090-class cards.

Example:

```bat
install_wan2gp_bernini_lowvram.bat --profile 4
run_wan2gp_bernini.bat --profile 4 --port 7860
```

## Model Profiles

The native installer menu offers:

- `official-diffusers`: ByteDance's self-contained Bernini-R Diffusers layout. Best native compatibility; H100/A100-class VRAM is the realistic target.
- `neuregex-fp8`: self-contained FP8 Diffusers-layout bundle. Smaller and 24 GB ComfyUI-proven, but native Bernini FP8 behavior is experimental.
- `kijai-fp8-separate`: FP8 high/low checkpoints plus local Wan2.2 base. Experimental for native Bernini.
- `abiray-fp8-separate`: alternate FP8 high/low checkpoints plus local Wan2.2 base. Experimental for native Bernini.

Model source URLs and compatibility notes are in [docs/MODEL_SOURCES.md](docs/MODEL_SOURCES.md).

## Layout

```text
.venv\                 Python environment
.venv-wan2gp\          Wan2GP Python environment
vendor\Bernini\         cloned upstream Bernini repo
vendor\Wan2GP\          cloned Wan2GP repo
models\                 downloaded model files
vendor\Wan2GP\ckpts\    Wan2GP model files
config\model_profile.cmd selected launch profile
outputs\               Gradio output
outputs-wan2gp\         Wan2GP output
logs\                  install breadcrumbs
```

## Launch

Low-VRAM:

```bat
RUN_GUI.bat
```

This launches the Wan2GP Gradio GUI for Bernini and opens the browser by default. It calls `run_wan2gp_bernini.bat` under the hood, so advanced options such as `--profile 4.5`, `--port 7861`, or `--no-open` still work. The Bernini prompt area includes a trained-task prefix dropdown with the `default`, `t2i`, `t2v`, `i2i`, `r2i`, `i2v`, `v2v`, `r2v`, `vi2v`, `rv2v`, `ads2v`, `vrc2v`, and `mv2v` prefixes.

One-click smoke render:

```bat
run_bernini_smoke.bat
```

Native:

```bat
run.bat
```

Pass upstream Gradio arguments after `run.bat`:

```bat
run.bat --port 7861 --share
```

Both launchers set local cache folders and default to Hugging Face Hub offline mode after install so runtime does not silently redownload model files. Set `WANGP_ALLOW_ONLINE=1` for Wan2GP or `BERNINI_ALLOW_ONLINE=1` for native Bernini if you intentionally want upstream libraries to reach the network.
