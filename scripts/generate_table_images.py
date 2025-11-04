"""
Generate PNG snapshots of CREATE TABLE statements for Phase II submission.
"""
from pathlib import Path
from typing import Dict

from PIL import Image, ImageDraw, ImageFont

SCHEMA_PATH = Path("db/schema.sql")
OUTPUT_DIR = Path("docs/images/phase2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_table_blocks(sql_text: str) -> Dict[str, str]:
    blocks: Dict[str, str] = {}
    lines = sql_text.splitlines()
    capture = False
    table_name = ""
    buffer = []
    for line in lines:
        stripped = line.strip().lower()
        if stripped.startswith("create table"):
            capture = True
            table_name = line.split("(")[0].split()[-1].strip()
            buffer = [line]
            continue
        if capture:
            buffer.append(line)
            if stripped.endswith(");") or stripped == ");":
                blocks[table_name.replace("`", "").replace('"', "")] = "\n".join(buffer)
                capture = False
                table_name = ""
                buffer = []
    return blocks


def render_text_to_image(text: str, output_path: Path) -> None:
    lines = text.splitlines()
    if not lines:
        return
    font = ImageFont.load_default()
    line_height = font.getbbox("Ag")[3] + 6
    text_width = max(font.getbbox(line)[2] for line in lines)
    padding_x, padding_y = 20, 20
    width = text_width + (padding_x * 2)
    height = line_height * len(lines) + (padding_y * 2)

    img = Image.new("RGB", (width, height), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    y = padding_y
    for line in lines:
        draw.text((padding_x, y), line, font=font, fill=(230, 230, 230))
        y += line_height

    img.save(output_path)


def main() -> None:
    sql_text = SCHEMA_PATH.read_text()
    table_blocks = extract_table_blocks(sql_text)
    for table_name, block in table_blocks.items():
        slug = table_name.replace(".", "_")
        output_file = OUTPUT_DIR / f"{slug}_schema.png"
        render_text_to_image(block, output_file)
        print(f"Generated {output_file}")


if __name__ == "__main__":
    main()

