"""Safe interactive and PDF helpers for the autobiography section."""

import ast
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
