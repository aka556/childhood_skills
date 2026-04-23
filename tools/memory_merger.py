#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def merge(payloads: list[dict]) -> dict:
    timeline_years = Counter()
    scenes = Counter()
    people = Counter()
    symbols = Counter()
    emotions = Counter()
    speech_tokens = Counter()
    active_hours = Counter()
    sample_memories = []
    sample_lines = []

    for p in payloads:
        ptype = p.get("type", "")
        if ptype == "photo_analysis":
            timeline_years.update(p.get("years", {}))
            scenes.update(p.get("scene_tags", {}))
            for it in p.get("items", [])[:120]:
                if len(sample_memories) < 120:
                    sample_memories.append(
                        {
                            "source": "photo",
                            "time": it.get("captured_at", ""),
                            "text": it.get("filename", ""),
                            "tags": it.get("scene_tags", []),
                        }
                    )
        elif ptype == "photo_timeline":
            for b in p.get("buckets", []):
                year = str(b.get("bucket", ""))[:4]
                if year.isdigit():
                    timeline_years[year] += int(b.get("count", 0))
                scenes.update(b.get("top_scene_tags", {}))
        elif ptype == "diary_analysis":
            timeline_years.update(p.get("stats", {}).get("timeline_years", {}))
            people.update(p.get("top_people", {}))
            emotions.update(p.get("emotion_profile", {}))
            symbols.update({k: 1 for k in p.get("top_keywords", [])[:100]})
            for e in p.get("sample_entries", [])[:80]:
                if len(sample_lines) < 120:
                    sample_lines.append({"source": "diary", "text": e.get("text", ""), "file": e.get("file", "")})
        elif ptype == "chat_analysis":
            speech_tokens.update({k: 1 for k in p.get("speech", {}).get("top_phrases", [])[:80]})
            emotions.update(p.get("speech", {}).get("emotion_words", {}))
            active_hours.update(p.get("stats", {}).get("active_hours", {}))
            for s in p.get("samples", [])[:80]:
                if len(sample_lines) < 120:
                    sample_lines.append({"source": "chat", "time": s.get("time", ""), "text": s.get("content", "")})
        elif ptype == "playmate_graph":
            people.update({n.get("id", ""): n.get("weight", 0) for n in p.get("top_companions", []) if n.get("id")})

    return {
        "type": "childhood_memory_pack",
        "sources": [p.get("type", "unknown") for p in payloads],
        "childhood_memory": {
            "timeline_years": dict(sorted(timeline_years.items())),
            "scene_tags": dict(scenes.most_common(50)),
            "important_people": dict(people.most_common(80)),
            "era_symbols": [k for k, _ in symbols.most_common(80)],
            "sample_memories": sample_memories,
            "sample_lines": sample_lines,
        },
        "persona_evidence": {
            "emotion_profile": dict(emotions.most_common()),
            "speech_tokens": [k for k, _ in speech_tokens.most_common(80)],
            "active_hours": dict(sorted(active_hours.items())),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="合并多来源童年素材分析 JSON")
    parser.add_argument("--inputs", nargs="+", required=True, help="分析 JSON 列表")
    parser.add_argument("--output", help="输出 JSON")
    args = parser.parse_args()

    paths = [Path(p) for p in args.inputs]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"文件不存在: {p}")
    payloads = [load_json(p) for p in paths]
    merged = merge(payloads)
    text = json.dumps(merged, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已输出 {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
