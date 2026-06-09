# Low-VRAM Bernini Research

## Decision

The project should not claim native ByteDance Bernini is guaranteed on lower VRAM. The practical default is Wan2GP because it already implements Bernini-R as a Wan2.2-derived model, supports int8/fp8/GGUF-style low-bit workflows across the app, and exposes memory profiles for 12 GB to 24 GB NVIDIA cards.

The native installer remains useful as a reference path and for high-memory systems.

## Findings

| Project | Location | Why It Matters | Installer Decision |
| --- | --- | --- | --- |
| Wan2GP | https://github.com/deepbeepmeep/Wan2GP | First-class Bernini support, low-VRAM profiles, int8 Bernini high/low checkpoints, Sage/Flash attention docs. Wan2GP documents Bernini at about 12 GB VRAM for v2v and about 16 GB for v2v plus reference frames. | Use as the recommended low-VRAM installer path. |
| AIMixer/ComfyUI-Bernini | https://github.com/AIMixer/ComfyUI-Bernini | Standalone ComfyUI plugin for Wan2.2 Bernini. Documents GGUF tiers down to 8 GB VRAM and FP8 safetensors. | Documented as the lowest-VRAM Comfy route, but not the main installer target. |
| neuregex/ComfyUI-BerniniR | https://github.com/neuregex/ComfyUI-BerniniR | Reimplements Bernini-specific inference code on diffusers and reports FP8 operation in 24 GB. | Useful reference for Bernini inference behavior and FP8/GGUF compatibility. |
| neuregex/Bernini-R-GGUF | https://huggingface.co/neuregex/Bernini-R-GGUF | GGUF Bernini-R weights intended for ComfyUI-BerniniR plus ComfyUI-GGUF. | Documented as a lower-VRAM model source, but not used by the Wan2GP batch path. |
| city96/ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF | General GGUF loader for ComfyUI diffusion models and T5 text encoders. | Relevant if a future ComfyUI installer track is added. |
| ComfyUI core Bernini PR | https://github.com/Comfy-Org/ComfyUI/pull/14216 | Shows Bernini support moving into native ComfyUI Wan video handling. | Watch, but do not depend on it until merged/released. |

## Other GitHub Hits Checked

These were found in GitHub repo search and are documented for follow-up, but were not chosen as the primary installer target.

| Project | Location | Notes |
| --- | --- | --- |
| CCpt5/ComfyUI-BerniniStudio | https://github.com/CCpt5/ComfyUI-BerniniStudio | Prompting assistant/preset nodes for Bernini workflows, not a complete low-VRAM runtime by itself. |
| Deno2026/comfyui-deno-custom-nodes | https://github.com/Deno2026/comfyui-deno-custom-nodes | Mixed ComfyUI helper nodes including Bernini prompt/video-edit helpers. |
| RH-RunningHub/ComfyUI-RH-Bernini | https://github.com/RH-RunningHub/ComfyUI-RH-Bernini | RunningHub ComfyUI Bernini node/plugin. |
| filliptm/ComfyUI-FL-BerniniR | https://github.com/filliptm/ComfyUI-FL-BerniniR | Bernini-R ComfyUI nodes. |
| AvivK5498/Bernini-Runtime | https://github.com/AvivK5498/Bernini-Runtime | Bernini runtime experiment. |
| xocialize/bernini-r-mlx | https://github.com/xocialize/bernini-r-mlx | MLX-oriented Bernini-R experiment for Apple Silicon, not the Windows CUDA target. |

## Parameters Changed

- Recommended path: Wan2GP low-VRAM installer.
- Native path: reference/high-VRAM path only.
- Default low-VRAM model type: Bernini-R Wan2.2 int8 high/low transformer files from `DeepBeepMeep/Wan2.2`.
- Default Wan2GP memory profile: `4`, with `4.5` and `5` available for tighter VRAM and `3` available for 24 GB cards.
- Fast attention: require a supported Sage/Flash mode by default; allow SDPA only with `WANGP_ALLOW_SDPA=1`.

## Not Guaranteed

Even with Wan2GP, lower VRAM is workload-sensitive. Reference frames, longer frame counts, higher resolution, larger batches, and prompt enhancers can push memory over the edge. The installer therefore chooses conservative defaults and leaves the faster 24 GB profile as an explicit option.
