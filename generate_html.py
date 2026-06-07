"""
每日新闻 HTML 生成器
移动端友好的响应式 HTML，适合手机阅读
"""

from fetch_news import Article
from generate_summary import generate_summary
from collections import OrderedDict
from datetime import datetime


def build_html(articles: list[Article], date_str: str, summary: str = "", output_path: str = None) -> str:
    """生成每日新闻 HTML 文件，返回文件路径"""

    if output_path is None:
        output_path = f"每日新闻_{date_str.replace('-', '')}.html"

    grouped = OrderedDict()
    for a in articles:
        grouped.setdefault(a.source, []).append(a)

    # 星期
    wd_map = ["一", "二", "三", "四", "五", "六", "日"]
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = wd_map[dt.weekday()]

    # 摘要段落
    summary_paragraphs = ""
    if summary:
        for p in summary.strip().split("\n\n"):
            p = p.strip()
            if p:
                summary_paragraphs += f"<p>{p}</p>\n"

    # 构建文章列表
    articles_html = ""
    article_num = 0
    for src, items in grouped.items():
        articles_html += f'<div class="section"><h2>{src}<span class="count">（{len(items)} 篇）</span></h2>\n'
        for a in items:
            article_num += 1
            articles_html += f'<div class="article">'
            articles_html += f'<div class="title">{article_num}. {a.title}</div>'
            if a.url:
                articles_html += f'<div class="url"><a href="{a.url}">{a.url}</a></div>'
            if a.summary:
                articles_html += f'<div class="summary">{a.summary}</div>'
            articles_html += '</div>\n'
        articles_html += '</div>\n'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日新闻 {date_str}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 16px; line-height: 1.8; color: #222; background: #f8f8f8;
    max-width: 640px; margin: 0 auto; padding: 0 16px;
  }}
  .cover {{
    text-align: center; padding: 40px 0 24px;
  }}
  .cover h1 {{ font-size: 28px; font-weight: 800; }}
  .cover .date {{ color: #888; font-size: 14px; margin-top: 8px; }}
  .cover .sources {{
    color: #555; font-size: 14px; margin-top: 12px; padding-top: 12px;
    border-top: 1px solid #ddd;
  }}
  .summary-box {{
    background: #fff; border-radius: 10px; padding: 20px; margin: 16px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
  }}
  .summary-box h2 {{ font-size: 18px; margin-bottom: 10px; }}
  .summary-box p {{ color: #444; font-size: 15px; margin-bottom: 10px; }}
  .section {{ margin: 20px 0; }}
  .section h2 {{
    font-size: 20px; padding-bottom: 8px; border-bottom: 2px solid #222;
    margin-bottom: 12px;
  }}
  .section .count {{ font-size: 14px; color: #999; font-weight: normal; margin-left: 4px; }}
  .article {{
    background: #fff; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .article .title {{ font-size: 16px; font-weight: 700; margin-bottom: 4px; }}
  .article .url {{ font-size: 12px; margin-bottom: 4px; word-break: break-all; }}
  .article .url a {{ color: #0563C1; text-decoration: none; }}
  .article .summary {{
    font-size: 14px; color: #777; font-style: italic; margin-top: 6px;
    padding-top: 6px; border-top: 1px solid #eee;
  }}
  .footer {{
    text-align: center; color: #bbb; font-size: 12px; padding: 30px 0;
  }}
</style>
</head>
<body>

<div class="cover">
  <h1>每日新闻</h1>
  <div class="date">{date_str}  星期{weekday}  共 {len(articles)} 篇</div>
  <div class="sources">{'  ·  '.join(f'{k}（{len(v)}）' for k, v in grouped.items())}</div>
</div>

<div class="summary-box">
  <h2>今日摘要</h2>
  {summary_paragraphs}
</div>

{articles_html}

<div class="footer">每日新闻 · {date_str} · 自动生成</div>

</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


if __name__ == "__main__":
    from fetch_news import fetch_all
    today = datetime.now().strftime("%Y-%m-%d")
    articles = fetch_all()
    summary = generate_summary(articles, target_date=today)
    path = build_html(articles, today, summary)
    print(f"HTML: {path}  |  {len(articles)} 篇")
