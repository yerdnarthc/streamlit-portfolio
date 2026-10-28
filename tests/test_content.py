from pathlib import Path
import tempfile
import unittest

from utils.autobiography import build_autobiography_pdf, run_print_statement
from utils.content import load_markdown, parse_skills_markdown, remove_image_markdown
from components.portfolio import parse_portfolio_projects


class ContentTests(unittest.TestCase):
    def test_load_markdown_returns_text_for_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text("# Hello", encoding="utf-8")

            self.assertEqual(load_markdown(path), "# Hello")

    def test_load_markdown_returns_none_for_missing_file(self) -> None:
        self.assertIsNone(load_markdown(Path("does-not-exist.md")))

    def test_remove_image_markdown_removes_local_image_line(self) -> None:
        text = "Intro\n![Preview](../assets/preview.png)\nOutro"

        self.assertEqual(remove_image_markdown(text), "Intro\nOutro")

    def test_parse_skills_markdown_reads_valid_rows_only(self) -> None:
        markdown = (
            "| Skill | Rating | How I Use It |\n"
            "| --- | ---: | --- |\n"
            "| Python | 7 | APIs |\n"
            "| Bad | eleven | Invalid |"
        )

        frame = parse_skills_markdown(markdown)

        self.assertEqual(
            frame.to_dict("records"),
            [{"Skill": "Python", "Rating": 7, "How I Use It": "APIs"}],
        )

    def test_run_print_statement_returns_a_literal_message_only(self) -> None:
        self.assertEqual(
            run_print_statement('print("Thanks for reading!")'), "Thanks for reading!"
        )

        with self.assertRaises(ValueError):
            run_print_statement("import os")

    def test_build_autobiography_pdf_returns_pdf_bytes(self) -> None:
        pdf = build_autobiography_pdf("# My Autobiography\n\nThis is a short test.")

        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Helvetica", pdf)

    def test_parse_portfolio_projects_preserves_the_five_known_sections(self) -> None:
        markdown = Path("contents/my-portfolio.md").read_text(encoding="utf-8")

        projects = parse_portfolio_projects(markdown)

        self.assertEqual(
            list(projects),
            [
                "DeskDuck",
                "Custom Neofetch-Style Github Profile",
                "N-Queens Hill Climbing Visualizer",
                "BantAI Buddy Extension",
                "VWSim: Vacuum World Agent Simulator",
            ],
        )
        self.assertIn("Solo developer", projects["DeskDuck"].body)
