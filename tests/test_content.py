from pathlib import Path
import tempfile
import unittest

from utils.autobiography import (
    build_autobiography_pdf,
    run_print_statement,
    structure_autobiography,
)
from utils.content import load_markdown, parse_skills_markdown, remove_image_markdown
from components.portfolio import parse_portfolio_projects


class ContentTests(unittest.TestCase):
    def test_structure_autobiography_builds_chapters_without_changing_prose(self):
        source = (
            "# My Autobiography\n\n"
            "A human-written preface.\n\n"
            "Born on a September morning.\n\n"
            "My childhood continued.\n\n"
            "By around year 2018, we moved.\n\n"
            "During Senior High School days, I chose a course.\n\n"
            "Then, here comes College.\n\n"
            "Computers really fascinate me.\n\n"
            "This is my life."
        )

        structure = structure_autobiography(source)

        self.assertEqual(structure.title, "My Autobiography")
        self.assertEqual(
            [chapter.title for chapter in structure.chapters],
            [
                "Origins",
                "Moving and growing",
                "Choosing Computer Science",
                "College",
                "The present",
            ],
        )
        reconstructed = "\n\n".join(
            [structure.preface, *(chapter.markdown for chapter in structure.chapters)]
        )
        self.assertEqual(reconstructed, source.split("\n\n", maxsplit=1)[1])

    def test_structure_autobiography_rejects_incomplete_or_reordered_markers(self):
        preface = "# My Autobiography\n\nA human-written preface.\n\n"
        valid_blocks = [
            "Born on a September morning.",
            "By around year 2018, we moved.",
            "During Senior High School days, I chose a course.",
            "Then, here comes College.",
            "Computers really fascinate me.",
        ]
        invalid_variants = {
            "missing": valid_blocks[:2] + valid_blocks[3:],
            "duplicate": valid_blocks + [valid_blocks[-1]],
            "reordered": [valid_blocks[0], valid_blocks[2], valid_blocks[1], *valid_blocks[3:]],
        }

        for case, blocks in invalid_variants.items():
            with self.subTest(case=case):
                structure = structure_autobiography(preface + "\n\n".join(blocks))
                self.assertEqual(structure.chapters, ())

    def test_portfolio_groups_follow_source_headings(self):
        projects = parse_portfolio_projects(Path('contents/my-portfolio.md').read_text(encoding='utf-8'))
        self.assertEqual([p.title for p in projects.values() if p.group == 'More Projects'],
                         ['BantAI Buddy Extension', 'VWSim: Vacuum World Agent Simulator'])
        self.assertEqual(len([p for p in projects.values() if p.group == 'Featured Projects']), 3)

    def test_portfolio_group_can_change_and_be_unassigned(self):
        source = '# More Projects\n## 1.) DeskDuck\n### Overview\nOriginal text.'
        self.assertEqual(parse_portfolio_projects(source)['DeskDuck'].group, 'More Projects')
        self.assertIsNone(parse_portfolio_projects(source.replace('# More Projects', '# Other'))['DeskDuck'].group)

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
        asset_dir = Path("assets")

        projects = parse_portfolio_projects(markdown, asset_dir)

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

    def test_parse_portfolio_projects_slug_is_url_safe(self) -> None:
        markdown = Path("contents/my-portfolio.md").read_text(encoding="utf-8")
        asset_dir = Path("assets")

        projects = parse_portfolio_projects(markdown, asset_dir)

        for title, p in projects.items():
            self.assertRegex(p.slug, r"^[a-z0-9_]+$", msg=f"Slug not URL-safe for '{title}'")

    def test_parse_portfolio_projects_body_has_no_raw_image_lines(self) -> None:
        markdown = Path("contents/my-portfolio.md").read_text(encoding="utf-8")
        asset_dir = Path("assets")

        projects = parse_portfolio_projects(markdown, asset_dir)

        for title, p in projects.items():
            self.assertNotIn("![", p.body, msg=f"Image markdown not stripped for '{title}'")
