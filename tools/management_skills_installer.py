#!/usr/bin/env python3
import argparse
from pathlib import Path


LIST_SKILL = """---
name: list-childhoods
description: 列出所有童年 Skill
user-invocable: true
allowed-tools: Bash
---

执行并返回结果：

```bash
python ./.claude/skills/create-childhood/tools/skill_writer.py --action list --base-dir ./.claude/skills
```
"""


UPDATE_SKILL = """---
name: update-childhood
description: 更新一个童年 Skill（追加素材或纠正）
user-invocable: true
allowed-tools: Read, Edit, Bash
---

用户输入格式：`{slug} + 更新内容` 或 `slug: xxx`

步骤：
1. 识别 slug（必填）
2. 读取：
   - `./.claude/skills/{slug}/childhood.md`
   - `./.claude/skills/{slug}/persona.md`
3. 若文本含纠正语气（如“不对”“不是这样的”“我不会这样说”），执行：
```bash
python ./.claude/skills/create-childhood/tools/auto_correction.py --slug {slug} --base-dir ./.claude/skills --text "{用户原话}"
python ./.claude/skills/create-childhood/tools/skill_writer.py --action combine --slug {slug} --base-dir ./.claude/skills
```
4. 否则按增量内容写入对应文件，再 combine。
"""


ROLLBACK_SKILL = """---
name: childhood-rollback
description: 回滚童年 Skill 到历史版本
user-invocable: true
allowed-tools: Bash
---

用户输入格式：`{slug} {version}`

执行：
```bash
python ./.claude/skills/create-childhood/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./.claude/skills
```
"""


DELETE_SKILL = """---
name: delete-childhood
description: 删除童年 Skill
user-invocable: true
allowed-tools: Bash
---

先确认，再执行：
```bash
rm -rf ./.claude/skills/{slug}
```
Windows PowerShell:
```powershell
Remove-Item -Recurse -Force ./.claude/skills/{slug}
```
"""


INSTALL_MAP = {
    "list-childhoods": LIST_SKILL,
    "update-childhood": UPDATE_SKILL,
    "childhood-rollback": ROLLBACK_SKILL,
    "delete-childhood": DELETE_SKILL,
}


def write_skill(base_dir: Path, name: str, content: str):
    skill_dir = base_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    print(f"已安装 /{name} -> {skill_dir / 'SKILL.md'}")


def main():
    parser = argparse.ArgumentParser(description="安装童年 Skill 管理命令")
    parser.add_argument("--base-dir", default="./.claude/skills")
    args = parser.parse_args()
    base_dir = Path(args.base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    for name, content in INSTALL_MAP.items():
        write_skill(base_dir, name, content)


if __name__ == "__main__":
    main()
