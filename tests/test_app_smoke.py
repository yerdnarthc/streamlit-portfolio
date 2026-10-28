from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
    def test_portfolio_empty_group_and_stale_selection_recover(self):
        def fixture_app():
            from pathlib import Path
            import streamlit as st
            from components.portfolio import parse_portfolio_projects, _portfolio_theater
            projects = parse_portfolio_projects(
                '# Featured Projects\n## 1.) DeskDuck\n### Overview\nFixture overview.'
            )
            if 'portfolio_group_selections' not in st.session_state:
                st.session_state.portfolio_group_selections = {'Featured Projects': 'Removed project'}
            _portfolio_theater(projects, Path('assets'))

        app = AppTest.from_function(fixture_app).run()
        self.assertFalse(app.exception)
        self.assertTrue(any(h.value == 'DeskDuck' for h in app.subheader))
        app.segmented_control(key='portfolio_group').set_value('More Projects').run()
        self.assertFalse(app.exception)
        self.assertTrue(any('No projects are available in More Projects' in item.value for item in app.info))
        self.assertEqual(len(app.subheader), 0)
        app.segmented_control(key='portfolio_group').set_value('Featured Projects').run()
        self.assertTrue(any(h.value == 'DeskDuck' for h in app.subheader))

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

    def test_portfolio_page_renders_without_exception(self) -> None:
        """Portfolio route renders the theater; no Python exception is raised."""
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Portfolio").run()

        self.assertFalse(app.exception)

    def test_portfolio_page_shows_header(self) -> None:
        """Portfolio route starts with the Portfolio header."""
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Portfolio").run()

        self.assertFalse(app.exception)
        self.assertTrue(any("Portfolio" in h.value for h in app.header))

    def test_portfolio_page_switches_between_project_dossiers(self) -> None:
        """Visitor can select different project capsules in the theater rail."""
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Portfolio").run()
        self.assertFalse(app.exception)

        # Switch to N-Queens Visualizer
        app.button(key="explore_n_queens_hill_climbing_visualizer").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("N-Queens Hill Climbing Visualizer" in el.value for el in list(app.subheader) + list(app.markdown)))

        # Switch to VWSim
        self.assertFalse(any(b.key == 'explore_vwsim_vacuum_world_agent_simulator' for b in app.button))
        app.segmented_control(key='portfolio_group').set_value('More Projects').run()
        app.button(key="explore_vwsim_vacuum_world_agent_simulator").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(
            any("VWSim: Vacuum World Agent Simulator" in el.value for el in list(app.subheader) + list(app.markdown))
        )
        app.segmented_control(key='portfolio_group').set_value('Featured Projects').run()
        self.assertTrue(any('N-Queens Hill Climbing Visualizer' in el.value for el in app.subheader))
