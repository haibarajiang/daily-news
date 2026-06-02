# 每日新闻日报

每天早上 10:00 自动采集 5 个信源的新闻 → DeepSeek AI 生成摘要 → 生成 A4 PDF → 发送到邮箱。

## 快速开始

### 1. 安装依赖

```bash
pip install requests fpdf2
```

### 2. 配置

```bash
cp config.example.py config.py
```

编辑 `config.py`，填入：
- **DeepSeek API Key** — [申请地址](https://platform.deepseek.com/)
- **QQ 邮箱授权码** — QQ 邮箱 → 设置 → 账户 → POP3/SMTP → 开启获取

### 3. 手动运行

```bash
python run_daily.py
```

输出 PDF `每日新闻_YYYYMMDD.pdf`，并发送到配置的邮箱。

## 信源

| 信源 | 覆盖 | 采集方式 |
|------|------|---------|
| 学习强国-重要新闻 | 时政 | JSON 数据文件 |
| 中国政府网-要闻 | 政策 | JSON API |
| 华尔街见闻-硬AI | AI | JSON API |
| 华尔街见闻-全球 | 宏观 | JSON API |
| 同花顺-今日要闻 | 财经 | JSON API |

## 定时任务（Windows）

```powershell
schtasks /create /tn "DailyNews" /tr "\"python.exe\" \"路径\run_daily.py\"" /sc daily /st 10:00 /f
```

## 文件结构

```
├── run_daily.py          # 一键全流程
├── fetch_news.py         # 数据采集
├── generate_summary.py   # AI 摘要
├── generate_pdf.py       # PDF 生成
├── send_email.py         # 邮件发送
├── config.example.py     # 配置模板
└── SKILL.md              # 详细说明
```

## 许可

MIT
