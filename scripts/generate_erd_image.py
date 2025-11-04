"""
Generate a simple ER-style diagram using Pillow for Phase II submission.
"""
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = Path("docs/images/phase2/erd.png")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

ENTITY_LAYOUT: Dict[str, Tuple[int, int]] = {
    "analysts": (80, 80),
    "incident_tasks": (80, 380),
    "compliance_reports": (80, 650),
    "assets": (640, 80),
    "security_events": (640, 350),
    "ai_assessments": (1120, 150),
    "threat_intel_matches": (1120, 400),
}

ENTITY_FIELDS: Dict[str, List[str]] = {
    "analysts": ["PK analyst_id", "full_name", "email", "role", "on_call", "created_at"],
    "incident_tasks": [
        "PK task_id",
        "FK event_id",
        "FK assigned_to",
        "task_description",
        "priority",
        "due_date",
        "status",
    ],
    "compliance_reports": [
        "PK report_id",
        "FK event_id (unique)",
        "FK generated_by",
        "generated_at",
        "regulation",
        "summary_text",
    ],
    "assets": [
        "PK asset_id",
        "hostname",
        "ip_address",
        "business_owner",
        "criticality",
        "last_patch_date",
    ],
    "security_events": [
        "PK event_id",
        "FK asset_id",
        "ingest_time",
        "source",
        "raw_log",
        "status",
    ],
    "ai_assessments": [
        "PK assessment_id",
        "FK event_id",
        "model_version",
        "risk_score",
        "severity_label",
        "recommended_action",
    ],
    "threat_intel_matches": [
        "PK match_id",
        "FK event_id",
        "indicator_type",
        "indicator_value",
        "threat_actor",
        "confidence",
    ],
}

RELATIONSHIPS = [
    ("analysts", "incident_tasks", "1", "M"),
    ("analysts", "compliance_reports", "1", "M"),
    ("assets", "security_events", "1", "M"),
    ("security_events", "incident_tasks", "1", "M"),
    ("security_events", "ai_assessments", "1", "M"),
    ("security_events", "threat_intel_matches", "1", "M"),
    ("security_events", "compliance_reports", "1", "1"),
]


def draw_entity(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont, name: str, x: int, y: int) -> None:
    width, height = 320, 200
    draw.rounded_rectangle((x, y, x + width, y + height), radius=12, outline="#1f3c88", width=3, fill="#f5f7fb")
    title_font = ImageFont.load_default()
    draw.text((x + 12, y + 12), name.upper(), font=title_font, fill="#1f3c88")
    field_y = y + 36
    for field in ENTITY_FIELDS[name]:
        draw.text((x + 20, field_y), f"- {field}", font=font, fill="#2c2c2c")
        field_y += 18


def draw_relationships(draw: ImageDraw.ImageDraw) -> None:
    for left, right, card_left, card_right in RELATIONSHIPS:
        x1, y1 = ENTITY_LAYOUT[left]
        x2, y2 = ENTITY_LAYOUT[right]
        center_left = (x1 + 160, y1 + 100)
        center_right = (x2 + 160, y2 + 100)
        draw.line([center_left, center_right], fill="#4b69c6", width=3)
        draw.ellipse([center_left[0] - 4, center_left[1] - 4, center_left[0] + 4, center_left[1] + 4], fill="#4b69c6")
        draw.ellipse([center_right[0] - 4, center_right[1] - 4, center_right[0] + 4, center_right[1] + 4], fill="#4b69c6")
        draw.text((center_left[0] - 20, center_left[1] - 20), card_left, fill="#0d1b2a")
        draw.text((center_right[0] + 8, center_right[1] - 20), card_right, fill="#0d1b2a")


def main() -> None:
    img = Image.new("RGB", (1500, 900), color="white")
    draw = ImageDraw.Draw(img)
    body_font = ImageFont.load_default()

    for entity, (x, y) in ENTITY_LAYOUT.items():
        draw_entity(draw, body_font, entity, x, y)
    draw_relationships(draw)

    img.save(OUTPUT_PATH)
    print(f"Saved ER diagram to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
