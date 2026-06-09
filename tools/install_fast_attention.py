import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


FLASH_ATTN_TAG = "v2.8.3"


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None) -> None:
    print("[RUN] " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def cuda_capability() -> tuple[int, int]:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("torch.cuda.is_available() is false")
    return torch.cuda.get_device_capability(torch.cuda.current_device())


def install_fa2() -> None:
    run([sys.executable, "-m", "pip", "install", "flash-attn==2.8.3", "--no-build-isolation"])


def install_fa3(root: Path) -> None:
    build_root = root / "_build"
    source = build_root / "flash-attention"
    build_root.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        run(["git", "clone", "https://github.com/Dao-AILab/flash-attention.git", str(source)])
    run(["git", "fetch", "--tags"], cwd=source)
    run(["git", "checkout", FLASH_ATTN_TAG], cwd=source)

    env = os.environ.copy()
    env.setdefault("MAX_JOBS", str(max(1, (os.cpu_count() or 2) // 2)))
    run([sys.executable, "setup.py", "install"], cwd=source / "hopper", env=env)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if has_module("flash_attn_interface"):
        print("[OK] FlashAttention-3 module is already importable.")
        return 0
    if has_module("flash_attn"):
        print("[OK] FlashAttention-2 module is already importable.")
        return 0

    if os.environ.get("BERNINI_SKIP_FAST_ATTENTION") == "1":
        print("[SKIP] BERNINI_SKIP_FAST_ATTENTION=1")
        return 0

    cc = cuda_capability()
    print(f"[GPU CC] {cc[0]}.{cc[1]}")
    try:
        if cc[0] >= 9:
            if not shutil.which("nvcc"):
                raise RuntimeError("FlashAttention-3 build needs nvcc in PATH.")
            install_fa3(root)
        else:
            install_fa2()
    except Exception as exc:
        print(f"[ERROR] Fast attention install failed: {exc}")
        if os.environ.get("BERNINI_ALLOW_SDPA") == "1":
            print("[WARN] Continuing because BERNINI_ALLOW_SDPA=1.")
            return 0
        return 1

    if has_module("flash_attn_interface") or has_module("flash_attn"):
        print("[OK] Fast attention module is importable.")
        return 0
    print("[ERROR] Fast attention install finished but no module is importable.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

