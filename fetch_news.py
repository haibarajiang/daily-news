"""
每日新闻数据采集模块
支持信源: gov.cn, 同花顺, xuexi.cn(JSON), 华尔街见闻(硬AI+全球)
"""

import json
import re
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass

XUEXI_DATA_URL = "https://www.xuexi.cn/lgdata/1jscb6pu1n2.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

@dataclass
class Article:
    title: str
    url: str
    source: str
    date: str
    summary: str = ""

    def __hash__(self):
        return hash(self.url)


def fetch_govcn(target_date: str) -> list[Article]:
    """中国政府网 - 要闻 (JSON API, 指定日期)"""
    url = "https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = 'utf-8'
    data = resp.json()
    articles = []
    for item in data:
        date_str = item.get("DOCRELPUBTIME", "")
        if date_str != target_date:
            continue
        articles.append(Article(
            title=item.get("TITLE", "").strip(),
            url=item.get("URL", ""),
            source="中国政府网-要闻",
            date=date_str,
        ))
    return articles


def fetch_10jqka(category: str, label: str, target_date: str) -> list[Article]:
    """同花顺新闻 (JSON API, 指定日期)"""
    url = f"https://news.10jqka.com.cn/{category}_list/index.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    data = resp.json()
    articles = []
    for item in data:
        ts = item.get("ctime", 0)
        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
        if date_str != target_date:
            continue
        articles.append(Article(
            title=item.get("title", "").strip(),
            url=item.get("url", ""),
            source=f"同花顺-{label}",
            date=date_str,
        ))
    return articles


def fetch_xuexi(target_date: str) -> list[Article]:
    """学习强国 - 重要新闻 (JSON 数据文件, 指定日期)"""
    resp = requests.get(XUEXI_DATA_URL, headers=HEADERS, timeout=30)
    resp.encoding = 'utf-8'
    raw = resp.text

    articles = []
    seen = set()

    # JSON 有嵌套引号瑕疵, 用正则逐条提取 title / publishTime / url
    for m in re.finditer(
        r'\{"editor":[^}]*?"publishTime":"(\d{4}-\d{2}-\d{2})[^"]*".*?'
        r'"title":"((?:[^"\\]|\\.)*?)".*?'
        r'"url":"(https://www\.xuexi\.cn/lgpage/detail/index\.html\?[^"]+)"',
        raw
    ):
        date_str = m.group(1)
        if date_str != target_date:
            continue
        title = m.group(2).replace('\\"', '"').replace('\\\\', '\\')
        url = m.group(3).replace('\\/', '/')
        if url in seen:
            continue
        seen.add(url)
        articles.append(Article(
            title=title,
            url=url,
            source="学习强国-重要新闻",
            date=date_str,
        ))
    return articles


def fetch_wallstreetcn(channel: str, label: str, target_date: str) -> list[Article]:
    """华尔街见闻 - JSON API (information-flow, 指定日期)"""
    url = (
        "https://api-one-wscn.awtmt.com/apiv1/content/information-flow"
        f"?channel={channel}&accept=article&cursor=&limit=50&action=upglide"
    )
    resp = requests.get(url, headers=HEADERS, timeout=15)
    data = resp.json()

    articles = []
    for item in data.get("data", {}).get("items", []):
        res = item.get("resource", {})
        ts = res.get("display_time", 0)
        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
        if date_str != target_date:
            continue
        uri = res.get("uri", "")
        if uri.startswith("http"):
            article_url = uri
        else:
            article_url = f"https://wallstreetcn.com{uri}" if uri else ""
        articles.append(Article(
            title=res.get("title", "").strip(),
            url=article_url,
            source=f"华尔街见闻-{label}",
            date=date_str,
            summary=(res.get("content_short", "") or "").strip(),
        ))
    return articles


def fetch_all(target_date: str = None) -> list[Article]:
    """采集所有信源，去重，按日期排序。target_date 默认为今日。"""
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    all_articles = []

    fetchers = [
        ("xuexi.cn", lambda: fetch_xuexi(target_date)),
        ("gov.cn", lambda: fetch_govcn(target_date)),
        ("wscn-ai", lambda: fetch_wallstreetcn("ai", "硬AI", target_date)),
        ("wscn-global", lambda: fetch_wallstreetcn("global", "全球", target_date)),
        ("10jqka-today", lambda: fetch_10jqka("today", "今日要闻", target_date)[:20]),
    ]

    for name, fetcher in fetchers:
        try:
            articles = fetcher()
            all_articles.extend(articles)
            print(f"  [{name}] {len(articles)} 条")
        except Exception as e:
            print(f"  [{name}] 采集失败: {e}")

    # Dedup by URL
    seen = set()
    unique = []
    for a in all_articles:
        if a.url not in seen:
            seen.add(a.url)
            unique.append(a)

    # Sort by date descending (articles without date go last)
    unique.sort(key=lambda a: a.date or "0000-00-00", reverse=True)

    print(f"  总计: {len(unique)} 条（去重后）")
    return unique


if __name__ == "__main__":
    print("采集新闻...")
    articles = fetch_all()
    print(f"\n获取 {len(articles)} 篇文章")
    for i, a in enumerate(articles[:10]):
        print(f"{i+1}. [{a.source}] {a.title[:50]}")
