#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


def _load_text_or_json(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    try:
        data = json.loads(raw)
    except Exception:
        return raw
    return json.dumps(data, ensure_ascii=False)


def _extract_names(text: str) -> list[str]:
    cn = re.findall(r"(?:和|跟|找|叫|被|给|同桌|同学|朋友|小伙伴|哥哥|姐姐|弟弟|妹妹)([\u4e00-\u9fa5]{2,4})", text)
    en = re.findall(r"\b([A-Z][a-z]{1,20})\b", text)
    names = [n for n in cn + en if n not in {"我们", "他们", "老师"}]
    return names


def build_graph(paths: list[Path], min_weight: int) -> dict:
    node_counter = Counter()
    edge_counter = Counter()
    evidences = defaultdict(list)

    for path in paths:
        text = _load_text_or_json(path)
        lines = [ln.strip() for ln in re.split(r"[。！？\n\r]+", text) if ln.strip()]
        for line in lines:
            names = _extract_names(line)
            uniq = sorted(set(names))
            if not uniq:
                continue
            node_counter.update(uniq)
            for a, b in combinations(uniq, 2):
                key = (a, b)
                edge_counter[key] += 1
                if len(evidences[key]) < 3:
                    evidences[key].append(line[:120])

    nodes = [{"id": n, "weight": c} for n, c in node_counter.most_common()]
    edges = []
    for (a, b), w in edge_counter.most_common():
        if w < min_weight:
            continue
        edges.append({"source": a, "target": b, "weight": w, "evidence": evidences[(a, b)]})
    top = sorted(nodes, key=lambda x: x["weight"], reverse=True)[:20]
    return {
        "type": "playmate_graph",
        "source_files": [str(p) for p in paths],
        "nodes": nodes,
        "edges": edges,
        "top_companions": top,
    }


def main():
    parser = argparse.ArgumentParser(description="构建童年小伙伴关系图")
    parser.add_argument("--inputs", nargs="+", required=True, help="输入文件列表（txt/md/json）")
    parser.add_argument("--min-weight", type=int, default=2, help="边最小权重")
    parser.add_argument("--output", help="输出 JSON")
    args = parser.parse_args()

    paths = [Path(p) for p in args.inputs]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"文件不存在: {p}")
    graph = build_graph(paths, args.min_weight)
    text = json.dumps(graph, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已输出 {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
