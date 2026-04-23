# 童年.skill

> _"真好，要是能再宴请一次小时候的自己，陪他好好吃顿饭就好了。"_

**每一次的对话，都是一次对儿时的追忆。**

把小时候的自己珍藏成一个可对话的 Skill。  
不是强行怀旧，也不是美化过去，而是给长大后的你一次和当年的自己坐下来聊聊的机会。

License: MIT · Python 3.9+ · Claude Code

---

## 安装

### Claude Code

在 git 仓库根目录执行：

```bash
mkdir -p .claude/skills
git clone https://github.com/yourname/childhood_skills .claude/skills/create-childhood
```

或全局安装：

```bash
git clone https://github.com/yourname/childhood_skills ~/.claude/skills/create-childhood
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 使用

在 Claude Code 中输入：

```text
/create-childhood
```

创建后调用：

- `/{slug}`：完整童年对话模式
- `/{slug}-childhood`：只看童年记忆档案
- `/{slug}-persona`：只看儿童声口与反应模式

管理命令：

- `/list-childhoods`
- `/update-childhood {slug}`
- `/childhood-rollback {slug} {version}`
- `/delete-childhood {slug}`

---

## 创建流程

1. 基础信息录入（3 问）
2. 导入原材料（照片 / 日记 / 聊天 / 口述）
3. 自动解析（工具链提取结构化证据）
4. 生成 `childhood.md` + `persona.md`
5. 合并输出可运行 `SKILL.md`

---

## 数据源支持

| 来源 | 格式 | 作用 |
|------|------|------|
| 老照片 | jpg/png/webp/heic | 提取拍摄时间、场景标签、时间跨度 |
| 日记/作文 | txt/md | 提取情绪词、关键词、关键人物、时间线 |
| 聊天记录 | txt/csv/json/mht/html | 提取口头禅、表达风格、活跃时段 |
| 记忆文本 | txt/md/json | 提取玩伴关系与证据句 |
| 口述 | 纯文本 | 补齐无文件场景 |

---

## 生成结构

每个童年 Skill 由两部分组成：

- **Part A — Childhood Memory**：童年时空、场景、高光、脆弱、重要他人
- **Part B — Persona**：儿童化语言风格、情绪反应、行为模式

运行逻辑：

`收到用户输入 → Persona 决定小时候会怎么回应 → Memory 补充具体场景细节 → 输出对话`

---

## 工具链

`tools/` 目录包含：

- `photo_analyzer.py`：照片元数据与场景标签
- `album_timeline_builder.py`：相册时间线
- `diary_parser.py`：日记/作文解析
- `chat_parser.py`：聊天记录解析
- `playmate_graph.py`：小伙伴关系图
- `memory_merger.py`：多源素材合并
- `skill_writer.py`：Skill 文件创建与合并
- `version_manager.py`：版本备份与回滚

---

## 项目结构

```text
childhood_skills/
├── SKILL.md
├── README.md
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
    ├── skill_writer.py
    └── version_manager.py
```

---

## 边界说明

1. 只用于个人回忆、自我对话与情绪整理
2. 不用于冒充真人或侵犯隐私
3. 允许童年不完美，不强行治愈叙事
4. 所有素材默认本地处理

---

## 致谢

项目形态参考了社区记忆重构类 Skill 的结构设计，尤其是 [parents-skills](https://github.com/xiaoheizi8/parents-skills)。

---

## License

MIT
