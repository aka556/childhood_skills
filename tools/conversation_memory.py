#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def _skill_dir(base_dir: str, slug: str) -> Path:
    return Path(base_dir) / slug


def _chat_log_path(base_dir: str, slug: str) -> Path:
    return _skill_dir(base_dir, slug) / "memories" / "chats" / "dialogue.jsonl"


def _append_line(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def action_append(base_dir: str, slug: str, user_text: str, assistant_text: str, source: str):
    now = datetime.now().isoformat()
    record = {
        "at": now,
        "source": source,
        "user": user_text.strip(),
        "assistant": assistant_text.strip(),
    }
    _append_line(_chat_log_path(base_dir, slug), record)
    print(json.dumps({"ok": True, "action": "append", "slug": slug, "at": now}, ensure_ascii=False))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items


def _pick_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"[。！？\n\r]+", text) if p.strip()]
    return [p[:120] for p in parts if len(p) >= 6]


def action_extract(base_dir: str, slug: str, output: str | None):
    data = _read_jsonl(_chat_log_path(base_dir, slug))
    memory_keys = ["小时候", "小学", "初中", "家里", "老师", "同学", "操场", "院子", "小卖部", "害怕", "喜欢", "讨厌"]
    persona_keys = ["我会", "我不会", "我一般", "我习惯", "我说话", "我不爱", "我喜欢", "我讨厌", "会先", "会直接"]
    memory_hits = []
    persona_hits = []
    for rec in data:
        user = str(rec.get("user", ""))
        assistant = str(rec.get("assistant", ""))
        for s in _pick_sentences(user):
            if any(k in s for k in memory_keys):
                memory_hits.append({"at": rec.get("at", ""), "text": s, "from": "user"})
            if any(k in s for k in persona_keys):
                persona_hits.append({"at": rec.get("at", ""), "text": s, "from": "user"})
        for s in _pick_sentences(assistant):
            if any(k in s for k in memory_keys):
                memory_hits.append({"at": rec.get("at", ""), "text": s, "from": "assistant"})
            if any(k in s for k in persona_keys):
                persona_hits.append({"at": rec.get("at", ""), "text": s, "from": "assistant"})

    result = {
        "type": "conversation_extract",
        "slug": slug,
        "source_count": len(data),
        "memory_candidates": memory_hits[:120],
        "persona_candidates": persona_hits[:120],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"已输出 {output}")
    else:
        print(text)


def _append_markdown_section(path: Path, title: str, lines: list[str]):
    origin = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    block = "\n".join(lines).strip()
    if not block:
        return
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    section = f"\n\n<!-- [追加于 {stamp}，来源：对话沉淀] -->\n### {title}\n{block}\n"
    path.write_text(origin + section, encoding="utf-8")


def _bump_meta(base_dir: str, slug: str):
    meta_path = _skill_dir(base_dir, slug) / "meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
    ver = str(meta.get("version", "v1"))
    m = re.match(r"^v(\d+)$", ver)
    if m:
        ver = f"v{int(m.group(1)) + 1}"
    else:
        ver = "v2"
    meta["version"] = ver
    meta["updated_at"] = datetime.now().isoformat()
    meta["conversation_updates"] = int(meta.get("conversation_updates", 0)) + 1
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def action_apply(base_dir: str, slug: str, extract_json: str):
    payload = json.loads(Path(extract_json).read_text(encoding="utf-8", errors="ignore"))
    sk = _skill_dir(base_dir, slug)
    childhood = sk / "childhood.md"
    persona = sk / "persona.md"
    m_lines = [f"- {x.get('text', '')}" for x in payload.get("memory_candidates", [])[:20] if x.get("text")]
    p_lines = [f"- {x.get('text', '')}" for x in payload.get("persona_candidates", [])[:20] if x.get("text")]
    _append_markdown_section(childhood, "对话增量记忆", m_lines)
    _append_markdown_section(persona, "对话增量声口", p_lines)
    _bump_meta(base_dir, slug)
    print(json.dumps({"ok": True, "action": "apply", "slug": slug, "memory_added": len(m_lines), "persona_added": len(p_lines)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="童年对话记忆保存与提炼")
    parser.add_argument("--action", required=True, choices=["append", "extract", "apply"])
    parser.add_argument("--slug", required=True)
    parser.add_argument("--base-dir", default="./.claude/skills")
    parser.add_argument("--user", default="")
    parser.add_argument("--assistant", default="")
    parser.add_argument("--source", default="dialogue")
    parser.add_argument("--output")
    parser.add_argument("--extract-json")
    args = parser.parse_args()

    if args.action == "append":
        action_append(args.base_dir, args.slug, args.user, args.assistant, args.source)
    elif args.action == "extract":
        action_extract(args.base_dir, args.slug, args.output)
    elif args.action == "apply":
        if not args.extract_json:
            raise SystemExit("apply 需要 --extract-json")
        action_apply(args.base_dir, args.slug, args.extract_json)


if __name__ == "__main__":
    main()
