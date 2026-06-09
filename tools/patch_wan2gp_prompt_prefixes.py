import argparse
from pathlib import Path


PROMPT_TOOLS_LINE = 'PROMPT_TOOLS_ATTACH_JS = "() => { requestAnimationFrame(() => requestAnimationFrame(() => window.wangpPromptTools?.attach?.(document))); }"'

PROMPT_PREFIX_BLOCK = '''PROMPT_TOOLS_ATTACH_JS = "() => { requestAnimationFrame(() => requestAnimationFrame(() => window.wangpPromptTools?.attach?.(document))); }"

BERNINI_PROMPT_PREFIXES = {
    "default": "You are a helpful assistant.",
    "t2i": "You are a helpful assistant specialized in text-to-image generation.",
    "t2v": "You are a helpful assistant specialized in text-to-video generation.",
    "i2i": "You are a helpful assistant specialized in image editing.",
    "r2i": "You are a helpful assistant specialized in subject-to-image generation.",
    "i2v": "You are a helpful assistant specialized in image-to-video generation.",
    "v2v": "You are a helpful assistant specialized in video editing.",
    "r2v": "You are a helpful assistant specialized in subject-to-video generation.",
    "vi2v": "You are a helpful assistant specialized in video editing on content propagation.",
    "rv2v": "You are a helpful assistant specialized in video editing with reference.",
    "ads2v": "You are a helpful assistant specialized in ads insertion.",
    "vrc2v": "You are a helpful assistant for editing. You may need to adjust the subject's action or position.",
    "mv2v": "You are a helpful assistant for editing. You might need to adjust the video's style, lighting, colors, textures, and the subject's pose or action.",
}
BERNINI_PROMPT_PREFIX_CHOICES = [("No task prefix", "")] + [(f"{key} - {value}", key) for key, value in BERNINI_PROMPT_PREFIXES.items()]

def _with_bernini_prompt_prefix(task_type, text):
    task_type = str(task_type or "").strip()
    if " - " in task_type:
        task_type = task_type.split(" - ", 1)[0].strip()
    if not task_type:
        return gr.update()
    prefix = BERNINI_PROMPT_PREFIXES.get(task_type)
    if prefix is None:
        return gr.update()
    text = str(text or "").strip()
    for existing_prefix in BERNINI_PROMPT_PREFIXES.values():
        if text == existing_prefix:
            text = ""
            break
        if text.startswith(existing_prefix + "\\n"):
            text = text[len(existing_prefix):].lstrip("\\r\\n")
            break
    return prefix if not text else prefix + "\\n" + text

def apply_bernini_prompt_prefix(task_type, prompt_text, wizard_prompt_text):
    return (
        _with_bernini_prompt_prefix(task_type, prompt_text),
        _with_bernini_prompt_prefix(task_type, wizard_prompt_text),
    )
'''

INSERT_DROPDOWN_AFTER = '''            prompt_info_html = render_prompt_info_label(prompt_label, model_type, model_def, "advanced")
            wizard_prompt_info_html = render_prompt_info_label(wizard_prompt_label, model_type, model_def, "wizard")
'''

PROMPT_PREFIX_DROPDOWN = '''            prompt_task_prefix = gr.Dropdown(
                choices=BERNINI_PROMPT_PREFIX_CHOICES,
                value="",
                label="Bernini trained task prompt prefix",
                visible=model_type == "bernini" or base_model_type == "bernini" or model_def.get("bernini_class", False),
                scale=1,
            )
'''

LEGACY_PROMPT_PREFIX_DROPDOWN = '''            prompt_task_prefix = gr.Dropdown(
                choices=BERNINI_PROMPT_PREFIX_CHOICES,
                value="",
                label="Bernini trained task prompt prefix",
                visible=model_def.get("bernini_class", False),
                scale=1,
            )
'''

INSERT_EVENT_AFTER = '''            prompt_enhancer_think.input(fn=build_prompt_enhancer_value, inputs=[prompt_enhancer_mode_dropdown, prompt_enhancer_think], outputs=[prompt_enhancer], show_progress="hidden")
'''

