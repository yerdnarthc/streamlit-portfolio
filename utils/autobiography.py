"""Safe interactive and PDF helpers for the autobiography section."""

import ast
from pathlib import Path
import re

from fpdf import FPDF


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


def build_autobiography_pdf(markdown: str, font_path: Path) -> bytes:
    """Create a Unicode-capable PDF from the unmodified autobiography Markdown."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.add_font("PortfolioMono", fname=str(font_path))
    pdf.set_title("Arth Andrey C. Endrina — Autobiography")

    for raw_line in markdown.splitlines():
        heading = raw_line.startswith("#")
        text = re.sub(r"^#{1,6}\s*", "", raw_line)
        text = text.replace("***", "").replace("**", "").replace("`", "")

        if not text:
            pdf.ln(4)
            continue

        pdf.set_font("PortfolioMono", size=16 if heading else 10)
        pdf.multi_cell(0, 8 if heading else 6, text)

    return bytes(pdf.output())
