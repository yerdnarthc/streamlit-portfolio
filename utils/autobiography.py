"""Safe interactive and PDF helpers for the autobiography section."""

import ast
from dataclasses import dataclass
import re

from fpdf import FPDF


@dataclass(frozen=True)
class AutobiographyChapter:
    """One chronological reading section derived from the source narrative."""

    number: int
    title: str
    markdown: str


@dataclass(frozen=True)
class AutobiographyStructure:
    """Editorial structure layered over the student's unchanged prose."""

    title: str
    preface: str
    chapters: tuple[AutobiographyChapter, ...]


_CHAPTER_MARKERS = (
    ("Origins", "Born on"),
    ("Moving and growing", "By around year 2018"),
    ("Choosing Computer Science", "During Senior High School"),
    ("College", "Then, here comes College"),
    ("The present", "Computers really fascinate me"),
)


def structure_autobiography(markdown: str) -> AutobiographyStructure:
    """Add chronological chapters without rewriting the source paragraphs."""
    heading = re.match(r"^#\s+(.+?)\s*(?:\n+|$)", markdown)
    title = heading.group(1) if heading else "Autobiography"
    body = markdown[heading.end() :] if heading else markdown
    blocks = [block.strip() for block in re.split(r"\n\s*\n", body) if block.strip()]

    marker_positions: list[int] = []
    for _, marker in _CHAPTER_MARKERS:
        matches = [index for index, block in enumerate(blocks) if block.startswith(marker)]
        if len(matches) != 1:
            return AutobiographyStructure(title, body.strip(), ())
        marker_positions.append(matches[0])

    if marker_positions != sorted(marker_positions):
        return AutobiographyStructure(title, body.strip(), ())

    chapter_at = {
        position: chapter_title
        for position, (chapter_title, _) in zip(marker_positions, _CHAPTER_MARKERS)
    }

    preface_blocks: list[str] = []
    grouped_chapters: list[tuple[str, list[str]]] = []
    for index, block in enumerate(blocks):
        chapter_title = chapter_at.get(index)
        if chapter_title:
            grouped_chapters.append((chapter_title, [block]))
        elif grouped_chapters:
            grouped_chapters[-1][1].append(block)
        else:
            preface_blocks.append(block)

    chapters = tuple(
        AutobiographyChapter(number, chapter_title, "\n\n".join(chapter_blocks))
        for number, (chapter_title, chapter_blocks) in enumerate(
            grouped_chapters, start=1
        )
    )
    return AutobiographyStructure(title, "\n\n".join(preface_blocks), chapters)


def split_closing_print(markdown: str) -> tuple[str, str | None]:
    """Separate a trailing standalone print statement from autobiography prose."""
    matches = list(re.finditer(r"(?m)^print\(.+\);?\s*$", markdown))
    if not matches:
        return markdown, None

    closing_match = matches[-1]
    if markdown[closing_match.end() :].strip():
        return markdown, None

    return markdown[: closing_match.start()].rstrip(), closing_match.group().strip()


def run_print_statement(source: str) -> str:
    """Return the output of one literal-string print call without executing code."""
    try:
        program = ast.parse(source, mode="exec")
    except SyntaxError as error:
        raise ValueError("Enter a valid print statement.") from error

    if len(program.body) != 1 or not isinstance(program.body[0], ast.Expr):
        raise ValueError("Only one print statement can be run here.")

    call = program.body[0].value
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "print"
        or len(call.args) != 1
        or call.keywords
        or not isinstance(call.args[0], ast.Constant)
        or not isinstance(call.args[0].value, str)
    ):
        raise ValueError("Use print with one quoted message.")

    return call.args[0].value


def _core_font_text(text: str) -> str:
    """Normalize typography that the standard Helvetica PDF font cannot encode."""
    replacements = str.maketrans(
        {
            "\u2014": "-",
            "\u2013": "-",
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
        }
    )
    return text.translate(replacements).encode("latin-1", "replace").decode("latin-1")


def build_autobiography_pdf(markdown: str) -> bytes:
    """Create a one-inch-margin PDF using the standard Helvetica font."""
    pdf = FPDF()
    one_inch = 25.4
    pdf.set_margins(one_inch, one_inch, one_inch)
    pdf.set_auto_page_break(auto=True, margin=one_inch)
    pdf.add_page()
    pdf.set_title("Arth Andrey C. Endrina — Autobiography")

    for raw_line in markdown.splitlines():
        heading = raw_line.startswith("#")
        text = re.sub(r"^#{1,6}\s*", "", raw_line)
        text = text.replace("***", "").replace("**", "").replace("`", "")
        text = _core_font_text(text)

        if not text:
            pdf.ln(4)
            continue

        pdf.set_font("Helvetica", size=16 if heading else 10)
        pdf.multi_cell(0, 8 if heading else 6, text)

    return bytes(pdf.output())
