from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
    def test_feedback_page_shows_form_inputs(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run()

        app.sidebar.radio[0].set_value("Feedback").run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.text_input), 1)
        self.assertEqual(len(app.text_area), 1)
        self.assertEqual(len(app.radio), 2)
        self.assertEqual(len(app.multiselect), 1)
        self.assertEqual(len(app.form_submit_button), 1)

    def test_feedback_form_requires_name_and_message(self) -> None:
        invalid_submissions = [
            ("   ", "The message is present."),
            ("Alex", "   "),
        ]

        for visitor_name, message in invalid_submissions:
            with self.subTest(visitor_name=visitor_name, message=message):
                app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run()
                app.sidebar.radio[0].set_value("Feedback").run()

                app.text_input[0].set_value(visitor_name)
                app.text_area[0].set_value(message)
                app.form_submit_button[0].click().run()

                self.assertFalse(app.exception)
                self.assertTrue(
                    any(
                        item.value == "Please enter your name and a message."
                        for item in app.error
                    )
                )
                self.assertEqual(len(app.success), 0)

    def test_feedback_form_confirms_valid_submission_locally(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run()
        app.sidebar.radio[0].set_value("Feedback").run()

        app.text_input[0].set_value("  Alex  ")
        app.text_area[0].set_value("Great portfolio.")
        app.form_submit_button[0].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.error), 0)
        self.assertTrue(any("Alex" in item.value for item in app.success))
        confirmation = app.session_state["feedback_confirmation"]
        self.assertIn("Alex", confirmation)
        self.assertNotIn("Great portfolio.", confirmation)
        for response_key in (
            "feedback_name",
            "feedback_topic",
            "feedback_sections",
            "feedback_message",
        ):
            self.assertNotIn(response_key, app.session_state)

        app.sidebar.radio[0].set_value("About").run()
        app.sidebar.radio[0].set_value("Feedback").run()
        self.assertTrue(
            any(
                item.value == confirmation
                for item in app.success
            )
        )

    def test_portfolio_previous_next_respect_group_boundaries(self):
        app = AppTest.from_file(Path(__file__).parents[1] / 'app.py').run()
        app.sidebar.radio[0].set_value('Portfolio').run()
        self.assertTrue(app.button(key='pf_previous').disabled)
        app.button(key='pf_next').click().run()
        self.assertTrue(any('Custom Neofetch' in h.value for h in app.subheader))
        app.button(key='pf_next').click().run()
        self.assertTrue(app.button(key='pf_next').disabled)
        app.button(key='pf_show_more').click().run()
        self.assertTrue(app.button(key='pf_previous').disabled)
        app.button(key='pf_next').click().run()
        self.assertTrue(any('VWSim' in h.value for h in app.subheader))
        self.assertTrue(app.button(key='pf_next').disabled)
        app.button(key='pf_previous').click().run()
        self.assertTrue(any('BantAI Buddy' in h.value for h in app.subheader))
        self.assertFalse(app.exception)

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
        app.button(key='pf_show_more').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('No projects are available in More Projects' in item.value for item in app.info))
        self.assertTrue(any(h.value == 'More Projects' for h in app.subheader))
        self.assertFalse(any(h.value == 'DeskDuck' for h in app.subheader))
        app.button(key='pf_show_featured').click().run()
        self.assertTrue(any(h.value == 'DeskDuck' for h in app.subheader))

    def test_app_shows_portfolio_title_and_about_page(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()

        self.assertFalse(app.exception)
        self.assertTrue(any("Arth Andrey" in title.value for title in app.title))
        self.assertTrue(
            any("Arth Andrey C. Endrina" == header.value for header in app.header)
        )
        self.assertTrue(
            any("Short Biography" == heading.value for heading in app.subheader)
        )
        rendered_markdown = "\n".join(item.value for item in app.markdown)
        self.assertIn("Bachelor of Science in Computer Science", rendered_markdown)
        self.assertIn("3rd Year", rendered_markdown)
        self.assertIn("passionate about building practical software", rendered_markdown)
        self.assertEqual(len(app.image), 1)

    def test_skills_page_shows_data_and_chart(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Skills").run()

        self.assertFalse(app.exception)
        self.assertGreaterEqual(len(app.dataframe), 1)
        self.assertTrue(any("Skill" in metric.label for metric in app.metric))

    def test_skills_page_updates_highlight_and_filter(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

        app.run()
        app.sidebar.radio[0].set_value("Skills").run()
        self.assertFalse(app.exception)

        # Highlight C#
        app.selectbox[0].set_value("C#").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("C#" in h.value for h in app.subheader))

        # Filter minimum rating to 9 (AI-Assisted Software Development only)
        app.slider[0].set_value(9).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe[0].value), 1)

    def test_autobiography_page_renders_editorial_chapters(self) -> None:
        app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run()

        app.sidebar.radio[0].set_value("Autobiography").run()

        self.assertFalse(app.exception)
        self.assertTrue(any(h.value == "My Autobiography" for h in app.header))
        self.assertEqual(
            [heading.value for heading in app.subheader],
            [
                "Origins",
                "Moving and growing",
                "Choosing Computer Science",
                "College",
                "The present",
            ],
        )
        self.assertTrue(
            any("Born on the 1st of September" in item.value for item in app.markdown)
        )
        self.assertEqual([item.value for item in app.text], ["01", "02", "03", "04", "05"])

        source = Path("contents/my-autobiography.md").read_text(encoding="utf-8")
        narrative = source.rsplit("\n\nprint(", maxsplit=1)[0]
        source_paragraphs = [
            paragraph.strip()
            for paragraph in narrative.split("\n\n")[1:]
            if paragraph.strip()
        ]
        rendered_markdown = "\n\n".join(item.value for item in app.markdown)
        for paragraph in source_paragraphs:
            self.assertEqual(rendered_markdown.count(paragraph), 1)

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
        self.assertTrue(any(h.value == "Featured Projects" for h in app.subheader))
        self.assertEqual(len(app.segmented_control), 0)
        self.assertEqual(app.button(key="pf_show_more").label, "More Projects")

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
        app.button(key='pf_show_more').click().run()
        app.button(key="explore_vwsim_vacuum_world_agent_simulator").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(
            any("VWSim: Vacuum World Agent Simulator" in el.value for el in list(app.subheader) + list(app.markdown))
        )
        app.button(key='pf_show_featured').click().run()
        self.assertTrue(any('N-Queens Hill Climbing Visualizer' in el.value for el in app.subheader))
