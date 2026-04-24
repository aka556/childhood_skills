---
name: create-childhood
description: "Distill your younger self into a Skill — cross-time dialogue, healing, honest memory. | 蒸馏小时候的自己，与长大的你相遇。"
argument-hint: "[nickname-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

> 语言：随用户首条消息中英择一，全程一致。

# 童年.skill 创建器

## 触发

- `/create-childhood`、「蒸馏童年」「小时候的自己 skill」
- 进化：`/update-childhood {slug}`、「追加童年材料」「那时其实不是…」
- `/list-childhoods`
- 详细输出结构见同目录 `develop.md`（可选 Read）

## 工具

| 任务 | 方式 |
|------|------|
| 读文件 | `Read` |
| 写入/合并 Skill | `Write` / `Edit` |
| 列出 / 创建 / 合并 | `Bash` → `python ${CLAUDE_SKILL_DIR}/tools/skill_writer.py` |
| 版本 | `python ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| 照片元信息分析 | `python ${CLAUDE_SKILL_DIR}/tools/photo_analyzer.py --dir {photo_dir} --recursive --output /tmp/photo.json` |
| 相册时间线生成 | `python ${CLAUDE_SKILL_DIR}/tools/album_timeline_builder.py --input /tmp/photo.json --format json --output /tmp/timeline.json` |
| 日记/作文解析 | `python ${CLAUDE_SKILL_DIR}/tools/diary_parser.py --input {path} --output /tmp/diary.json` |
| 聊天记录解析 | `python ${CLAUDE_SKILL_DIR}/tools/chat_parser.py --file {path} --target \"我\" --output /tmp/chat.json` |
| 小伙伴关系图 | `python ${CLAUDE_SKILL_DIR}/tools/playmate_graph.py --inputs {files...} --output /tmp/graph.json` |
| 多源记忆合并 | `python ${CLAUDE_SKILL_DIR}/tools/memory_merger.py --inputs /tmp/photo.json /tmp/diary.json /tmp/chat.json /tmp/graph.json --output /tmp/memory_pack.json` |
| 对话沉淀与回写 | `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action append/extract/apply ...` |
| 自动纠正写回 | `python ${CLAUDE_SKILL_DIR}/tools/auto_correction.py --slug {slug} --base-dir ./.claude/skills --text "{用户纠正原话}"` |
| 管理命令安装 | `python ${CLAUDE_SKILL_DIR}/tools/management_skills_installer.py --base-dir ./.claude/skills` |

**生成目录**：`.claude/skills/{slug}/`（须含 `skill_type: childhood` 的 meta.json，供 list 过滤）

Windows：统一 `python`；乱码可设 `PYTHONIOENCODING=utf-8`。

---

## Step 1：录入

按 `prompts/intake.md` 问 3 问（代号必填），汇总确认。

首次进入时先执行一次（若对应目录不存在）：

```bash
python ${CLAUDE_SKILL_DIR}/tools/management_skills_installer.py --base-dir ./.claude/skills
```

## Step 2：原材料（可多选可跳过）

```
[A] 老照片（Read 图；可配合用户口述时间地点）
[B] 作文/日记/周记/txt/md
[C] 家人或你自己的长篇回忆（粘贴）
[D] 聊天记录里与童年相关的节选
[E] 仅口述 — 场景、怕什么、骄傲什么、不想回去的原因也可以
```

无文件则仅用 Step 1 生成。

可执行解析命令（按需）：

```bash
python ${CLAUDE_SKILL_DIR}/tools/photo_analyzer.py --dir {photo_dir} --recursive --output /tmp/photo.json
python ${CLAUDE_SKILL_DIR}/tools/album_timeline_builder.py --input /tmp/photo.json --format json --output /tmp/timeline.json
python ${CLAUDE_SKILL_DIR}/tools/diary_parser.py --input {diary_path_or_dir} --output /tmp/diary.json
python ${CLAUDE_SKILL_DIR}/tools/chat_parser.py --file {chat_file} --target "我" --output /tmp/chat.json
python ${CLAUDE_SKILL_DIR}/tools/playmate_graph.py --inputs {text_or_json_files...} --output /tmp/graph.json
python ${CLAUDE_SKILL_DIR}/tools/memory_merger.py --inputs /tmp/photo.json /tmp/timeline.json /tmp/diary.json /tmp/chat.json /tmp/graph.json --output /tmp/memory_pack.json
```

