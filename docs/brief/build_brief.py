#!/usr/bin/env python3
"""Build the stead.ai 2-page brief (A4 PDF) from brief.json.

Usage:  python3 docs/brief/build_brief.py [output.pdf]

All text lives in brief.json. This script only holds layout. It fails
(exit code 1) if the content does not fit on exactly 2 pages, so a text
edit can never silently spill onto a third page or get cut off.
"""
import json
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "stead.ai_Stock_Swap_Brief_2pages.pdf"

NAVY = HexColor("#0E1726")
TEXT = HexColor("#3B4656")
ORANGE = HexColor("#E8590C")
DEEP_ORANGE = HexColor("#C2410C")
SLATE = HexColor("#4A5568")
LINK = "#1D5C9E"
RULE = HexColor("#D5DBE3")
PANEL = HexColor("#F5F7FA")
HIGHLIGHT = HexColor("#FFF1E6")
BAR_COLORS = {"navy": NAVY, "slate": SLATE, "orange": DEEP_ORANGE}

PAGE_W, PAGE_H = A4
MARGIN_X = 42
TOP = 40
BOTTOM = 40
WIDTH = PAGE_W - 2 * MARGIN_X

for _name in ("Inter-Regular", "Inter-Medium", "Inter-SemiBold", "SpaceGrotesk-Bold"):
    pdfmetrics.registerFont(TTFont(_name, str(HERE / "fonts" / f"{_name}.ttf")))

R, M, SB, H = "Inter-Regular", "Inter-Medium", "Inter-SemiBold", "SpaceGrotesk-Bold"


def style(name, font=R, size=7.6, lead=None, color=TEXT, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=lead or size * 1.36, textColor=color, **kw)


BODY = style("body")
LEAD = style("lead", M, 7.9, 11.4, NAVY)
CELL = style("cell", size=7.3, lead=9.9)
CELL_HEAD = style("cellhead", SB, 6.5, 8.4, NAVY)
HEADING = style("heading", H, 11.6, 13.6, NAVY)
BULLET = style("bullet", leftIndent=9, bulletIndent=0, bulletFontName=SB,
               bulletFontSize=7.6, bulletColor=ORANGE)
STAT_TEXT = style("stat", size=7.3, lead=9.6)
CARD_TITLE = style("cardtitle", H, 11.2, 13.4, NAVY)
BOX_TITLE = style("boxtitle", SB, 7.4, 10, NAVY)
BOX_TITLE_C = style("boxtitlec", SB, 7.4, 10, NAVY, alignment=TA_CENTER)
BOX_TEXT = style("boxtext", size=7.2, lead=9.7)
BOX_TEXT_C = style("boxtextc", size=7.2, lead=9.7, alignment=TA_CENTER)
BADGE = style("badge", SB, 7.2, 9.4, NAVY, alignment=TA_CENTER)


def markup(text):
    """**bold** and [text](url) to ReportLab paragraph markup."""
    if chr(0x2014) in text:
        raise ValueError(f"Em dash found, not allowed: {text[:60]!r}")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # bold inside a link keeps the link colour; bold elsewhere is navy
    text = re.sub(r"\[\*\*([^\]]+?)\*\*\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}" color="{LINK}"><font name="{SB}">{m.group(1)}</font></a>', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}" color="{LINK}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*",
                  lambda m: f'<font name="{SB}" color="#0E1726">{m.group(1)}</font>', text)
    return text


def para(text, st=BODY):
    return Paragraph(markup(text), st)


def height_of(flowable, width):
    return flowable.wrap(width, 10000)[1]


class Spaced(Flowable):
    """One line of letter-spaced text (kickers, bylines)."""

    def __init__(self, text, font=SB, size=6.5, color=ORANGE, spacing=1.1):
        super().__init__()
        self.text, self.font, self.size, self.color, self.spacing = text, font, size, color, spacing

    def wrap(self, aw, ah):
        return aw, self.size * 1.25

    def draw(self):
        t = self.canv.beginText(0, self.size * 0.2)
        t.setFont(self.font, self.size)
        t.setFillColor(self.color)
        t.setCharSpace(self.spacing)
        t.textLine(self.text)
        self.canv.drawText(t)


class Header(Flowable):
    def __init__(self, b):
        super().__init__()
        self.b = b

    def wrap(self, aw, ah):
        self.w = aw
        return aw, 86

    def draw(self):
        c, b = self.canv, self.b
        Spaced(b["kicker"], spacing=1.5).drawOn(c, 0, 76)
        c.setFillColor(NAVY)
        c.setFont(H, 27)
        c.drawString(0, 46, b["title"])
        c.setFont(R, 11.6)
        c.setFillColor(TEXT)
        c.drawString(0, 27, b["subtitle"])
        Spaced(b["byline"], font=M, size=6.6, color=TEXT, spacing=0.5).drawOn(c, 0, 10)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.line(0, 0, self.w, 0)
        # four-point star
        cx, cy, a, k = self.w - 16, 58, 14, 2.6
        p = c.beginPath()
        p.moveTo(cx, cy + a)
        for x, y in ((cx + k, cy + k), (cx + a, cy), (cx + k, cy - k), (cx, cy - a),
                     (cx - k, cy - k), (cx - a, cy), (cx - k, cy + k)):
            p.lineTo(x, y)
        p.close()
        c.setFillColor(ORANGE)
        c.drawPath(p, stroke=0, fill=1)


