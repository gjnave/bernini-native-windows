import argparse
import os
import shutil
import subprocess
import urllib.parse
from pathlib import Path


REVISION = "main"


FILES = [
    {
        "repo": "DeepBeepMeep/Wan2.2",
        "source": "bernini_r_wan2.2_high_quanto_bf16_int8.safetensors",
        "target": "vendor/Wan2GP/ckpts/bernini_r_wan2.2_high_quanto_bf16_int8.safetensors",
        "group": "Bernini high-noise transformer, int8",
    },
    {
        "repo": "DeepBeepMeep/Wan2.2",
        "source": "bernini_r_wan2.2_low_quanto_bf16_int8.safetensors",
        "target": "vendor/Wan2GP/ckpts/bernini_r_wan2.2_low_quanto_bf16_int8.safetensors",
        "group": "Bernini low-noise transformer, int8",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "umt5-xxl/models_t5_umt5-xxl-enc-quanto_int8.safetensors",
        "target": "vendor/Wan2GP/ckpts/umt5-xxl/models_t5_umt5-xxl-enc-quanto_int8.safetensors",
        "group": "Wan UMT5 text encoder, int8",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "umt5-xxl/special_tokens_map.json",
        "target": "vendor/Wan2GP/ckpts/umt5-xxl/special_tokens_map.json",
        "group": "Wan UMT5 tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "umt5-xxl/spiece.model",
        "target": "vendor/Wan2GP/ckpts/umt5-xxl/spiece.model",
        "group": "Wan UMT5 tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "umt5-xxl/tokenizer.json",
        "target": "vendor/Wan2GP/ckpts/umt5-xxl/tokenizer.json",
        "group": "Wan UMT5 tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "umt5-xxl/tokenizer_config.json",
        "target": "vendor/Wan2GP/ckpts/umt5-xxl/tokenizer_config.json",
        "group": "Wan UMT5 tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "Wan2.1_VAE.safetensors",
        "target": "vendor/Wan2GP/ckpts/Wan2.1_VAE.safetensors",
        "group": "Wan VAE",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "Wan2.1_VAE_upscale2x_imageonly_real_v1.safetensors",
        "target": "vendor/Wan2GP/ckpts/Wan2.1_VAE_upscale2x_imageonly_real_v1.safetensors",
        "group": "Wan optional VAE upsampler",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "xlm-roberta-large/models_clip_open-clip-xlm-roberta-large-vit-huge-14-bf16.safetensors",
        "target": "vendor/Wan2GP/ckpts/xlm-roberta-large/models_clip_open-clip-xlm-roberta-large-vit-huge-14-bf16.safetensors",
        "group": "Wan CLIP/reference encoder",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "xlm-roberta-large/sentencepiece.bpe.model",
        "target": "vendor/Wan2GP/ckpts/xlm-roberta-large/sentencepiece.bpe.model",
        "group": "Wan CLIP/reference tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "xlm-roberta-large/special_tokens_map.json",
        "target": "vendor/Wan2GP/ckpts/xlm-roberta-large/special_tokens_map.json",
        "group": "Wan CLIP/reference tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "xlm-roberta-large/tokenizer.json",
        "target": "vendor/Wan2GP/ckpts/xlm-roberta-large/tokenizer.json",
        "group": "Wan CLIP/reference tokenizer",
    },
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": "xlm-roberta-large/tokenizer_config.json",
        "target": "vendor/Wan2GP/ckpts/xlm-roberta-large/tokenizer_config.json",
        "group": "Wan CLIP/reference tokenizer",
    },
]


