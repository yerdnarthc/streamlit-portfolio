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

    def test_autobiography_timeline_uses_readable_editorial_measure(self) -> None:
        css = Path("assets/styles/app.css").read_text(encoding="utf-8")

        self.assertIn('[class*="st-key-autobio_chapter_"]', css)
        self.assertIn(".st-key-autobiography_timeline", css)
        self.assertIn("max-width: 72ch", css)
        self.assertIn("font-size: clamp(3rem", css)

    def test_motion_runtime_has_one_observer_pair_and_explicit_cleanup(self) -> None:
        script = Path("ui/motion/motion.js").read_text(encoding="utf-8")

        self.assertEqual(script.count("new MutationObserver"), 1)
        self.assertEqual(script.count("new IntersectionObserver"), 1)
        self.assertIn("abortController.abort()", script)
        self.assertIn("mutationObserver.disconnect()", script)
        self.assertIn("intersectionObserver?.disconnect()", script)
        self.assertIn("return () =>", script)

    def test_motion_is_progressive_and_has_a_reduced_motion_strategy(self) -> None:
        app_css = Path("assets/styles/app.css").read_text(encoding="utf-8")
        motion_css = Path("ui/motion/motion.css").read_text(encoding="utf-8")

        self.assertIn("html.portfolio-motion-ready", motion_css)
        self.assertIn("prefers-reduced-motion: reduce", motion_css)
        self.assertIn("--motion-duration-medium: 420ms", motion_css)
        self.assertIn("--motion-duration-slow: 720ms", motion_css)
        self.assertNotIn("transition: all", app_css + motion_css)

    def test_about_portrait_reveal_uses_the_stable_frame(self) -> None:
        script = Path("ui/motion/motion.js").read_text(encoding="utf-8")

        self.assertIn('selector: ".st-key-about_photo_frame"', script)
        self.assertIn("eager: true", script)
        self.assertNotIn(
            '.st-key-about_photo_frame [data-testid="stImage"]',
            script,
        )

    def test_feedback_success_has_a_dedicated_delight_sequence(self) -> None:
        component = Path("components/feedback.py").read_text(encoding="utf-8")
        script = Path("ui/motion/motion.js").read_text(encoding="utf-8")
        motion_css = Path("ui/motion/motion.css").read_text(encoding="utf-8")

        self.assertIn('key="feedback_success"', component)
        self.assertIn('key="feedback_error"', component)
        self.assertIn('selector: ".st-key-feedback_success"', script)
        self.assertIn('motion: "feedback-success"', script)
        self.assertIn("@keyframes feedback-signal-trace", motion_css)
        self.assertIn("@keyframes feedback-submit-release", motion_css)
        self.assertIn("prefers-reduced-motion: reduce", motion_css)
