import argparse
import json
from pathlib import Path


def profile_value(raw: str) -> float:
    value = float(raw)
    allowed = {1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0}
    if value not in allowed:
        raise argparse.ArgumentTypeError("profile must be one of 1, 2, 3, 3.5, 4, 4.5, or 5")
    return value


def as_json_number(value: float):
    return int(value) if value.is_integer() else value


def write_config(root: Path, profile: float, attention: str) -> Path:
    wangp_dir = root / "vendor" / "Wan2GP"
    if not wangp_dir.exists():
        raise FileNotFoundError(f"Missing Wan2GP checkout: {wangp_dir}")

    output_dir = root / "outputs-wan2gp"
    output_dir.mkdir(parents=True, exist_ok=True)

    profile_no = as_json_number(profile)
    config = {
        "attention_mode": attention,
        "transformer_types": ["bernini"],
        "transformer_quantization": "int8",
        "text_encoder_quantization": "int8",
        "lm_decoder_engine": "",
        "save_path": str(output_dir),
        "image_save_path": str(output_dir),
        "audio_save_path": str(output_dir),
        "compile": "",
        "metadata_type": "metadata",
        "boost": 1,
        "enable_int8_kernels": 1,
        "clear_file_list": 5,
        "keep_intermediate_sliding_windows": 1,
        "enable_4k_resolutions": 0,
        "max_reserved_loras": -1,
        "vae_config": 0,
        "profile": profile_no,
        "video_profile": profile_no,
        "image_profile": profile_no,
        "audio_profile": profile_no,
        "preload_model_policy": [],
        "UI_theme": "default",
        "checkpoints_paths": ["ckpts", "."],
        "loras_root": "loras",
        "save_queue_if_crash": 1,
        "queue_color_scheme": "pastel",
        "process_queues_when_browser_unfocused": 1,
        "multi_prompts_gen_type": "PG",
        "model_hierarchy_type": 1,
        "mmaudio_mode": 0,
        "mmaudio_persistence": 1,
        "seedvc_mode": 0,
        "seedvc_persistence": 1,
        "flashvsr_mode": 0,
        "flashvsr_persistence": 1,
        "pid_tiling_threshold": 0,
        "pid_persistence": 1,
        "flashvsr_topk_ratio": 0.0,
        "rife_version": "v4",
        "prompt_enhancer_quantization": "quanto_int8",
        "prompt_enhancer_temperature": 0.6,
        "prompt_enhancer_top_p": 0.9,
        "prompt_enhancer_randomize_seed": True,
        "last_model_type": "bernini",
        "last_model_per_family": {"Wan": "bernini", "wan": "bernini"},
        "last_model_per_type": {"bernini": "bernini"},
        "last_advanced_choice": True,
    }

    out = wangp_dir / "wgp_config.json"
    out.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"[WRITE] {out}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure Wan2GP for Bernini low-VRAM mode")
    parser.add_argument("--root", default=".", help="installer repo root")
    parser.add_argument("--profile", type=profile_value, default=4.0)
    parser.add_argument("--attention", choices=["auto", "sage2", "sage", "flash", "sdpa"], default="auto")
    args = parser.parse_args()

    write_config(Path(args.root).resolve(), args.profile, args.attention)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
