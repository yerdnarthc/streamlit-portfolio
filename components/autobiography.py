"""Render the student's full autobiography."""

from pathlib import Path

import streamlit as st

from utils.autobiography import build_autobiography_pdf, run_print_statement, split_closing_print
from utils.content import load_markdown


def render_autobiography(content_dir: Path) -> None:
    """Display and offer the unmodified autobiography Markdown."""
    st.header("Autobiography")
    autobiography = load_markdown(content_dir / "my-autobiography.md")
    if autobiography is None:
        st.warning("Autobiography content could not be loaded.")
        return

    narrative, closing_code = split_closing_print(autobiography)
    st.markdown(narrative)

    if closing_code:
        st.divider()
        st.subheader("Run the closing program")
        code = st.text_area(
            "Closing Python code",
            value=closing_code,
            height=72,
            key="autobiography_closing_code",
        )
        if st.button("Run", icon=":material/play_arrow:", key="run_autobiography_code"):
            try:
                st.session_state.autobiography_code_output = run_print_statement(code)
            except ValueError as error:
                st.session_state.pop("autobiography_code_output", None)
                st.error(str(error))

        if output := st.session_state.get("autobiography_code_output"):
            st.code(output, language="text")

    font_path = Path(__file__).parents[1] / "static" / "fonts" / "JetBrainsMonoNerdFont-Regular.ttf"
    st.download_button(
        "Download my autobiography as PDF",
        data=build_autobiography_pdf(autobiography, font_path),
        file_name="arth-endrina-autobiography.pdf",
        mime="application/pdf",
    )
