"""Load and prepare the student's Markdown content for display."""

from pathlib import Path
import re

import pandas as pd


def load_markdown(path: Path) -> str | None:
    """Return UTF-8 Markdown text, or None when the file is unavailable."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def remove_image_markdown(markdown: str) -> str:
    """Remove Markdown image lines that Streamlit renders separately."""
    return re.sub(
        r"^!\[[^\]]*\]\([^\n]+\)\s*\n?",
        "",
        markdown,
        flags=re.MULTILINE,
    ).strip()


def parse_skills_markdown(markdown: str) -> pd.DataFrame:
    """Parse valid skill rows from the student's three-column Markdown table."""
    rows: list[dict[str, object]] = []

    for line in markdown.splitlines():
        cells = [cell.strip().strip("*") for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in {"Skill", "---"} or set(cells[0]) == {"-"}:
            continue

        try:
            rating = int(cells[1])
        except ValueError:
            continue

        if 1 <= rating <= 10:
            rows.append(
                {"Skill": cells[0], "Rating": rating, "How I Use It": cells[2]}
            )

    return pd.DataFrame(rows, columns=["Skill", "Rating", "How I Use It"])