class LeadBox(Flowable):
    PAD = 9

    def __init__(self, text):
        super().__init__()
        self.p = para(text, LEAD)

    def wrap(self, aw, ah):
        self.w = aw
        self.h = height_of(self.p, aw - 2 * self.PAD - 6) + 2 * self.PAD
        return aw, self.h

    def draw(self):
        c = self.canv
        c.setFillColor(PANEL)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.rect(0, 0, self.w, self.h, stroke=1, fill=1)
        c.setFillColor(ORANGE)
        c.rect(0, 0, 2.4, self.h, stroke=0, fill=1)
        self.p.drawOn(c, self.PAD + 6, self.PAD)


class Boxes(Flowable):
    """A row of equal boxes with an orange top border (stats and ask cards)."""

    def __init__(self, columns, gap=10, pad=8):
        super().__init__()
        self.columns, self.gap, self.pad = columns, gap, pad

    def wrap(self, aw, ah):
        n = len(self.columns)
        self.cw = (aw - self.gap * (n - 1)) / n
        inner = self.cw - 2 * self.pad
        self.heights = [[(f, height_of(f, inner)) for f in col] for col in self.columns]
        self.h = max(sum(h for _, h in col) for col in self.heights) + 2 * self.pad
        return aw, self.h

    def draw(self):
        c = self.canv
        for i, col in enumerate(self.heights):
            x = i * (self.cw + self.gap)
            c.setStrokeColor(RULE)
            c.setLineWidth(0.5)
            c.setFillColor(white)
            c.rect(x, 0, self.cw, self.h, stroke=1, fill=1)
            c.setFillColor(ORANGE)
            c.rect(x, self.h - 2, self.cw, 2, stroke=0, fill=1)
            y = self.h - self.pad
            for f, h in col:
                y -= h
                f.drawOn(c, x + self.pad, y)


class Bars(Flowable):
    HEIGHT = 34

    def __init__(self, items):
        super().__init__()
        self.items = items

    def wrap(self, aw, ah):
        self.w = aw
        return aw, self.HEIGHT

    def draw(self):
        c = self.canv
        total = sum(i["weight"] for i in self.items)
        x = 0
        for it in self.items:
            w = self.w * it["weight"] / total
            c.setFillColor(BAR_COLORS[it["color"]])
            c.rect(x, 0, w - 1, self.HEIGHT, stroke=0, fill=1)
            c.setFillColor(white)
            c.setFont(SB, 7.8)
            c.drawString(x + 9, 20, it["title"])
            c.setFont(R, 7.3)
            c.drawString(x + 9, 9, it["text"])
            x += w


class Flow(Flowable):
    SIDE, GAP, PAD = 96, 26, 8

    def __init__(self, b):
        super().__init__()
        self.b = b

    def wrap(self, aw, ah):
        self.w = aw
        self.mid_w = aw - 2 * (self.SIDE + self.GAP) - 2 * self.PAD
        inner = self.mid_w - 2 * self.PAD
        b = self.b
        self.top = [para(b["top"]["title"], BOX_TITLE), para(b["top"]["text"], BOX_TEXT)]
        self.bot = [para(b["bottom"]["title"], BOX_TITLE), para(b["bottom"]["text"], BOX_TEXT)]
        self.badge = para(b["bottom"]["badge"], BADGE)
        self.top_h = sum(height_of(f, inner) for f in self.top) + 2 * self.PAD + 2
        self.bot_h = sum(height_of(f, inner) for f in self.bot) + 2 * self.PAD + 2 + 22
        self.h = self.top_h + self.bot_h + 3 * self.PAD
        return aw, self.h

    def _stack(self, flowables, x, y_top, width):
        y = y_top
        for f in flowables:
            h = height_of(f, width)
            y -= h
            f.drawOn(self.canv, x, y)
            y -= 2
        return y

    def _arrow(self, x1, x2, y, color):
        c = self.canv
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(0.9)
        c.line(x1, y, x2, y)
        d = 4 if x2 > x1 else -4
        p = c.beginPath()
        p.moveTo(x2, y)
        p.lineTo(x2 - d, y + 2.6)
        p.lineTo(x2 - d, y - 2.6)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    def draw(self):
        c, b, P = self.canv, self.b, self.PAD
        c.setFillColor(PANEL)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, self.w, self.h, 4, stroke=1, fill=1)
        # side boxes
        for x, side in ((P, b["left"]), (self.w - P - self.SIDE, b["right"])):
            c.setFillColor(white)
            c.roundRect(x, P, self.SIDE, self.h - 2 * P, 4, stroke=1, fill=1)
            t = para(side["title"], BOX_TITLE_C)
            s = para(side["text"], BOX_TEXT_C)
            inner = self.SIDE - 2 * P
            block = height_of(t, inner) + 4 + height_of(s, inner)
            self._stack([t, s], x + P, self.h / 2 + block / 2, inner)
        # middle boxes
        mx = P + self.SIDE + self.GAP
        top_y = self.h - P - self.top_h
        inner = self.mid_w - 2 * P
        c.setFillColor(white)
        c.roundRect(mx, top_y, self.mid_w, self.top_h, 4, stroke=1, fill=1)
        self._stack(self.top, mx + P, top_y + self.top_h - P, inner)
        c.roundRect(mx, P, self.mid_w, self.bot_h, 4, stroke=1, fill=1)
        self._stack(self.bot, mx + P, P + self.bot_h - P, inner)
        c.setFillColor(HIGHLIGHT)
        c.setStrokeColor(ORANGE)
        c.roundRect(mx + P, P + 6, inner, 15, 3, stroke=1, fill=1)
        self.badge.wrap(inner, 100)
        self.badge.drawOn(c, mx + P, P + 6 + 3.6)
        # arrows: loan goes right (navy), repayment comes back (orange)
        y1 = top_y + self.top_h / 2
        y2 = P + self.bot_h / 2
        left_edge, right_edge = P + self.SIDE, self.w - P - self.SIDE
        self._arrow(left_edge + 3, mx - 3, y1, NAVY)
        self._arrow(mx + self.mid_w + 3, right_edge - 3, y1, NAVY)
        self._arrow(right_edge - 3, mx + self.mid_w + 3, y2, ORANGE)
        self._arrow(mx - 3, left_edge + 3, y2, ORANGE)


