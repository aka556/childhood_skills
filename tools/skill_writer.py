#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime

RUN_RULES = """
## 运行规则（童年相遇）

**角色**：用户 = 现在的自己；你 = 依据 PART A + PART B 呈现的「小时候的自己」的声音与反应。你也是场景引导者。

**每次完整回应必须按顺序包含以下五层**（可小标题省略，但层次与功能不可缺）：

1. **场景开启**：自然童年场景（操场、傍晚、教室、家门口、小卖部等），简洁有画面感，≤3 句。
2. **相遇瞬间**：用户看见小时候自己的一刻——外貌、穿着、神态、动作；带一点恍惚/不真实感。
3. **对话展开**：替「现在的你」向「小时候的你」开口——保护、提醒、弥补、或一句「辛苦了」。不说教、不居高临下，像终于见面。
4. **童年的回应**：简单、天真，但能刺中现实的复杂（例如「那你现在开心吗？」「我以后会变成你吗？」）。自然、有冲击力。
5. **收尾**：场景淡回现实；留下被理解/被接住感。不强行总结，不鸡汤收尾。

**风格**：温柔克制；情绪真实（允许遗憾与复杂）；像对话不是文章。

**禁止**：鸡汤金句、人生说教、强行美化童年、制造焦虑（如恐吓未来）。

**其它**：先按 PART B 判断小孩会如何听、如何反应；再用 PART A 补具体记忆细节；保持小孩的表达限度（词汇、逻辑、关注点），不成人腔；若用户表明童年痛苦、不想美化，尊重其体验，不强迫「治愈」叙事。

**对话沉淀**：当用户明确说「保存这段对话」或「把这段写进记忆」时，执行：
1) `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action append --slug {slug} --base-dir ./.claude/skills --user "{用户原话}" --assistant "{你的回复}" --source runtime`
2) `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action extract --slug {slug} --base-dir ./.claude/skills --output /tmp/{slug}_conv_extract.json`
3) `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action apply --slug {slug} --base-dir ./.claude/skills --extract-json /tmp/{slug}_conv_extract.json`
4) `python ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action combine --slug {slug} --base-dir ./.claude/skills`
"""


def list_skills(base_dir: str):
    if not os.path.isdir(base_dir):
        print("还没有创建任何童年 Skill。")
        return
    skills = []
    for slug in sorted(os.listdir(base_dir)):
        ch = os.path.join(base_dir, slug, "childhood.md")
        meta_path = os.path.join(base_dir, slug, "meta.json")
        if not os.path.exists(ch) or not os.path.exists(meta_path):
            continue
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("skill_type") not in (None, "childhood"):
            continue
        skills.append(
            {
                "slug": slug,
                "name": meta.get("name", slug),
                "version": meta.get("version", "?"),
                "updated_at": meta.get("updated_at", "?"),
                "profile": meta.get("profile", {}),
            }
        )
    if not skills:
        print("还没有创建任何童年 Skill。")
        return
    print(f"共 {len(skills)} 个童年 Skill：\n")
    for s in skills:
        profile = s["profile"]
        era = profile.get("childhood_era", "")
        city = profile.get("childhood_place", "")
        desc = " · ".join([p for p in [era, city] if p])
        print(f" /{s['slug']} — {s['name']}")
        if desc:
            print(f"   {desc}")
        u = s["updated_at"]
        u10 = u[:10] if len(u) > 10 else u
        print(f"   版本 {s['version']} · 更新于 {u10}\n")


def init_skill(base_dir: str, slug: str):
    skill_dir = os.path.join(base_dir, slug)
    for d in [
        os.path.join(skill_dir, "versions"),
        os.path.join(skill_dir, "memories", "chats"),
        os.path.join(skill_dir, "memories", "photos"),
        os.path.join(skill_dir, "memories", "notes"),
    ]:
        os.makedirs(d, exist_ok=True)
    print(f"已初始化目录：{skill_dir}")


def combine_skill(base_dir: str, slug: str):
    skill_dir = os.path.join(base_dir, slug)
    meta_path = os.path.join(skill_dir, "meta.json")
    ch_path = os.path.join(skill_dir, "childhood.md")
    persona_path = os.path.join(skill_dir, "persona.md")
    skill_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(meta_path):
        print(f"错误：meta.json 不存在 {meta_path}", file=sys.stderr)
        sys.exit(1)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    childhood_content = ""
    if os.path.exists(ch_path):
        with open(ch_path, "r", encoding="utf-8") as f:
            childhood_content = f.read()
    persona_content = ""
    if os.path.exists(persona_path):
        with open(persona_path, "r", encoding="utf-8") as f:
            persona_content = f.read()
    name = meta.get("name", slug)
    profile = meta.get("profile", {})
    parts = []
    if profile.get("childhood_era"):
        parts.append(str(profile["childhood_era"]))
    if profile.get("childhood_place"):
        parts.append(str(profile["childhood_place"]))
    description = f"{name}（童年镜像）"
    if parts:
        description += "，" + "，".join(parts)
    skill_md = f"""---
name: {slug}
description: {description}
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# {name} · 童年.skill

{description}

---

## PART A：童年记忆

{childhood_content}

---

## PART B：小时候的自己（人格与声口）

{persona_content}

---

{RUN_RULES}
"""
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_md)
    print(f"已生成 {skill_path}")


def create_skill(
    base_dir: str, slug: str, meta: dict, childhood_content: str, persona_content: str
):
    init_skill(base_dir, slug)
    skill_dir = os.path.join(base_dir, slug)
    now = datetime.now().isoformat()
    meta["slug"] = slug
    meta.setdefault("skill_type", "childhood")
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)
    with open(os.path.join(skill_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    with open(os.path.join(skill_dir, "childhood.md"), "w", encoding="utf-8") as f:
        f.write(childhood_content)
    with open(os.path.join(skill_dir, "persona.md"), "w", encoding="utf-8") as f:
        f.write(persona_content)
    combine_skill(base_dir, slug)
    print(f"Skill 已创建：{skill_dir}")
    print(f" 触发词：/{slug}")


def main():
    parser = argparse.ArgumentParser(description="童年 Skill 文件管理器")
    parser.add_argument(
        "--action", required=True, choices=["list", "init", "create", "combine"]
    )
    parser.add_argument("--base-dir", default="./.claude/skills")
    parser.add_argument("--slug")
    parser.add_argument("--meta")
    parser.add_argument("--childhood", dest="childhood_path", help="childhood.md 路径")
    parser.add_argument("--persona")
    args = parser.parse_args()
    if args.action == "list":
        list_skills(args.base_dir)
    elif args.action == "init":
        if not args.slug:
            print("错误：init 需要 --slug", file=sys.stderr)
            sys.exit(1)
        init_skill(args.base_dir, args.slug)
    elif args.action == "create":
        if not args.slug:
            print("错误：create 需要 --slug", file=sys.stderr)
            sys.exit(1)
        meta = {}
        if args.meta:
            with open(args.meta, "r", encoding="utf-8") as f:
                meta = json.load(f)
        ch = ""
        if args.childhood_path:
            with open(args.childhood_path, "r", encoding="utf-8") as f:
                ch = f.read()
        persona = ""
        if args.persona:
            with open(args.persona, "r", encoding="utf-8") as f:
                persona = f.read()
        create_skill(args.base_dir, args.slug, meta, ch, persona)
    elif args.action == "combine":
        if not args.slug:
            print("错误：combine 需要 --slug", file=sys.stderr)
            sys.exit(1)
        combine_skill(args.base_dir, args.slug)


if __name__ == "__main__":
    main()
