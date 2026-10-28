from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
    def test_app_shows_portfolio_title_and_about_page(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()

        self.assertFalse(app.exception)
        self.assertTrue(any("Arth Andrey" in title.value for title in app.title))
        self.assertTrue(any("About" in header.value for header in app.header))

    def test_skills_page_shows_data_and_chart(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Skills").run()

        self.assertFalse(app.exception)
        self.assertGreaterEqual(len(app.dataframe), 1)
        self.assertTrue(any("Skill" in metric.label for metric in app.metric))

    def test_autobiography_code_panel_runs_the_closing_message(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Autobiography").run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.text_area), 1)
        self.assertEqual(len(app.button), 1)
        app.button[0].click().run()
        self.assertTrue(
            any("Thank you for taking your time" in code.value for code in app.code)
        )