def table(b):
    compact = b.get("compact", False)
    rows = [[para(h, CELL_HEAD) for h in b["header"]]]
    rows += [[para(cell, CELL) for cell in row] for row in b["rows"]]
    t = Table(rows, colWidths=[WIDTH * w for w in b["widths"]])
    pad = 2.6 if compact else 3.6
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad + 0.6),
        ("LINEABOVE", (0, 0), (-1, 0), 1.1, NAVY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, NAVY),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
    ]
    if b.get("highlight_last"):
        cmds.append(("BACKGROUND", (0, -1), (-1, -1), HIGHLIGHT))
    t.setStyle(TableStyle(cmds))
    return t


def render(block):
    """Return a list of (flowable, space_before) for one content block."""
    kind = block["type"]
    if kind == "header":
        return [(Header(block), 0)]
    if kind == "lead":
        return [(LeadBox(block["text"]), 8)]
    if kind == "stats":
        cols = [[Paragraph(markup(i["big"]), style("big", H, 20, 23, NAVY)),
                 para(i["text"], STAT_TEXT), para(i["source"], style("src", size=7.1, lead=12))]
                for i in block["items"]]
        return [(Boxes(cols), 8)]
    if kind == "section":
        return [(Spaced(block["kicker"]), 8.5), (para(block["heading"], HEADING), 2)]
    if kind == "para":
        return [(para(block["text"]), 4)]
    if kind == "bullets":
        return [(Paragraph(markup(t), BULLET, bulletText="•"), 3 if i else 4)
                for i, t in enumerate(block["items"])]
    if kind == "table":
        return [(table(block), 4)]
    if kind == "flow":
        return [(Flow(block), 6)]
    if kind == "bars":
        return [(Bars(block["items"]), 6)]
    if kind == "cards":
        cols = [[Spaced(i["kicker"], spacing=0.6), para(i["title"], CARD_TITLE),
                 para(i["text"], STAT_TEXT)] for i in block["items"]]
        return [(Boxes(cols, gap=8, pad=7), 5)]
    raise ValueError(f"Unknown block type: {kind}")


def build(out_path=DEFAULT_OUT, source=HERE / "brief.json"):
    from reportlab.pdfgen.canvas import Canvas

    data = json.loads(Path(source).read_text(encoding="utf-8"))
    pages = data["pages"]
    if len(pages) != 2:
        raise SystemExit(f"brief.json must define exactly 2 pages, found {len(pages)}")

    c = Canvas(str(out_path), pagesize=A4)
    c.setTitle("stead.ai: insured stock swaps (2-page brief)")
    c.setAuthor("stead.ai")
    report = []
    for number, blocks in enumerate(pages, 1):
        y = PAGE_H - TOP
        for block in blocks:
            for flowable, space in render(block):
                _, h = flowable.wrap(WIDTH, 10000)
                y -= space + h
                flowable.drawOn(c, MARGIN_X, y)
        spare = y - BOTTOM
        report.append((number, spare))
        c.setFont(R, 6.8)
        c.setFillColor(TEXT)
        c.drawString(MARGIN_X, 26, data["footer"])
        c.drawRightString(PAGE_W - MARGIN_X, 26, f"{number} / {len(pages)}")
        c.showPage()

    overflow = [(n, s) for n, s in report if s < 0]
    if overflow:
        for n, s in overflow:
            print(f"ERROR: page {n} overflows by {-s:.0f} pt. Cut text in brief.json.", file=sys.stderr)
        raise SystemExit(1)
    c.save()
    for n, s in report:
        print(f"page {n}: {s:.0f} pt spare")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT)
