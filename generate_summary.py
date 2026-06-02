"""
每日新闻 AI 摘要生成器
调用 DeepSeek API，根据所有标题生成当日 3 段自然语言摘要
"""

from datetime import datetime
import re
import requests
from config import DEEPSEEK_API_KEY
from fetch_news import Article

API_URL = "https://api.deepseek.com/v1/chat/completions"


def generate_summary(articles: list[Article], target_date: str = None, max_chars: int = 3000) -> str:
    """根据文章列表生成当日新闻摘要。若标题总长超限则自动截断。"""

    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    # 按信源分组，截取适合 API 的长度
    groups: dict[str, list[str]] = {}
    total_chars = 0
    for a in articles:
        groups.setdefault(a.source, [])
        line = f"  - {a.title}"
        if total_chars + len(line) > max_chars:
            break
        groups[a.source].append(line)
        total_chars += len(line)

    # 构造输入文本
    sections = []
    for src, lines in groups.items():
        sections.append(f"【{src}】\n" + "\n".join(lines))
    titles_text = "\n\n".join(sections)

    prompt = f"""以下是{target_date}各新闻源的文章标题列表。请根据这些标题，生成一份当日新闻总摘要。要求：

1. 用 3 段自然语言概述，每段聚焦一个主题方向（如政策动向 / 财经市场 / 科技AI 等，根据当天内容灵活选择）
2. 每段 80-150 字，不罗列标题，而是提炼关键词背后的趋势和信号
3. 语言简洁、客观，不添加标题中没有的信息，不做预测
4. 纯文本输出，禁止使用 Markdown 格式（不要 ### 标题、不要 ** 加粗、不要列表符号）
5. 文末不要写"以上是今日摘要"之类的收尾

{titles_text}"""

    resp = requests.post(API_URL, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }, json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 600,
    }, timeout=60)

    data = resp.json()
    text = data["choices"][0]["message"]["content"].strip()

    # 后处理：清理残留的 Markdown 标记
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)  # ### 标题
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)        # **加粗** *斜体*
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)     # - 列表
    text = re.sub(r'\n{3,}', '\n\n', text)                        # 多余空行

    return text
