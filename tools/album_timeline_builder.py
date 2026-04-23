#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _bucket_key(captured_at: str, granularity: str) -> str:
    dt = datetime.fromisoformat(captured_at)
    if granularity == "month":
        return f"{dt.year:04d}-{dt.month:02d}"
    return f"{dt.year:04d}"


def build_timeline(photo_json: dict, granularity: str) -> dict:
    groups = defaultdict(list)
    for item in photo_json.get("items", []):
        captured = item.get("captured_at")
        if not captured:
            continue
        groups[_bucket_key(captured, granularity)].append(item)

    buckets = []
    for key in sorted(groups.keys()):
        photos = sorted(groups[key], key=lambda x: x.get("captured_at", ""))
        tags = defaultdict(int)
        for p in photos:
            for t in p.get("scene_tags", []):
                tags[t] += 1
        buckets.append(
            {
                "bucket": key,
                "count": len(photos),
                "top_scene_tags": dict(sorted(tags.items(), key=lambda kv: kv[1], reverse=True)[:5]),
                "samples": [p.get("filename", "") for p in photos[:8]],
            }
        )
    return {
        "type": "photo_timeline",
        "source": photo_json.get("source", ""),
        "granularity": granularity,
        "total_photos": photo_json.get("total", 0),
        "buckets": buckets,
    }


def render_markdown(timeline: dict) -> str:
    lines = [
        "# 童年相册时间线",
        f"- 来源：{timeline.get('source', '')}",
        f"- 粒度：{timeline.get('granularity', '')}",
        f"- 总照片数：{timeline.get('total_photos', 0)}",
        "",
    ]
    for b in timeline.get("buckets", []):
        lines.append(f"## {b['bucket']}（{b['count']} 张）")
        tags = "、".join([f"{k}x{v}" for k, v in b.get("top_scene_tags", {}).items()]) or "无"
        lines.append(f"- 场景标签：{tags}")
        samples = "、".join([s for s in b.get("samples", []) if s]) or "无"
        lines.append(f"- 示例照片：{samples}")
        lines.append("")
    return "\n".join(lines)


def output_data(timeline: dict, output: str | None, output_format: str):
    if output_format == "md":
        text = render_markdown(timeline)
    else:
        text = json.dumps(timeline, ensure_ascii=False, indent=2)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"已输出 {output}")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(description="从照片分析 JSON 生成相册时间线")
    parser.add_argument("--input", required=True, help="photo_analyzer 输出 JSON")
    parser.add_argument("--output", help="输出文件")
    parser.add_argument("--granularity", choices=["year", "month"], default="year")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()

    photo_json = _read_json(args.input)
    timeline = build_timeline(photo_json, args.granularity)
    output_data(timeline, args.output, args.format)


if __name__ == "__main__":
    main()
