#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime
from pathlib import Path


TRIGGERS = ["不对", "不是这样的", "我不会这样说", "我小时候不是这样", "不像我", "应该是"]
PERSONA_HINTS = ["说话", "语气", "我会", "我不会", "生气", "害怕", "开心", "反应"]
MEMORY_HINTS = ["小时候", "家里", "老师", "同学", "地点", "那年", "发生", "记得"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def _append_section(path: Path, block: str):
    old = _read(path)
    path.write_text(old + ("\n" if old and not old.endswith("\n") else "") + block + "\n", encoding="utf-8")


def _ensure_skill(slug_dir: Path):
    if not slug_dir.exists():
        raise SystemExit(f"找不到 skill 目录: {slug_dir}")


def _pick_target(text: str) -> str:
    p_score = sum(1 for k in PERSONA_HINTS if k in text)
    m_score = sum(1 for k in MEMORY_HINTS if k in text)
    return "persona" if p_score >= m_score else "childhood"


def _bump_meta(meta_path: Path):
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
    ver = str(meta.get("version", "v1"))
    m = re.match(r"^v(\d+)$", ver)
    if m:
        meta["version"] = f"v{int(m.group(1)) + 1}"
    else:
        meta["version"] = "v2"
    meta["updated_at"] = datetime.now().isoformat()
    meta["corrections_count"] = int(meta.get("corrections_count", 0)) + 1
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_correction(base_dir: str, slug: str, text: str):
    if not any(t in text for t in TRIGGERS):
        print("未检测到纠正触发词，跳过")
        return
    slug_dir = Path(base_dir) / slug
    _ensure_skill(slug_dir)
    target = _pick_target(text)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = (
        f"### Correction 自动记录 — {now}\n"
        f"- 层级：{'Layer 2/3/4' if target == 'persona' else '童年记忆'}\n"
        f"- 用户原话：\"{text.strip()}\"\n"
        f"- 纠正规则：后续回答优先遵循这条用户修正\n"
    )
    target_file = slug_dir / ("persona.md" if target == "persona" else "childhood.md")
    _append_section(target_file, block)
    _bump_meta(slug_dir / "meta.json")
    print(f"已写入纠正：{target_file}")


def main():
    parser = argparse.ArgumentParser(description="自动追加用户纠正到童年 skill")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--base-dir", default="./.claude/skills")
    parser.add_argument("--text", required=True)
    args = parser.parse_args()
    apply_correction(args.base_dir, args.slug, args.text)


if __name__ == "__main__":
    main()
