# user-needs-analyzer

An evidence-based V1.0 skill for traceable user-needs analysis.

## 这是什么

`user-needs-analyzer` 是一个面向用户需求分析的 Skill，用来把访谈、反馈、工单和开放题材料整理成可追溯的需求结论，而不是直接把用户原话改写成功能清单。

## 能解决什么问题

- 帮助分析者区分“用户真正需要什么”和“用户提出希望做什么”
- 帮助把零散反馈整理为结构化证据
- 帮助判断某条候选需求是 `validated`、`conditionally_validated`、`need_hypothesis`、`insufficient_evidence` 还是 `invalid_or_out_of_scope`
- 帮助输出可继续讨论的需求分析结果，而不是直接进入产品排期

## 支持哪些输入材料

- 用户访谈纪要和原话
- 用户反馈与功能建议
- 客服工单和服务相关反馈
- 问卷开放题
- 带有稳定 source ID 的混合定性材料

## 输出什么

- `evidence-table.md`
- `need-card-Nxxx.md`
- `needs-ranking.md`
- `final-report.md`

## 最简单的使用方式

```text
Please use user-needs-analyzer to analyze the following user feedback,
and follow SKILL.md to output an evidence table, user need cards,
needs ranking, and an analysis report.
```

## V1.0 的能力边界

当前版本可以：
- 基于证据整理和分析用户需求
- 区分需求、解决方案和相邻问题
- 做需求成立性判断和需求侧相对排序

本 Skill 不负责：
- 证明市场规模或商业规模
- 自动决定产品路线图或研发排期
- 直接生成最终功能方案或 PRD
