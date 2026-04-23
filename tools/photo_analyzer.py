#!/usr/bin/env python3
import argparse
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
SCENE_HINTS = {
    "操场": ["操场", "playground", "track", "运动场"],
    "教室": ["教室", "classroom", "课桌", "黑板"],
    "家里": ["家", "home", "卧室", "客厅", "院子"],
    "小卖部": ["小卖部", "store", "shop", "便利店"],
    "公园": ["公园", "park"],
    "学校": ["学校", "school", "校门", "校服"],
}


def _load_pillow():
    try:
        from PIL import Image, ExifTags  # type: ignore

        return Image, ExifTags
    except Exception:
        return None, None


def _exif_datetime(path: Path) -> str | None:
    Image, ExifTags = _load_pillow()
    if Image is None:
        return None
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return None
            tag_map = {v: k for k, v in ExifTags.TAGS.items()}
            raw = exif.get(tag_map.get("DateTimeOriginal")) or exif.get(tag_map.get("DateTime"))
            if not raw:
                return None
            dt = datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S")
            return dt.isoformat()
    except Exception:
        return None


def _guess_scene(filename: str) -> list[str]:
    low = filename.lower()
    tags = []
    for scene, keys in SCENE_HINTS.items():
        for key in keys:
            if key.lower() in low:
                tags.append(scene)
                break
    return tags


def analyze_photo(path: Path) -> dict:
    captured = _exif_datetime(path)
    if not captured:
        captured = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    return {
        "path": str(path),
        "filename": path.name,
        "captured_at": captured,
        "year": captured[:4],
        "size_kb": int(path.stat().st_size / 1024),
        "scene_tags": _guess_scene(path.name),
    }


def scan_dir(photo_dir: Path, recursive: bool) -> list[dict]:
    iterator = photo_dir.rglob("*") if recursive else photo_dir.glob("*")
    items = []
    for p in iterator:
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            items.append(analyze_photo(p))
    items.sort(key=lambda x: x["captured_at"])
    return items


def summarize(items: list[dict], source: str) -> dict:
    if not items:
        return {
            "source": source,
            "type": "photo_analysis",
            "total": 0,
            "date_range": {"start": "", "end": ""},
            "years": {},
            "scene_tags": {},
            "items": [],
        }
    years = Counter(i["year"] for i in items if i.get("year"))
    scenes = Counter(tag for i in items for tag in i.get("scene_tags", []))
    return {
        "source": source,
        "type": "photo_analysis",
        "total": len(items),
        "date_range": {"start": items[0]["captured_at"], "end": items[-1]["captured_at"]},
        "years": dict(sorted(years.items())),
        "scene_tags": dict(scenes.most_common()),
        "items": items,
    }


def dump_output(data: dict, output: str | None):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"已输出 {output}")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(description="照片元数据与场景标签分析")
    parser.add_argument("--dir", required=True, help="照片目录")
    parser.add_argument("--output", help="输出 JSON 路径")
    parser.add_argument("--recursive", action="store_true", help="递归扫描")
    args = parser.parse_args()

    photo_dir = Path(args.dir)
    if not photo_dir.exists() or not photo_dir.is_dir():
        raise SystemExit(f"目录不存在: {photo_dir}")
    items = scan_dir(photo_dir, args.recursive)
    dump_output(summarize(items, str(photo_dir)), args.output)


if __name__ == "__main__":
    main()
