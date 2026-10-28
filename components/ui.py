"""Shared presentation helpers for the Streamlit portfolio."""

import base64
from pathlib import Path

import streamlit as st


_FONT_SOURCES = {
    "__JETBRAINS_MONO_FONT__": "JetBrainsMonoNerdFont-Regular.ttf",
    "__GEIST_BOLD_FONT__": "Geist-Bold.woff2",
}


def _font_data_uri(font_path: Path) -> str:
    """Return a self-contained data URI for a local font file."""
    font_bytes = font_path.read_bytes()
    encoded_font = base64.b64encode(font_bytes).decode("ascii")
    mime_type = "font/woff2" if font_path.suffix == ".woff2" else "font/ttf"
    return f"data:{mime_type};base64,{encoded_font}"


def apply_visual_system(stylesheet: Path) -> None:
    """Inject the trusted local stylesheet and its self-hosted font assets."""
    try:
        css = stylesheet.read_text(encoding="utf-8")
    except OSError:
        st.warning("The portfolio stylesheet could not be loaded.")
        return

    font_directory = stylesheet.parent.parent / "fonts"
    for marker, filename in _FONT_SOURCES.items():
        font_path = font_directory / filename
        if not font_path.is_file():
            st.warning(f"The {filename} font file could not be loaded.")
            css = css.replace(marker, "")
            continue
        css = css.replace(marker, _font_data_uri(font_path))

    st.html(css)
