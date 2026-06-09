import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


REVISION = "main"


PROFILES = {
    "official-diffusers": {
        "label": "ByteDance official Diffusers bundle",
        "downloads": [
            {
                "type": "snapshot",
                "repo": "ByteDance/Bernini-R-Diffusers",
                "target": "models/ByteDance/Bernini-R-Diffusers",
            }
        ],
        "mode": "self_contained",
        "config": "models/ByteDance/Bernini-R-Diffusers",
    },
    "neuregex-fp8": {
        "label": "neuregex self-contained FP8 bundle",
        "downloads": [
            {
                "type": "snapshot",
                "repo": "neuregex/Bernini-R-fp8",
                "target": "models/neuregex/Bernini-R-fp8",
            }
        ],
        "mode": "self_contained",
        "config": "models/neuregex/Bernini-R-fp8",
    },
    "kijai-fp8-separate": {
        "label": "Kijai FP8 HIGH/LOW checkpoints plus Wan2.2 base",
        "downloads": [
            {
                "type": "snapshot",
                "repo": "Wan-AI/Wan2.2-T2V-A14B-Diffusers",
                "target": "models/Wan-AI/Wan2.2-T2V-A14B-Diffusers",
            },
            {
                "type": "file",
                "repo": "Kijai/WanVideo_comfy_fp8_scaled",
                "source": "Bernini/Wan22_Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
                "target": "models/Kijai/WanVideo_comfy_fp8_scaled/Bernini/high/Wan22_Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
            },
            {
                "type": "file",
                "repo": "Kijai/WanVideo_comfy_fp8_scaled",
                "source": "Bernini/Wan22_Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
                "target": "models/Kijai/WanVideo_comfy_fp8_scaled/Bernini/low/Wan22_Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
            },
        ],
        "mode": "separate_ckpt",
        "base": "models/Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        "config": "config/bernini_renderer_local",
        "high": "models/Kijai/WanVideo_comfy_fp8_scaled/Bernini/high",
        "low": "models/Kijai/WanVideo_comfy_fp8_scaled/Bernini/low",
    },
    "abiray-fp8-separate": {
        "label": "Abiray FP8 HIGH/LOW checkpoints plus Wan2.2 base",
        "downloads": [
            {
                "type": "snapshot",
                "repo": "Wan-AI/Wan2.2-T2V-A14B-Diffusers",
                "target": "models/Wan-AI/Wan2.2-T2V-A14B-Diffusers",
            },
            {
                "type": "file",
                "repo": "Abiray/Wan22_Bernini_FP8_Scaled",
                "source": "Wan22_Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
                "target": "models/Abiray/Wan22_Bernini_FP8_Scaled/high/Wan22_Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
            },
            {
                "type": "file",
                "repo": "Abiray/Wan22_Bernini_FP8_Scaled",
                "source": "Wan22_Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
                "target": "models/Abiray/Wan22_Bernini_FP8_Scaled/low/Wan22_Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
            },
        ],
        "mode": "separate_ckpt",
        "base": "models/Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        "config": "config/bernini_renderer_local",
        "high": "models/Abiray/Wan22_Bernini_FP8_Scaled/high",
        "low": "models/Abiray/Wan22_Bernini_FP8_Scaled/low",
    },
}


class ReplacePolicy:
    def __init__(self, value: str):
        self.value = value

    def should_download(self, path: Path) -> bool:
        if not path.exists():
            return True
        if path.stat().st_size == 0:
            print(f"[REPLACE] {path} is empty")
            return True
        if self.value == "replace":
            return True
        if self.value == "skip":
            print(f"[SKIP] Existing file: {path}")
            return False

        while True:
            answer = input(f"[EXISTS] {path}\nReplace it? [y]es/[n]o/[a]ll/[s]kip all: ").strip().lower()
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no", ""):
                return False
            if answer in ("a", "all"):
                self.value = "replace"
                return True
            if answer in ("s", "skip"):
                self.value = "skip"
                return False
            print("Please answer y, n, a, or s.")


def hf_url(repo: str, filename: str, revision: str = REVISION) -> str:
    quoted = urllib.parse.quote(filename.replace("\\", "/"), safe="/")
    return f"https://huggingface.co/{repo}/resolve/{revision}/{quoted}?download=true"


def api_url(repo: str, revision: str = REVISION) -> str:
    return f"https://huggingface.co/api/models/{repo}/revision/{revision}"