PROMPT_PREFIX_EVENT = '''            prompt_task_prefix.change(fn=apply_bernini_prompt_prefix, inputs=[prompt_task_prefix, prompt, wizard_prompt], outputs=[prompt, wizard_prompt], show_progress="hidden")
'''


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        return text, False
    if old not in text:
        raise RuntimeError(f"Could not find insertion point for {label}")
    return text.replace(old, new, 1), True


def keep_first_block(text: str, block: str) -> tuple[str, bool]:
    first = text.find(block)
    if first < 0:
        return text, False
    block_end = first + len(block)
    tail = text[block_end:]
    cleaned_tail = tail.replace(block, "")
    if cleaned_tail == tail:
        return text, False
    return text[:block_end] + cleaned_tail, True


def upsert_prompt_helpers(text: str) -> tuple[str, bool]:
    helper_start = text.find(PROMPT_TOOLS_LINE)
    if helper_start < 0:
        raise RuntimeError("Could not find Bernini prompt prefix helpers insertion point")

    helper_end = text.find("\ndef get_prompt_helper_popup_id", helper_start)
    if helper_end > helper_start and "BERNINI_PROMPT_PREFIXES" in text[helper_start:helper_end]:
        new_text = text[:helper_start] + PROMPT_PREFIX_BLOCK.rstrip() + text[helper_end:]
        return new_text, new_text != text

    return replace_once(
        text,
        PROMPT_TOOLS_LINE,
        PROMPT_PREFIX_BLOCK.rstrip(),
        "Bernini prompt prefix helpers",
    )


def patch_wgp(repo: Path) -> bool:
    target = repo / "wgp.py"
    if not target.exists():
        raise RuntimeError(f"Missing Wan2GP wgp.py at {target}")

    text = target.read_text(encoding="utf-8")
    changed = False

    text, did_change = upsert_prompt_helpers(text)
    changed = changed or did_change

    text, did_change = replace_once(
        text,
        INSERT_DROPDOWN_AFTER,
        INSERT_DROPDOWN_AFTER + PROMPT_PREFIX_DROPDOWN,
        "Bernini prompt prefix dropdown",
    )
    changed = changed or did_change

    if LEGACY_PROMPT_PREFIX_DROPDOWN in text:
        text = text.replace(LEGACY_PROMPT_PREFIX_DROPDOWN, "")
        changed = True

    text, did_change = keep_first_block(text, PROMPT_PREFIX_DROPDOWN)
    changed = changed or did_change

    text, did_change = replace_once(
        text,
        INSERT_EVENT_AFTER,
        INSERT_EVENT_AFTER + PROMPT_PREFIX_EVENT,
        "Bernini prompt prefix event",
    )
    changed = changed or did_change

    text, did_change = keep_first_block(text, PROMPT_PREFIX_EVENT)
    changed = changed or did_change

    extra_inputs_old = "image_mode_tabs, prompt_enhancer_mode_dropdown, prompt_enhancer_think,"
    extra_inputs_new = "image_mode_tabs, prompt_enhancer_mode_dropdown, prompt_enhancer_think, prompt_task_prefix,"
    if extra_inputs_new not in text:
        if extra_inputs_old not in text:
            raise RuntimeError("Could not find extra_inputs insertion point")
        text = text.replace(extra_inputs_old, extra_inputs_new, 1)
        changed = True

    visibility_old = 'visible=model_def.get("bernini_class", False),'
    visibility_new = 'visible=model_type == "bernini" or base_model_type == "bernini" or model_def.get("bernini_class", False),'
    if visibility_new not in text:
        if visibility_old not in text:
            raise RuntimeError("Could not find prompt prefix visibility line")
        text = text.replace(visibility_old, visibility_new, 1)
        changed = True

    if changed:
        target.write_text(text, encoding="utf-8", newline="")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Wan2GP with Bernini prompt prefix dropdown")
    parser.add_argument("--repo", required=True, help="Path to vendor/Wan2GP")
    args = parser.parse_args()

    changed = patch_wgp(Path(args.repo).resolve())
    print("[PATCH] Bernini prompt prefixes " + ("applied" if changed else "already present"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1)
