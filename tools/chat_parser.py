#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MSG_LINE_PATTERNS = [
    re.compile(
        r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+(?P<sender>[^:：]{1,40})[:：]\s*(?P<content>.+)$"
    ),
    re.compile(
        r"^\[(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?P<sender>[^:：]{1,40})[:：]\s*(?P<content>.+)$"
    ),
]

EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")
STOPWORDS = {"然后", "就是", "你们", "我们", "今天", "一个", "这个", "那个"}


def parse_txt(path: Path) -> list[dict]:
    messages = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        for pat in MSG_LINE_PATTERNS:
            m = pat.match(line)
            if m:
                messages.append(
                    {
                        "time": m.group("time"),
                        "sender": m.group("sender").strip(),
                        "content": m.group("content").strip(),
                    }
                )
                break
    return messages


def parse_mht(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;|&lt;|&gt;|&amp;", " ", text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    messages = []
    for line in lines:
        for pat in MSG_LINE_PATTERNS:
            m = pat.match(line)
            if m:
                messages.append(
                    {
                        "time": m.group("time"),
                        "sender": m.group("sender").strip(),
                        "content": m.group("content").strip(),
                    }
                )
                break
    return messages


def parse_csv(path: Path) -> list[dict]:
    messages = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sender = row.get("sender") or row.get("from") or row.get("name") or ""
            content = row.get("content") or row.get("text") or row.get("message") or ""
            time = row.get("time") or row.get("timestamp") or row.get("date") or ""
            if sender and content:
                messages.append({"time": str(time), "sender": str(sender), "content": str(content)})
    return messages


def parse_json(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    items = raw if isinstance(raw, list) else raw.get("messages", [])
    messages = []
    for it in items:
        if not isinstance(it, dict):
            continue
        sender = it.get("sender") or it.get("from") or it.get("name") or ""
        content = it.get("content") or it.get("text") or it.get("message") or ""
        time = it.get("time") or it.get("timestamp") or it.get("date") or ""
        if sender and content:
            messages.append({"time": str(time), "sender": str(sender), "content": str(content)})
    return messages


def parse_file(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix in {".json"}:
        return parse_json(path)
    if suffix in {".csv"}:
        return parse_csv(path)
    if suffix in {".mht", ".html", ".htm"}:
        return parse_mht(path)
    return parse_txt(path)


def analyze(messages: list[dict], target: str | None) -> dict:
    sender_counter = Counter(m["sender"] for m in messages)
    target_msgs = [m for m in messages if not target or m["sender"] == target]
    all_text = "\n".join(m["content"] for m in target_msgs)
    emoji_counter = Counter(EMOJI_PATTERN.findall(all_text))
    tokens = [t for t in re.findall(r"[\u4e00-\u9fa5]{2,4}", all_text) if t not in STOPWORDS]
    phrase_counter = Counter(tokens)
    by_hour = defaultdict(int)
    for m in target_msgs:
        hm = re.search(r"\s(\d{1,2}):", m["time"])
        if hm:
            by_hour[int(hm.group(1))] += 1
    emotional_words = ["开心", "难过", "生气", "害怕", "委屈", "喜欢", "讨厌", "想"]
    emotional_hits = {w: all_text.count(w) for w in emotional_words if all_text.count(w) > 0}
    return {
        "type": "chat_analysis",
        "target": target or "",
        "stats": {
            "total_messages": len(messages),
            "target_messages": len(target_msgs),
            "senders": dict(sender_counter.most_common()),
            "active_hours": dict(sorted(by_hour.items())),
        },
        "speech": {
            "top_phrases": [k for k, _ in phrase_counter.most_common(40)],
            "top_emoji": dict(emoji_counter.most_common(20)),
            "emotion_words": emotional_hits,
        },
        "samples": target_msgs[:120],
    }


def main():
    parser = argparse.ArgumentParser(description="解析童年聊天记录（txt/csv/json/mht）")
    parser.add_argument("--file", required=True, help="输入文件")
    parser.add_argument("--target", help="仅分析该发送者")
    parser.add_argument("--output", help="输出 JSON")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"文件不存在: {path}")
    messages = parse_file(path)
    result = analyze(messages, args.target)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已输出 {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
