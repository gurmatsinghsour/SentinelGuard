"""
Convert a text file into a PNG image (monospace on dark background).
Usage: python3 scripts/text_to_image.py input.txt output.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def text_to_image(text: str, output_path: Path) -> None:
    lines = text.rstrip("\n").splitlines()
    if not lines:
        return
    font = ImageFont.load_default()
    line_height = font.getbbox("Ag")[3] + 6
    text_width = max(font.getbbox(line)[2] for line in lines) if lines else 0
    padding = 20
    width = text_width + padding * 2
    height = line_height * len(lines) + padding * 2

    img = Image.new("RGB", (width, height), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    y = padding
    for line in lines:
        draw.text((padding, y), line, font=font, fill=(236, 236, 236))
        y += line_height
    img.save(output_path)


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/text_to_image.py input.txt output.png")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    text = input_path.read_text()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text_to_image(text, output_path)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()

