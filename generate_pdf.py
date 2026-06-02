"""
每日新闻 PDF 生成器
A4竖版，微软雅黑，简洁报纸风格
"""

import os
import sys
import warnings
from fpdf import FPDF
from fetch_news import Article, fetch_all
from generate_summary import generate_summary
from datetime import datetime
from collections import OrderedDict

warnings.filterwarnings("ignore")
os.environ["FPDF_FONTCONFIG_ENABLED"] = "0"

FONT_DIR = "C:/Windows/Fonts"
FONT_REGULAR = os.path.join(FONT_DIR, "msyh.ttc")
FONT_BOLD = os.path.join(FONT_DIR, "msyhbd.ttc")

PAGE_W = 210
PAGE_H = 297
ML = 30
MR = 28
MT = 14
MB = 16
CONTENT_W = PAGE_W - ML - MR


class DailyNewsPDF(FPDF):
    def __init__(self, date_str: str):
        import logging
        logging.getLogger("fontTools").setLevel(logging.ERROR)
        super().__init__("P", "mm")
        self.date_str = date_str
        self.set_auto_page_break(True, MB)
        self.set_margins(ML, MT, MR)
        self.add_font("CN", "", FONT_REGULAR)
        self.add_font("CN", "B", FONT_BOLD)
        self._current_source = ""

    # ── header / footer ──

    def header(self):
        if self.page_no() <= 2:
            return
        self.set_font("CN", "", 6.5)
        self.set_text_color(170, 170, 170)
        self.cell(CONTENT_W / 2, 4.5, self.date_str, align="L")
        self.cell(CONTENT_W / 2, 4.5, self._current_source, align="R")
        self.ln(5)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("CN", "", 6.5)
        self.set_text_color(170, 170, 170)
        self.cell(0, 10, str(self.page_no()), align="C")

    # ── cover ──

    def cover_page(self, total: int, groups: OrderedDict):
        self.add_page()
        self.ln(50)
        # Title: 42pt bold
        self.set_font("CN", "B", 42)
        self.set_text_color(0, 0, 0)
        self.cell(0, 18, "每日新闻", align="C")
        self.ln(22)
        # Date: 11pt gray
        self.set_font("CN", "", 11)
        self.set_text_color(102, 102, 102)
        today = datetime.now()
        wd = ["一", "二", "三", "四", "五", "六", "日"][today.weekday()]
        self.cell(0, 7, f"{self.date_str}  星期{wd}  共 {total} 篇", align="C")
        self.ln(12)
        # Divider
        x0 = 55
        y = self.get_y()
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.25)
        self.line(x0, y, PAGE_W - x0, y)
        self.ln(12)
        # Source list: bold centered, 14pt each line
        for src, items in groups.items():
            self.set_font("CN", "B", 14)
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, f"{src}（{len(items)} 篇）", align="C")
            self.ln(8)

    # ── TOC ──

    def toc_page(self, articles: list[Article]):
        self.add_page()
        self.set_font("CN", "B", 18)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, "目录", align="L")
        self.ln(12)
        for i, a in enumerate(articles):
            self.set_font("CN", "", 9)
            # Number: gray
            self.set_text_color(136, 136, 136)
            num = f"{i + 1}."
            num_w = self.get_string_width(num) + 3
            self.cell(num_w, 5.5, num, align="R")
            # Title: dark gray
            self.set_text_color(85, 85, 85)
            title = a.title[:60] + ("…" if len(a.title) > 60 else "")
            self.cell(0, 5.5, title)
            self.ln(5.5)

    # ── summary ──

    def summary_page(self, text: str):
        """AI 生成的今日新闻总摘要"""
        self.add_page()
        self.set_font("CN", "B", 18)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, "今日摘要", align="L")
        self.ln(10)
        # Underline
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(ML, self.get_y(), PAGE_W - MR, self.get_y())
        self.ln(8)
        # Summary body: 10.5pt, 1.6x line height
        self.set_font("CN", "", 10.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(CONTENT_W, 8.5, text, align="L")

    # ── section & article ──

    def section_header(self, title: str, count: int):
        """章节标题: Heading 1 风格, 底部分割线"""
        self._current_source = title
        self.ln(4)
        self.set_font("CN", "B", 18)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"{title}（{count} 篇）")
        self.ln(10)
        # Black bottom border
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(ML, self.get_y(), PAGE_W - MR, self.get_y())
        self.ln(8)

    def article_entry(self, a: Article, is_last: bool = False):
        """单篇文章: 标题 → URL → 摘要 → 分隔线"""
        # Estimate needed height
        title_lines = max(1, int(self.get_string_width(a.title) / CONTENT_W) + 1)
        needed = title_lines * 7 + 5 + 5 + 12
        if a.summary:
            summary_lines = max(1, int(self.get_string_width(a.summary) / (CONTENT_W - 8)) + 1)
            needed += summary_lines * 6
        if self.get_y() + needed > PAGE_H - MB:
            self.add_page()

        # Title: 14pt bold, spacing before=8mm after=2mm
        self.ln(2)
        self.set_font("CN", "B", 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(CONTENT_W, 7, a.title, align="L")
        self.ln(1.5)

        # URL: 10.5pt blue underlined Hyperlink style
        if a.url:
            self.set_font("CN", "", 7.5)
            self.set_text_color(5, 99, 193)  # #0563C1
            # Underline via draw after multi_cell
            self.multi_cell(CONTENT_W, 5, a.url, align="L")
            self.ln(2)

        # Summary: 10.5pt italic gray
        if a.summary:
            self.set_font("CN", "", 9)
            self.set_text_color(119, 119, 119)
            indent = 8  # mm indent
            self.set_x(ML + indent)
            self.multi_cell(CONTENT_W - indent, 5.5, a.summary, align="L")

        # Separator: light gray bottom border
        if not is_last:
            self.ln(2)
            self.set_draw_color(221, 221, 221)
            self.set_line_width(0.2)
            y = self.get_y()
            self.line(ML, y, PAGE_W - MR, y)
        self.ln(3)


def build(articles: list[Article], output_path: str, top_n: int = 150, date_str: str = None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    pdf = DailyNewsPDF(date_str)

    selected = articles[:top_n]

    groups = OrderedDict()
    for a in selected:
        groups.setdefault(a.source, []).append(a)

    # Cover
    pdf.cover_page(len(selected), groups)
    # AI Summary (fail gracefully)
    try:
        print("  生成 AI 摘要...")
        summary = generate_summary(selected, target_date=date_str)
        pdf.summary_page(summary)
    except Exception as e:
        print(f"  摘要生成失败: {e}")
    # TOC
    pdf.toc_page(selected)

    # Articles grouped by source, each section starts fresh page
    for src, items in groups.items():
        pdf.add_page()
        pdf.section_header(src, len(items))
        for i, a in enumerate(items):
            pdf.article_entry(a, is_last=(i == len(items) - 1))

    pdf.output(output_path)
    return pdf.page_no()


if __name__ == "__main__":
    print("采集新闻...")
    articles = fetch_all()
    if not articles:
        print("未获取到文章")
        sys.exit(1)

    fn = "每日新闻_" + datetime.now().strftime("%Y%m%d") + ".pdf"
    pages = build(articles, fn, top_n=150)
    print(f"PDF: {fn}  |  页数: {pages}  |  文章: {min(len(articles), 150)}")
