---
name: daily-news
description: 每日新闻聚合 — 5信源自动采集→AI摘要→A4 PDF→邮件推送，定时任务每天10:00执行，覆盖前一日新闻。
---

# 每日新闻聚合 Skill

## 功能

5 个信源全自动采集，DeepSeek AI 生成摘要，输出 A4 PDF 日报，QQ 邮箱自动推送。

| 信源 | 类型 | 数据格式 |
|------|------|---------|
| 学习强国-重要新闻 | 时政 | JSON 数据文件 |
| 中国政府网-要闻 | 政策/时政 | JSON API |
| 华尔街见闻-硬AI | AI | JSON API |
| 华尔街见闻-全球 | 宏观/综合 | JSON API |
| 同花顺-今日要闻 | 财经 | JSON API（截断 20 条） |

所有信源均按指定日期过滤，零 CDP 依赖。

## 自动化

Windows 任务计划程序，任务名 `DailyNews`，每天 **10:00** 执行：

```
run_daily.py
  → fetch_news.py     采集昨日 5 信源新闻
  → generate_summary.py  DeepSeek AI 生成三段落摘要
  → generate_pdf.py    生成 A4 PDF（封面→摘要→目录→正文）
  → send_email.py      发送到 3261436550@qq.com
```

## 手动使用

### 生成今日日报
```bash
cd f:/ai_talks/01/每日新闻 && python generate_pdf.py
```

### 指定日期
```python
from fetch_news import fetch_all
from generate_pdf import build

articles = fetch_all(target_date="2026-06-01")
build(articles, "日报.pdf", date_str="2026-06-01")
```

### 调整输出
- 修改 `generate_pdf.py` 中 `build()` 的 `top_n` 参数控制文章数（默认 150）
- 修改 `fetch_news.py` 中各 `limit` 参数控制 API 返回量

## 文件结构

```
每日新闻/
├── run_daily.py            ← 一键全流程入口（定时任务调用）
├── fetch_news.py           ← 数据采集模块
├── generate_summary.py     ← AI 摘要（DeepSeek API）
├── generate_pdf.py         ← PDF 生成模块
├── send_email.py           ← QQ SMTP 邮件发送
├── SKILL.md                ← 本文件
└── 每日新闻_YYYYMMDD.pdf   ← 输出
```

## 输出格式

- A4 竖版（210×297mm），微软雅黑
- 封面（标题 + 日期 + 五信源列表）→ AI 摘要 → 目录 → 按信源分组正文
- 文章条目：14pt 粗体标题 + 蓝色超链接 URL + 斜体灰色摘要（如有）
- 文章间浅灰分隔线，章节间黑色标题分割线

## 依赖

- Python 3.x
- `fpdf2`, `requests`
- DeepSeek API Key（`generate_summary.py` 中配置）
- QQ 邮箱 SMTP 授权码（`send_email.py` 中配置）
