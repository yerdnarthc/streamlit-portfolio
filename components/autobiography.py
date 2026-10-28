"""Render the student's full autobiography."""

from pathlib import Path

import streamlit as st

from utils.autobiography import (
    build_autobiography_pdf,
    run_print_statement,
    split_closing_print,
    structure_autobiography,
)
from utils.content import load_markdown


def render_autobiography(content_dir: Path) -> None:
    """Display and offer the unmodified autobiography Markdown."""
    autobiography = load_markdown(content_dir / "my-autobiography.md")
    if autobiography is None:
        st.warning("Autobiography content could not be loaded.")
        return

    narrative, closing_code = split_closing_print(autobiography)
    structure = structure_autobiography(narrative)

    with st.container(key="autobiography_page"):
        st.header(structure.title)

        if structure.chapters:
            if structure.preface:
                with st.container(key="autobiography_preface"):
                    st.markdown(structure.preface)

            with st.container(key="autobiography_timeline"):
                for chapter in structure.chapters:
                    with st.container(key=f"autobio_chapter_{chapter.number:02d}"):
                        number_column, narrative_column = st.columns(
                            [1, 4], gap="large", vertical_alignment="top", wrap=True
                        )
                        with number_column:
                            st.text(f"{chapter.number:02d}")
                        with narrative_column:
                            st.subheader(chapter.title)
                            st.markdown(chapter.markdown)
        else:
            st.markdown(structure.preface)

        if closing_code:
            st.divider()
            with st.container(border=True, key="autobiography_code_panel"):
                code = st.text_area(
                    "Closing Python code",
                    value=closing_code,
                    height=72,
                    key="autobiography_closing_code",
                    label_visibility="collapsed",
                )
                with st.container(horizontal_alignment="right"):
                    run_code = st.button(
                        "Run",
                        icon=":material/play_arrow:",
                        key="run_autobiography_code",
                        width="content",
                    )

            if run_code:
                try:
                    st.session_state.autobiography_code_output = run_print_statement(code)
                except ValueError as error:
                    st.session_state.pop("autobiography_code_output", None)
                    st.error(str(error))

            if output := st.session_state.get("autobiography_code_output"):
                st.code(output, language="text")

        with st.container(key="autobiography_download", horizontal_alignment="right"):
            st.download_button(
                "Download my autobiography as PDF",
                data=build_autobiography_pdf(autobiography),
                file_name="arth-endrina-autobiography.pdf",
                mime="application/pdf",
                icon=":material/download:",
            )
