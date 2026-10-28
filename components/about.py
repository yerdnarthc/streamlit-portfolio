"""Render the student's About section."""

from pathlib import Path

import streamlit as st

from utils.content import load_markdown, remove_image_markdown


def render_about(content_dir: Path, asset_dir: Path) -> None:
    """Display the prepared profile information and photo."""
    st.header("About")
    details_column, photo_column = st.columns([3, 2], vertical_alignment="center")

    with details_column:
        about_markdown = load_markdown(content_dir / "about-me.md")
        if about_markdown is None:
            st.warning("About-me content could not be loaded.")
        else:
            st.markdown(remove_image_markdown(about_markdown))

    with photo_column:
        profile_photo = asset_dir / "profile" / "me.png"
        if profile_photo.is_file():
            st.image(profile_photo, caption="Arth Andrey C. Endrina")
        else:
            st.warning("Profile photo could not be loaded.")
