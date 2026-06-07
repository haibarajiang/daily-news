"""
邮件发送模块 — 双收件人，PDF + HTML 双附件
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from config import SMTP_HOST, SMTP_PORT, EMAIL_FROM, EMAIL_TO, EMAIL_CC, EMAIL_AUTH_CODE


def send_daily_news(pdf_path: str, html_path: str, article_count: int):
    """发送每日新闻 PDF + HTML 到指定邮箱"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML 文件不存在: {html_path}")

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"每日新闻 {today}（共 {article_count} 篇）"

    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Cc"] = EMAIL_CC

    all_recipients = [EMAIL_TO] + [EMAIL_CC]

    # 正文
    body = (
        f"日报已生成，请查收附件。\n\n"
        f"日期：{today}\n"
        f"文章数：{article_count}\n"
        f"信源：学习强国/中国政府网/华尔街见闻·硬AI/华尔街见闻·全球/同花顺\n\n"
        f"PDF 适合电脑阅读，HTML 适合手机查看。"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # PDF 附件
    with open(pdf_path, "rb") as f:
        att = MIMEApplication(f.read(), _subtype="pdf", filename=os.path.basename(pdf_path))
        att.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_path))
        msg.attach(att)

    # HTML 附件（手机友好）
    with open(html_path, "rb") as f:
        att = MIMEApplication(f.read(), _subtype="html", filename=os.path.basename(html_path))
        att.add_header("Content-Disposition", "attachment", filename=os.path.basename(html_path))
        msg.attach(att)

    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
    server.login(EMAIL_FROM, EMAIL_AUTH_CODE)
    server.sendmail(EMAIL_FROM, all_recipients, msg.as_string())
    server.quit()
    print(f"邮件已发送: {subject}  →  {', '.join(all_recipients)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("用法: python send_email.py <pdf路径> <html路径> <文章数>")
        sys.exit(1)
    send_daily_news(sys.argv[1], sys.argv[2], int(sys.argv[3]))