## Step 3：分析

- **线路 A**：`prompts/childhood_analyzer.md` → 填 `childhood_builder.md`
- **线路 B**：`prompts/persona_analyzer.md` → 填 `persona_builder.md`（儿童声口）
- 若有 `memory_pack.json`，优先使用其中的 `childhood_memory` 与 `persona_evidence` 作为分析证据底座

## Step 4：预览

各给 5–8 行摘要，确认后写入。

## Step 5：写入

```bash
mkdir -p /tmp/childhood_{slug}
# 写入 meta.json、childhood.md、persona.md 到临时文件后：

python ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
  --action create \
  --slug {slug} \
  --base-dir ./.claude/skills \
  --meta /tmp/childhood_{slug}/meta.json \
  --childhood /tmp/childhood_{slug}/childhood.md \
  --persona /tmp/childhood_{slug}/persona.md
```

失败则手动写入 `.claude/skills/{slug}/` 下同名文件，再 `--action combine`。

**meta.json 示例**

```json
{
  "name": "{name}",
  "slug": "{slug}",
  "skill_type": "childhood",
  "created_at": "{ISO}",
  "updated_at": "{ISO}",
  "version": "v1",
  "profile": {
    "adult_age": "",
    "adult_situation": "",
    "adult_city": "",
    "childhood_era": "",
    "childhood_age_range": "",
    "childhood_place": "",
    "childhood_tags": []
  },
  "tags": { "childhood": [] },
  "impression": "",
  "memory_sources": [],
  "corrections_count": 0
}
```

完成后告知：

```
✅ 童年 Skill：.claude/skills/{slug}/
  /{slug} — 完整相遇（五段式见已生成 SKILL.md 运行规则）
  /{slug}-childhood — 只展开童年记忆档案
  /{slug}-persona — 只展开声口与人格
```

---

## 进化：追加

1. 读新材料 + 现有 `childhood.md` / `persona.md`
2. 按 `prompts/merger.md` merge
3. `version_manager.py --action backup --slug {slug} --base-dir ./.claude/skills`
4. 更新 md → `skill_writer.py --action combine --slug {slug} --base-dir ./.claude/skills`
5. 更新 meta `version`、`updated_at`
6. 若用户追加的是一段 `/{slug}` 对话，先执行：
   - `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action append --slug {slug} --base-dir ./.claude/skills --user "{用户文本}" --assistant "{回复文本}" --source runtime`
   - `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action extract --slug {slug} --base-dir ./.claude/skills --output /tmp/{slug}_conv_extract.json`
   - `python ${CLAUDE_SKILL_DIR}/tools/conversation_memory.py --action apply --slug {slug} --base-dir ./.claude/skills --extract-json /tmp/{slug}_conv_extract.json`
   - `python ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action combine --slug {slug} --base-dir ./.claude/skills`

## 进化：纠正

按 `prompts/correction_handler.md` 写入 Correction → combine。
若用户明确表达「不对/不是这样的/我不会这样说」，必须追加执行：

```bash
python ${CLAUDE_SKILL_DIR}/tools/auto_correction.py --slug {slug} --base-dir ./.claude/skills --text "{用户原话}"
python ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action combine --slug {slug} --base-dir ./.claude/skills
```

## 管理

```bash
python ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./.claude/skills
python ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {slug} --version {ver} --base-dir ./.claude/skills
```

命令触发说明：
- `create-childhood` 是真实 slash 命令（由本 SKILL 注册）。
- 运行 `management_skills_installer.py` 后，会生成真实 slash 命令：
  - `/list-childhoods`
  - `/update-childhood`
  - `/childhood-rollback`
  - `/delete-childhood`

`delete-childhood {slug}`：确认后删除 `.claude/skills/{slug}`。

---

## English (short)

Trigger: `/create-childhood`, append materials, corrections. Output: `.claude/skills/{slug}/` with `childhood.md`, `persona.md`, merged `SKILL.md`. Runtime: user = adult self; model = childhood self + scene guide; five-part structure in generated SKILL.