# Wan2GP checks the shared core bundle during model load, even for a
# text-only Bernini smoke job, so the installer must replicate these too.
WAN21_SHARED_FILES = [
    ("pose/dw-ll_ucoco_384.onnx", "Wan shared pose preprocessor"),
    ("pose/yolox_l.onnx", "Wan shared pose preprocessor"),
    ("scribble/netG_A_latest.pth", "Wan shared scribble preprocessor"),
    ("flow/raft-things.pth", "Wan shared optical-flow preprocessor"),
    ("depth/depth_anything_v2_vitl.pth", "Wan shared depth preprocessor"),
    ("wav2vec/config.json", "Wan shared wav2vec model"),
    ("wav2vec/feature_extractor_config.json", "Wan shared wav2vec model"),
    ("wav2vec/model.safetensors", "Wan shared wav2vec model"),
    ("wav2vec/preprocessor_config.json", "Wan shared wav2vec model"),
    ("wav2vec/special_tokens_map.json", "Wan shared wav2vec model"),
    ("wav2vec/tokenizer_config.json", "Wan shared wav2vec model"),
    ("wav2vec/vocab.json", "Wan shared wav2vec model"),
    ("chinese-wav2vec2-base/config.json", "Wan shared Chinese wav2vec model"),
    ("chinese-wav2vec2-base/pytorch_model.bin", "Wan shared Chinese wav2vec model"),
    ("chinese-wav2vec2-base/preprocessor_config.json", "Wan shared Chinese wav2vec model"),
    ("roformer/model_bs_roformer_ep_317_sdr_12.9755.ckpt", "Wan shared RoFormer audio separator"),
    ("roformer/model_bs_roformer_ep_317_sdr_12.9755.yaml", "Wan shared RoFormer audio separator"),
    ("roformer/download_checks.json", "Wan shared RoFormer audio separator"),
    ("pyannote/pyannote_model_wespeaker-voxceleb-resnet34-LM.bin", "Wan shared speaker model"),
    ("pyannote/pytorch_model_segmentation-3.0.bin", "Wan shared speaker model"),
    ("det_align/detface.pt", "Wan shared face detector"),
    ("rife4.26.pkl", "Wan shared RIFE temporal upsampler"),
    ("mask/sam_vit_h_4b8939_fp16.safetensors", "Wan shared MatAnyone mask model"),
    ("mask/matanyone.safetensors", "Wan shared MatAnyone mask model"),
    ("mask/config.json", "Wan shared MatAnyone mask model"),
]

FILES.extend(
    {
        "repo": "DeepBeepMeep/Wan2.1",
        "source": source,
        "target": f"vendor/Wan2GP/ckpts/{source}",
        "group": group,
    }
    for source, group in WAN21_SHARED_FILES
)


class ReplacePolicy:
    def __init__(self, value: str):
        self.value = value

    def should_download(self, path: Path) -> bool:
        if not path.exists() or path.stat().st_size == 0:
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


def hf_url(repo: str, filename: str) -> str:
    quoted = urllib.parse.quote(filename.replace("\\", "/"), safe="/")
    return f"https://huggingface.co/{repo}/resolve/{REVISION}/{quoted}?download=true"


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


def download(root: Path, replace: str, dry_run: bool) -> None:
    tool = downloader_name()
    if not tool:
        raise RuntimeError("Neither aria2c.exe nor curl.exe was found in PATH")
    print(f"[TOOL] {tool}")
    policy = ReplacePolicy(replace)
    for item in FILES:
        target = root / item["target"]
        url = hf_url(item["repo"], item["source"])
        if dry_run:
            print(f"[PLAN] {item['group']}: {url} -> {target}")
            continue
        if not policy.should_download(target):
            continue
        if target.exists():
            target.unlink()
        run_download(url, target, tool)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Wan2GP Bernini low-VRAM files without hf CLI")
    parser.add_argument("--root", default=".", help="installer repo root")
    parser.add_argument("--replace", choices=["ask", "skip", "replace"], default="ask")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for item in FILES:
            print(f"{item['group']}: https://huggingface.co/{item['repo']}/blob/{REVISION}/{item['source']}")
        return 0

    download(Path(args.root).resolve(), args.replace, args.dry_run)
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
