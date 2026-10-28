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
