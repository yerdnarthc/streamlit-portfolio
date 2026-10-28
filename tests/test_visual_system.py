from pathlib import Path
import unittest


class VisualSystemTests(unittest.TestCase):
    def test_theme_uses_only_the_confirmed_base_colors(self) -> None:
        theme = Path(".streamlit/config.toml").read_text(encoding="utf-8")

        self.assertIn('base = "dark"', theme)
        self.assertIn('primaryColor = "#965a5a"', theme)
        self.assertIn('backgroundColor = "#191919"', theme)
        self.assertIn('textColor = "#bbbaba"', theme)

    def test_stylesheet_keeps_surfaces_sharp_and_respects_reduced_motion(self) -> None:
        css = Path("assets/styles/app.css").read_text(encoding="utf-8")

        self.assertIn("border-radius: 0", css)
        self.assertIn("prefers-reduced-motion", css)

    def test_local_font_assets_exist(self) -> None:
        font_directory = Path("assets/fonts")

        self.assertTrue((font_directory / "JetBrainsMonoNerdFont-Regular.ttf").is_file())
        self.assertTrue((font_directory / "Geist-Bold.woff2").is_file())
