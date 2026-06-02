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
from send_email import send_daily_news

if __name__ == "__main__":
    # 日报覆盖"昨天"完整一天
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now()
    print(f"=== 每日新闻 {today:%Y-%m-%d %H:%M}（覆盖 {yesterday}）===\n")

    # 1. 采集昨天的新闻
    print("[1/3] 采集新闻...")
    articles = fetch_all(target_date=yesterday)
    if not articles:
        print(f"{yesterday} 未获取到任何文章，退出")
        sys.exit(1)
    print(f"  共 {len(articles)} 篇\n")

    # 2. 生成 PDF（封面日期用昨天）
    print("[2/3] 生成 PDF...")
    fn = "每日新闻_" + yesterday.replace("-", "") + ".pdf"
    pages = build(articles, fn, date_str=yesterday)
    print(f"  {fn} | {pages} 页\n")

    # 3. 发送邮件
    print("[3/3] 发送邮件...")
    send_daily_news(fn, len(articles))

    print("\n=== 完成 ===")
