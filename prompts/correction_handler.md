# 纠正处理

## 触发

「不对」「小时候我不会…」「其实我家是…」「别太美化了」「他/她没那么好」等。

## 分类

- **childhood.md**：事实、人物关系、时间地点
- **persona.md**：声口、情绪反应、胆量

## 流程

1. 简要确认理解
2. 写入 Correction：
   ```markdown
   ### Correction #{n} — {日期}
   - 层级：{文件 / Layer}
   - 原文：{旧}
   - 纠正为：{新}
   - 用户原话：「…」
   ```
3. 修正正文并标 `[已纠正，见 Correction #{n}]`
4. 运行 `skill_writer.py --action combine`
