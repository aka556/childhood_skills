#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

EMOTION_LEXICON = {
    "joy": ["开心", "高兴", "快乐", "兴奋", "喜欢", "幸福"],
    "sad": ["难过", "伤心", "委屈", "想哭", "孤独", "失落"],
    "fear": ["害怕", "紧张", "担心", "怕", "不敢"],
    "anger": ["生气", "气死", "烦", "讨厌", "火大"],
}

STOPWORDS = {"今天", "我们", "他们", "你们", "然后", "就是", "因为", "所以", "一个", "这个", "那个"}


def _iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files = []
    for p in path.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            files.append(p)
    return sorted(files)


def _extract_dates(text: str) -> list[str]:
    patterns = [
        r"\b(19|20)\d{2}[-/.年]\d{1,2}[-/.月]\d{1,2}(?:日)?\b",
        r"\b(19|20)\d{2}年\d{1,2}月\b",
    ]
    dates = []
    for pat in patterns:
        dates.extend(m.group(0) for m in re.finditer(pat, text))
    return dates


def _extract_people(text: str) -> list[str]:
    cn_names = re.findall(r"(?:和|跟|找|叫|被|给)([\u4e00-\u9fa5]{2,4})", text)
    en_names = re.findall(r"\b([A-Z][a-z]{1,20})\b", text)
    people = [n for n in cn_names + en_names if n not in STOPWORDS]
    return people


def _extract_keywords(text: str) -> list[str]:
    tokens = re.findall(r"[\u4e00-\u9fa5]{2,4}", text)
    filtered = [t for t in tokens if t not in STOPWORDS]
    return filtered


def _emotion_score(text: str) -> dict:
    score = {}
    for key, words in EMOTION_LEXICON.items():
        score[key] = sum(text.count(w) for w in words)
    return score


def parse_files(files: list[Path]) -> dict:
    keyword_counter = Counter()
    people_counter = Counter()
    emotion_counter = Counter()
    dates = []
    entries = []
    for file in files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        score = _emotion_score(text)
        dates.extend(_extract_dates(text))
        people_counter.update(_extract_people(text))
        keyword_counter.update(_extract_keywords(text))
        emotion_counter.update(score)
        segments = [s.strip() for s in re.split(r"\n{2,}", text) if s.strip()]
        for seg in segments[:20]:
            if len(seg) > 12:
                entries.append({"file": str(file), "text": seg[:280]})
    top_emotions = dict(sorted(emotion_counter.items(), key=lambda kv: kv[1], reverse=True))
    timeline = defaultdict(int)
    for d in dates:
        year = re.search(r"(19|20)\d{2}", d)
        if year:
            timeline[year.group(0)] += 1
    return {
        "type": "diary_analysis",
        "files": [str(f) for f in files],
        "stats": {
            "file_count": len(files),
            "entry_count": len(entries),
            "timeline_years": dict(sorted(timeline.items())),
        },
        "top_keywords": [k for k, _ in keyword_counter.most_common(50)],
        "top_people": dict(people_counter.most_common(30)),
        "emotion_profile": top_emotions,
        "sample_entries": entries[:80],
    }


def main():
    parser = argparse.ArgumentParser(description="解析童年日记/作文文本")
    parser.add_argument("--input", required=True, help="文件或目录")
    parser.add_argument("--output", help="输出 JSON")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f"路径不存在: {src}")
    files = _iter_files(src)
    result = parse_files(files)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已输出 {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
