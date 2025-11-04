"""
Render Phase_II_Report.md (including image references) to a PDF using ReportLab.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

SOURCE = Path("Phase_II_Report.md")
OUTPUT = Path("Project_Phase_II.pdf")


def build_pdf():
    styles = getSampleStyleSheet()
    heading_styles = {
        1: ParagraphStyle("Heading1", parent=styles["Heading1"], spaceAfter=12, fontSize=18),
        2: ParagraphStyle("Heading2", parent=styles["Heading2"], spaceAfter=8, fontSize=14),
        3: ParagraphStyle("Heading3", parent=styles["Heading3"], spaceAfter=6, fontSize=12),
    }
    normal_style = styles["BodyText"]
    bullet_style = ParagraphStyle("Bullet", parent=normal_style, leftIndent=18, bulletIndent=9, spaceAfter=6)
    code_style = ParagraphStyle("Code", parent=styles["Code"], fontName="Courier", fontSize=9, leading=11)

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=42, bottomMargin=42)
    flow: List = []

    lines = SOURCE.read_text().splitlines()
    in_code = False
    code_buffer: List[str] = []
    bullet_buffer: List[str] = []

    def flush_code():
        nonlocal code_buffer
        if code_buffer:
            code_text = "\n".join(code_buffer)
            flow.append(Preformatted(code_text, code_style))
            flow.append(Spacer(1, 0.18 * inch))
            code_buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            items = [
                ListItem(Paragraph(item.strip(), normal_style), leftIndent=18, value="bullet") for item in bullet_buffer
            ]
            flow.append(ListFlowable(items, bulletType="bullet", start="circle", spaceAfter=6))
            bullet_buffer = []

    image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.strip() == "---":
            continue
        if line.startswith("```"):
            if in_code:
                flush_code()
            in_code = not in_code
            continue
        if in_code:
            code_buffer.append(line)
            continue

        if line.startswith("- "):
            bullet_buffer.append(line[2:].strip())
            continue
        else:
            flush_bullets()

        match = image_pattern.match(line.strip())
        if match:
            flush_code()
            alt, path = match.groups()
            image_path = Path(path)
            if image_path.exists():
                img = Image(str(image_path))
                max_width = 7.0 * inch
                if img.drawWidth > max_width:
                    ratio = max_width / img.drawWidth
                    img.drawWidth *= ratio
                    img.drawHeight *= ratio
                flow.append(img)
                if alt:
                    flow.append(Paragraph(f"<i>{alt}</i>", ParagraphStyle("ImageCaption", parent=normal_style, alignment=1)))
                flow.append(Spacer(1, 0.2 * inch))
            continue

        if not line.strip():
            flush_code()
            flow.append(Spacer(1, 0.15 * inch))
            continue

        if line.startswith("#"):
            flush_code()
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            style = heading_styles.get(level, normal_style)
            flow.append(Paragraph(text, style))
            continue

        flush_code()
        flow.append(Paragraph(line, normal_style))

    flush_code()
    flush_bullets()

    doc.build(flow)
    print(f"Exported PDF to {OUTPUT}")


if __name__ == "__main__":
    build_pdf()

