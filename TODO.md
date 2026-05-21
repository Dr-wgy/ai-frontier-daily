# AI Frontier Daily TODO

## 已完成

- [x] 1. ingested.jsonl 中「点击查看原文>」需要进行处理（InfoQ）— 针对性处理
- [x] 2. ingest from 极客公园 请求严重延迟问题 — 源异常剔除
- [x] 3. ingest from infoq 中文 SSL 异常 — 关闭 SSL 认证
- [x] 4. bugfix — 表现：部分新闻的「白话&影响」为空
- [x] 5. 迭代：影响数量 1～2 条
- [x] 6. 调整内容模块结构（信息块 → 今日速览 → 各模块正文）
- [x] 7. 新闻内容重复问题处理（当日、跨天）
    - ✅ prompts 文件命名：filter_ranker.j2.md, summarizer.j2.md
    - ✅ 日志统一：work_module.py 的 log 方法替代各模块的日志实现
- [x] 8. 调研 workflow，并实施落地优化

## 待处理

（暂无）
