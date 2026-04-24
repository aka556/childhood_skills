<div align="center">
  <h1>childhood.skill</h1>
  <p><em>"How good it would be to invite my younger self to dinner just one more time."</em></p>
  <p><strong>Every conversation is a return to childhood memory.</strong></p>
  <p>This skill turns your younger self into a runnable dialogue mirror.<br>Not forced nostalgia, not beautifying the past—just a chance for your present self to sit down and talk with who you once were.</p>
  <p>
    <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
    <a href="https://python.org"><img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9+-blue.svg"></a>
    <a href="https://claude.ai/code"><img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-Skill-blueviolet"></a>
    <a href="https://github.com/titanwings/agentskills"><img alt="AgentSkills" src="https://img.shields.io/badge/AgentSkills-Standard-brightgreen"></a>
  </p>
  <p><a href="./README.md">中文</a> · <a href="./README_EN.md">English</a></p>
</div>

---

## Install

### Claude Code

Run in your git repository root:

```bash
mkdir -p .claude/skills
git clone https://github.com/aka556/childhood_skills .claude/skills/create-childhood
```

Or install globally:

```bash
git clone https://github.com/aka556/childhood_skills ~/.claude/skills/create-childhood
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

> Before using management commands, install them once in `/create-childhood`:  
> `install management commands`  
> or run: `python tools/management_skills_installer.py --base-dir ./.claude/skills`

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
- `auto_correction.py`: auto-write "not like this" style corrections
- `management_skills_installer.py`: install `/list-childhoods` and related commands
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
