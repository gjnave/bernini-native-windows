import argparse
import os
import sys
from pathlib import Path


FAST_MODES = {"sage2", "sage", "sage3", "flash", "radial"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Wan2GP CUDA and attention runtime")
    parser.add_argument("--repo", default="vendor/Wan2GP", help="Wan2GP checkout path")
    parser.add_argument("--attention", default="auto")
    parser.add_argument("--require-fast-attention", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"[ERROR] Missing Wan2GP checkout: {repo}")
        return 1

    sys.path.insert(0, str(repo))
    os.chdir(repo)

    import torch

    print(f"[OK] torch {torch.__version__}")
    print(f"[OK] torch cuda build: {torch.version.cuda}")
    if not torch.cuda.is_available():
        print("[ERROR] torch.cuda.is_available() is false")
        return 1

    device = torch.cuda.current_device()
    name = torch.cuda.get_device_name(device)
    major, minor = torch.cuda.get_device_capability(device)
    total_gb = torch.cuda.get_device_properties(device).total_memory / (1024 ** 3)
    print(f"[OK] CUDA device: {name}")
    print(f"[OK] Compute capability: {major}.{minor}")
    print(f"[OK] VRAM: {total_gb:.1f} GB")

    from shared.attention import get_attention_modes, get_supported_attention_modes, resolve_attention_mode

    installed = get_attention_modes()
    supported = get_supported_attention_modes()
    print(f"[OK] Installed attention modes: {', '.join(installed)}")
    print(f"[OK] Supported attention modes: {', '.join(supported)}")

    try:
        resolved = resolve_attention_mode(args.attention)
        print(f"[OK] Requested attention '{args.attention}' resolves to '{resolved}'")
    except Exception as exc:
        print(f"[ERROR] Attention mode '{args.attention}' is not usable: {exc}")
        return 1

    if args.require_fast_attention and not (FAST_MODES & set(supported)):
        if os.environ.get("WANGP_ALLOW_SDPA") == "1":
            print("[WARN] No fast attention mode found; WANGP_ALLOW_SDPA=1 allows SDPA fallback.")
        else:
            print("[ERROR] No supported Sage/Flash attention mode found.")
            print("[INFO] Set WANGP_ALLOW_SDPA=1 only if slower SDPA fallback is acceptable.")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
