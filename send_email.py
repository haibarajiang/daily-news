"""
每日新闻邮件发送模块
通过 QQ SMTP 将 PDF 作为附件发送
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from config import SMTP_HOST, SMTP_PORT, EMAIL_FROM, EMAIL_TO, EMAIL_AUTH_CODE


def send_daily_news(pdf_path: str, article_count: int):
    """发送每日新闻 PDF 到指定邮箱"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"每日新闻 {today}（共 {article_count} 篇）"

    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    # 正文
    body = f"日报已生成，请查收附件。\n\n日期：{today}\n文章数：{article_count}\n信源：学习强国/中国政府网/华尔街见闻·硬AI/华尔街见闻·全球/同花顺"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # PDF 附件 — MIMEApplication 自动处理 MIME 类型和中文文件名编码
    fname = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as f:
        att = MIMEApplication(f.read(), _subtype="pdf", filename=fname)
        att.add_header("Content-Disposition", "attachment", filename=fname)
        msg.attach(att)

    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
    server.login(EMAIL_FROM, EMAIL_AUTH_CODE)
    server.send_message(msg)
    server.quit()
    print(f"邮件已发送: {subject}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python send_email.py <pdf路径> <文章数>")
        sys.exit(1)
    send_daily_news(sys.argv[1], int(sys.argv[2]))
