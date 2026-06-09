import argparse
import importlib.util
import os
import platform
import sys
from pathlib import Path


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Bernini CUDA and attention runtime")
    parser.add_argument("--repo", default="vendor/Bernini", help="upstream Bernini repo path")
    parser.add_argument("--require-fast-attention", action="store_true")
    args = parser.parse_args()

    print(f"[PYTHON] {sys.version.split()[0]} ({platform.platform()})")
    try:
        import torch
    except Exception as exc:
        print(f"[ERROR] torch import failed: {exc}")
        return 1

    print(f"[TORCH] {torch.__version__}")
    print(f"[TORCH CUDA] {torch.version.cuda}")
    if not torch.cuda.is_available():
        print("[ERROR] torch.cuda.is_available() is false")
        return 2

    index = torch.cuda.current_device()
    name = torch.cuda.get_device_name(index)
    cc = torch.cuda.get_device_capability(index)
    memory = torch.cuda.get_device_properties(index).total_memory / (1024 ** 3)
    print(f"[GPU] {name}")
    print(f"[GPU CC] {cc[0]}.{cc[1]}")
    print(f"[GPU VRAM] {memory:.1f} GiB")

    try:
        x = torch.ones((1,), device="cuda")
        y = (x + 1).item()
        print(f"[CUDA TEST] tensor add -> {y}")
    except Exception as exc:
        print(f"[ERROR] CUDA tensor test failed: {exc}")
        return 3

    if has_module("flash_attn_interface"):
        backend = "fa3"
    elif has_module("flash_attn"):
        backend = "fa2"
    else:
        backend = "sdpa"
    print(f"[ATTENTION MODULE] {backend}")

    repo = Path(args.repo).resolve()
    if repo.exists():
        sys.path.insert(0, str(repo))
        try:
            from bernini.attention import get_attention_backend

            print(f"[BERNINI ATTENTION] {get_attention_backend()}")
        except Exception as exc:
            print(f"[WARN] Could not import Bernini attention module: {exc}")

    allow_sdpa = os.environ.get("BERNINI_ALLOW_SDPA") == "1"
    if args.require_fast_attention and backend == "sdpa" and not allow_sdpa:
        print("[ERROR] Fast attention is required, but neither FlashAttention-2 nor FlashAttention-3 imported.")
        print("[INFO] Set BERNINI_ALLOW_SDPA=1 only if you intentionally accept the slower SDPA fallback.")
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

