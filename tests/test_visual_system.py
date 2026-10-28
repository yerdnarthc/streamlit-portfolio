from pathlib import Path
import unittest
from unittest.mock import patch

from components.ui import apply_visual_system


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
        font_directory = Path("static/fonts")

        self.assertTrue((font_directory / "JetBrainsMonoNerdFont-Regular.ttf").is_file())
        self.assertTrue((font_directory / "Geist-Bold.woff2").is_file())

    def test_theme_registers_the_required_self_hosted_fonts(self) -> None:
        theme = Path(".streamlit/config.toml").read_text(encoding="utf-8")

        self.assertIn("enableStaticServing = true", theme)
        self.assertIn('font = "JetBrainsMono Nerd Font"', theme)
        self.assertIn('headingFont = "Geist"', theme)
        self.assertIn('codeFont = "JetBrainsMono Nerd Font"', theme)
        self.assertIn('family = "JetBrainsMono Nerd Font"', theme)
        self.assertIn('url = "app/static/fonts/JetBrainsMonoNerdFont-Regular.ttf"', theme)
        self.assertIn('family = "Geist"', theme)
        self.assertIn('url = "app/static/fonts/Geist-Bold.woff2"', theme)

        font_directory = Path("static/fonts")
        self.assertTrue((font_directory / "JetBrainsMonoNerdFont-Regular.ttf").is_file())
        self.assertTrue((font_directory / "Geist-Bold.woff2").is_file())

    def test_visual_system_sends_stylesheet_as_a_style_element(self) -> None:
        stylesheet = Path("assets/styles/app.css")

        with patch("components.ui.st.html") as render_html:
            apply_visual_system(stylesheet)

        rendered_css = render_html.call_args.args[0]
        self.assertTrue(rendered_css.startswith("<style>"))
        self.assertTrue(rendered_css.endswith("</style>"))

    def test_sidebar_does_not_override_streamlit_icon_fonts(self) -> None:
        css = Path("assets/styles/app.css").read_text(encoding="utf-8")

        self.assertNotIn('[data-testid="stSidebar"] *', css)
