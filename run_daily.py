"""
每日新闻一键生成 + 发送（覆盖前一天新闻）
Windows 任务计划直接调用此脚本
"""

import sys
import os
from datetime import datetime, timedelta

# 确保在当前目录运行
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from fetch_news import fetch_all
from generate_pdf import build
from generate_html import build_html
from generate_summary import generate_summary
from send_email import send_daily_news

if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now()
    print(f"=== 每日新闻 {today:%Y-%m-%d %H:%M}（覆盖 {yesterday}）===\n")

    # 1. 采集
    print("[1/4] 采集新闻...")
    articles = fetch_all(target_date=yesterday)
    if not articles:
        print(f"{yesterday} 未获取到任何文章，退出")
        sys.exit(1)
    print(f"  共 {len(articles)} 篇\n")

    # 2. AI 摘要
    print("[2/4] 生成 AI 摘要...")
    summary = generate_summary(articles, target_date=yesterday)

    # 3. 生成 PDF + HTML
    print("[3/4] 生成文件...")
    pdf_fn = "每日新闻_" + yesterday.replace("-", "") + ".pdf"
    html_fn = "每日新闻_" + yesterday.replace("-", "") + ".html"
    pages = build(articles, pdf_fn, date_str=yesterday)
    build_html(articles, yesterday, summary, html_fn)
    print(f"  {pdf_fn} | {pages} 页")
    print(f"  {html_fn}\n")

    # 4. 发送
    print("[4/4] 发送邮件...")
    send_daily_news(pdf_fn, html_fn, len(articles))

    print("\n=== 完成 ===")