def read_json_url(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def list_snapshot_files(repo: str, revision: str = REVISION) -> list[str]:
    data = read_json_url(api_url(repo, revision))
    files = [item["rfilename"] for item in data.get("siblings", []) if item.get("rfilename")]
    if not files:
        raise RuntimeError(f"No files found for {repo}@{revision}")
    return files


def downloader_name() -> str:
    return shutil.which("aria2c.exe") or shutil.which("aria2c") or shutil.which("curl.exe") or shutil.which("curl") or ""


def run_download(url: str, target: Path, tool: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if "aria2c" in Path(tool).name.lower():
        cmd = [
            tool,
            "--continue=true",
            "--max-connection-per-server=8",
            "--split=8",
            "--min-split-size=1M",
            "--retry-wait=5",
            "--max-tries=5",
            "--auto-file-renaming=false",
            "--allow-overwrite=true",
            "--dir",
            str(target.parent),
            "--out",
            target.name,
            url,
        ]
        print(f"[GET] {target} (aria2c)")
        subprocess.run(cmd, check=True)
        return

    partial = target.with_name(target.name + ".part")
    cmd = [
        tool,
        "-L",
        "--fail",
        "--retry",
        "5",
        "--retry-delay",
        "5",
        "-C",
        "-",
        "-o",
        str(partial),
        url,
    ]
    print(f"[GET] {target} (curl)")
    subprocess.run(cmd, check=True)
    os.replace(partial, target)


def download_file(repo: str, source: str, target: Path, policy: ReplacePolicy, tool: str) -> None:
    if not policy.should_download(target):
        return
    if target.exists():
        target.unlink()
    run_download(hf_url(repo, source), target, tool)


def download_snapshot(repo: str, target_dir: Path, policy: ReplacePolicy, tool: str) -> None:
    print(f"[LIST] {repo}")
    for filename in list_snapshot_files(repo):
        target = target_dir / Path(filename.replace("/", os.sep))
        download_file(repo, filename, target, policy, tool)


def patch_self_contained_config(config_dir: Path) -> None:
    config_path = config_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data["wan22_base"] = str(config_dir.resolve())
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[PATCH] {config_path} wan22_base -> {data['wan22_base']}")


def write_separate_config(config_dir: Path, base_dir: Path) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "model_type": "bernini_renderer",
        "architectures": ["BerniniRendererModel"],
        "wan22_base": str(base_dir.resolve()),
        "skip_transformer_1": False,
        "skip_transformer_2": False,
        "switch_dit_boundary": 0.875,
        "max_sequence_length": 512,
        "shift": 3.0,
        "use_unipc": True,
        "use_src_id_rotary_emb": True,
    }
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[WRITE] {config_path}")


def rel_for_cmd(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("/", "\\")


def write_profile_cmd(root: Path, name: str, profile: dict) -> None:
    config_dir = root / profile["config"]
    high = root / profile["high"] if profile.get("high") else None
    low = root / profile["low"] if profile.get("low") else None
    out = root / "config" / "model_profile.cmd"
    lines = [
        "@echo off",
        f"set \"BERNINI_MODEL_PROFILE={name}\"",
        f"set \"BERNINI_CONFIG=%BERNINI_ROOT%\\{rel_for_cmd(root, config_dir)}\"",
    ]
    if high and low:
        lines.append(f"set \"BERNINI_HIGH_CKPT=%BERNINI_ROOT%\\{rel_for_cmd(root, high)}\"")
        lines.append(f"set \"BERNINI_LOW_CKPT=%BERNINI_ROOT%\\{rel_for_cmd(root, low)}\"")
    else:
        lines.append("set \"BERNINI_HIGH_CKPT=\"")
        lines.append("set \"BERNINI_LOW_CKPT=\"")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[WRITE] {out}")


def configure(root: Path, name: str) -> None:
    profile = PROFILES[name]
    if profile["mode"] == "self_contained":
        patch_self_contained_config(root / profile["config"])
    elif profile["mode"] == "separate_ckpt":
        write_separate_config(root / profile["config"], root / profile["base"])
    else:
        raise ValueError(f"Unknown profile mode: {profile['mode']}")
    write_profile_cmd(root, name, profile)


def download_profile(root: Path, name: str, replace: str) -> None:
    profile = PROFILES[name]
    tool = downloader_name()
    if not tool:
        raise RuntimeError("Neither aria2c.exe nor curl.exe was found in PATH")
    print(f"[TOOL] {tool}")
    policy = ReplacePolicy(replace)
    for item in profile["downloads"]:
        if item["type"] == "snapshot":
            download_snapshot(item["repo"], root / item["target"], policy, tool)
        elif item["type"] == "file":
            download_file(item["repo"], item["source"], root / item["target"], policy, tool)
        else:
            raise ValueError(f"Unknown download type: {item['type']}")
    configure(root, name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Bernini model profiles without hf CLI")
    parser.add_argument("--root", default=".", help="installer repo root")
    parser.add_argument("--profile", choices=sorted(PROFILES), required=False)
    parser.add_argument("--replace", choices=["ask", "skip", "replace"], default="ask")
    parser.add_argument("--configure-only", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for key, value in PROFILES.items():
            print(f"{key}: {value['label']}")
        return 0
    if not args.profile:
        parser.error("--profile is required unless --list is used")

    root = Path(args.root).resolve()
    if args.configure_only:
        configure(root, args.profile)
    else:
        download_profile(root, args.profile, args.replace)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n[ABORTED] Interrupted by user")
        raise SystemExit(130)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Download command failed with exit code {exc.returncode}")
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1)

