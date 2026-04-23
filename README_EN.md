# childhood.skill

> _"How good it would be to invite my younger self to dinner just one more time."_

**Every conversation is a return to childhood memory.**

This skill turns your younger self into a runnable dialogue mirror.  
Not forced nostalgia, not beautifying the past—just a chance for your present self to sit down and talk with who you once were.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-brightgreen)](https://github.com/titanwings/agentskills)

[中文](./README.md) · [English](./README_EN.md)

---

## Install

### Claude Code

Run in your git repository root:

```bash
mkdir -p .claude/skills
git clone https://github.com/yourname/childhood_skills .claude/skills/create-childhood
```

Or install globally:

```bash
git clone https://github.com/yourname/childhood_skills ~/.claude/skills/create-childhood
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

In Claude Code:

```text
/create-childhood
```

After creation:

- `/{slug}`: full childhood dialogue mode
- `/{slug}-childhood`: memory-only mode
- `/{slug}-persona`: voice/persona-only mode

Management commands:

- `list-childhoods`: list all created childhood skills
- `update-childhood {slug}`: append new materials/corrections and regenerate
- `childhood-rollback {slug} {version}`: roll back to a historical version
- `delete-childhood {slug}`: delete a skill and related memory files

---

## Creation Flow

1. Basic intake (3 questions)
2. Import source materials (photos / diaries / chats / narration)
3. Auto parsing (structured evidence extraction)
4. Generate `childhood.md` + `persona.md`
5. Merge into runnable `SKILL.md`
6. Optionally write runtime conversations back to memory

---

## Supported Sources

| Source | Format | Purpose |
|------|------|------|
| Old photos | jpg/png/webp/heic | capture time, scene tags, timeline span |
| Diaries / essays | txt/md | emotion words, keywords, people, timeline |
| Chat logs | txt/csv/json/mht/html | catchphrases, style, active hours |
| Memory texts | txt/md/json | playmate relations and evidence lines |
| Narration | plain text | fill gaps without files |

---

## Output Structure

Each childhood skill has two parts:

- **Part A — Childhood Memory**: time-space context, scenes, highlights, wounds, key people
- **Part B — Persona**: child-like speaking style, emotional responses, behavior patterns

Runtime logic:

`user input -> Persona decides child-like response -> Memory adds concrete context -> output`

---

## Toolchain

The `tools/` directory includes:

- `photo_analyzer.py`: photo metadata and scene tags
- `album_timeline_builder.py`: album timeline generation
- `diary_parser.py`: diary/essay parsing
- `chat_parser.py`: chat log parsing
- `playmate_graph.py`: playmate relation graph
- `memory_merger.py`: multi-source memory merge
- `conversation_memory.py`: save/extract/apply conversation memory
- `skill_writer.py`: skill file creation and merge
- `version_manager.py`: backup and rollback

Conversation write-back example:

```bash
python tools/conversation_memory.py --action append --slug xiao-yu --base-dir ./.claude/skills --user "I was most afraid of power outages as a child." --assistant "You would hide under the blanket." --source runtime
python tools/conversation_memory.py --action extract --slug xiao-yu --base-dir ./.claude/skills --output /tmp/xiao-yu_extract.json
python tools/conversation_memory.py --action apply --slug xiao-yu --base-dir ./.claude/skills --extract-json /tmp/xiao-yu_extract.json
python tools/skill_writer.py --action combine --slug xiao-yu --base-dir ./.claude/skills
```

---

## Project Structure

```text
childhood_skills/
├── SKILL.md
├── README.md
├── README_EN.md
├── requirements.txt
├── prompts/
│   ├── intake.md
│   ├── childhood_analyzer.md
│   ├── childhood_builder.md
│   ├── persona_analyzer.md
│   ├── persona_builder.md
│   ├── merger.md
│   └── correction_handler.md
└── tools/
    ├── photo_analyzer.py
    ├── album_timeline_builder.py
    ├── diary_parser.py
    ├── chat_parser.py
    ├── playmate_graph.py
    ├── memory_merger.py
    ├── conversation_memory.py
    ├── skill_writer.py
    └── version_manager.py
```

---

## Boundaries

1. For personal memory, self-dialogue, and emotional processing only
2. Not for impersonation or privacy violation
3. Childhood can be imperfect; no forced healing narrative
4. All data is processed locally by default

---

## Credits

This project references community memory-oriented skill structures, especially [parents-skills](https://github.com/xiaoheizi8/parents-skills).

---

## License

MIT
