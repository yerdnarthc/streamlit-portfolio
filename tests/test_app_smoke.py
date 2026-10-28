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

    def test_portfolio_page_shows_project_tabs_and_preview(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Portfolio").run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 4)
        self.assertTrue(any("DeskDuck" in heading.value for heading in app.subheader))
        self.assertGreaterEqual(len(app.image), 1)

    def test_portfolio_page_switches_between_project_dossiers(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Portfolio").run()
        app.button(key="explore_n_queens_hill_climbing_visualizer").click().run()

        self.assertTrue(any("N-Queens Hill Climbing Visualizer" in item.value for item in app.subheader))
        app.button(key="explore_vwsim_vacuum_world_agent_simulator").click().run()

        self.assertFalse(app.exception)
        self.assertTrue(
            any("VWSim: Vacuum World Agent Simulator" in item.value for item in app.subheader)
        )
