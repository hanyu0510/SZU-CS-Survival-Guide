# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.table import Table
from docx.text.paragraph import Paragraph


TABLE_CAPTIONS = [
    "表 1 实验目的、内容与过程",
    "表 2 实验结果分析与结论",
    "表 3 指导教师批阅意见表",
]

FIGURE_CAPTION_GROUPS = [
    ["图 1 鸡蛋掉落问题示意图"],
    [
        "图 2 （左）第一次从 2F 投掷的递归分支示意图",
        "图 3 （右）第一次从 1F 投掷的递归分支示意图",
    ],
    ["图 4 不同算法耗时走势对比图"],
]


def add_caption_style_if_needed(doc: Document) -> None:
    try:
        style = doc.styles["Caption"]
    except KeyError:
        style = doc.styles.add_style("Caption", 1)
    style.font.name = "宋体"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    style.font.size = Pt(10.5)
    style.font.italic = False


def caption_paragraph(text: str, *, before: int, after: int) -> OxmlElement:
    p = OxmlElement("w:p")

    p_pr = OxmlElement("w:pPr")
    p_style = OxmlElement("w:pStyle")
    p_style.set(qn("w:val"), "Caption")
    p_pr.append(p_style)

    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    p_pr.append(jc)

    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), str(before))
    spacing.set(qn("w:after"), str(after))
    p_pr.append(spacing)

    p.append(p_pr)

    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")

    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), "Times New Roman")
    r_fonts.set(qn("w:hAnsi"), "Times New Roman")
    r_fonts.set(qn("w:eastAsia"), "宋体")
    r_pr.append(r_fonts)

    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "21")
    r_pr.append(sz)
    sz_cs = OxmlElement("w:szCs")
    sz_cs.set(qn("w:val"), "21")
    r_pr.append(sz_cs)

    r.append(r_pr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    p.append(r)
    return p


def paragraph_text(p_el: OxmlElement) -> str:
    return "".join(p_el.xpath(".//w:t/text()")).strip()


def previous_text(el: OxmlElement) -> str:
    prev = el.getprevious()
    if prev is None or not prev.tag.endswith("}p"):
        return ""
    return paragraph_text(prev)


def next_text(el: OxmlElement) -> str:
    nxt = el.getnext()
    if nxt is None or not nxt.tag.endswith("}p"):
        return ""
    return paragraph_text(nxt)


def iter_paragraphs_in_table(table: Table):
    for row in table.rows:
        for cell in row.cells:
            for child in cell._tc.iterchildren():
                if child.tag.endswith("}p"):
                    yield Paragraph(child, cell)
                elif child.tag.endswith("}tbl"):
                    yield from iter_paragraphs_in_table(Table(child, cell))


def body_tables(doc: Document):
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}tbl"):
            yield child


def image_paragraphs(doc: Document):
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            para = Paragraph(child, doc)
            if para._p.xpath(".//w:drawing"):
                yield para
        elif child.tag.endswith("}tbl"):
            for para in iter_paragraphs_in_table(Table(child, doc)):
                if para._p.xpath(".//w:drawing"):
                    yield para


def main() -> None:
    candidates = sorted(
        Path.cwd().glob("*2024040042.docx"),
        key=lambda p: (p.name.count("("), -p.stat().st_mtime),
    )
    candidates = [p for p in candidates if "图表题注" not in p.stem]
    if not candidates:
        raise SystemExit("No target document found.")

    source = candidates[0]
    output = source.with_name(f"{source.stem}-图表题注.docx")

    doc = Document(source)
    add_caption_style_if_needed(doc)

    tables = list(body_tables(doc))
    if len(tables) != len(TABLE_CAPTIONS):
        raise SystemExit(f"Expected {len(TABLE_CAPTIONS)} body tables, found {len(tables)}.")
    for tbl_el, caption in zip(tables, TABLE_CAPTIONS):
        if not previous_text(tbl_el).startswith("表 "):
            tbl_el.addprevious(caption_paragraph(caption, before=120, after=80))

    figures = list(image_paragraphs(doc))
    if len(figures) != len(FIGURE_CAPTION_GROUPS):
        raise SystemExit(f"Expected {len(FIGURE_CAPTION_GROUPS)} image paragraphs, found {len(figures)}.")
    for para, captions in zip(figures, FIGURE_CAPTION_GROUPS):
        if not next_text(para._p).startswith("图 "):
            anchor = para._p
            for caption in captions:
                cap_el = caption_paragraph(caption, before=60, after=80)
                anchor.addnext(cap_el)
                anchor = cap_el

    doc.save(output)
    print(output)


if __name__ == "__main__":
    main()
