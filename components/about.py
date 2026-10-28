"""Render the student's About section as an editorial landing page."""

from pathlib import Path

import streamlit as st

from utils.content import load_markdown, parse_markdown_sections, remove_image_markdown


REQUIRED_PROFILE_SECTIONS = ("Name", "Program", "Year", "Short Biography")


def render_about(content_dir: Path, asset_dir: Path) -> None:
    """Display the prepared profile information and photo without rewriting it."""
    about_markdown = load_markdown(content_dir / "about-me.md")
    if about_markdown is None:
        st.warning("About-me content could not be loaded.")
        return

    _, profile = parse_markdown_sections(about_markdown)
    if any(not profile.get(section) for section in REQUIRED_PROFILE_SECTIONS):
        st.warning("The structured profile details could not be prepared.")
        st.markdown(remove_image_markdown(about_markdown))
        return

    profile_photo = asset_dir / "profile" / "me.png"

    with st.container(key="about_page"):
        with st.container(key="about_hero"):
            identity_column, photo_column = st.columns(
                [1.35, 0.65],
                gap="large",
                vertical_alignment="center",
                wrap=True,
            )

            with identity_column:
                with st.container(key="about_identity"):
                    st.header(profile["Name"])

                    with st.container(key="about_fact_program"):
                        st.caption("Program")
                        st.markdown(profile["Program"])

                    with st.container(key="about_fact_year"):
                        st.caption("Year")
                        st.markdown(profile["Year"])

            with photo_column:
                with st.container(key="about_photo_frame"):
                    if profile_photo.is_file():
                        st.image(
                            profile_photo,
                            alt=f"{profile['Name']}'s profile photo",
                            width="stretch",
                        )
                    else:
                        st.warning("Profile photo could not be loaded.")

        with st.container(key="about_biography"):
            section_column, biography_column = st.columns(
                [0.8, 3.2], gap="large", vertical_alignment="top", wrap=True
            )
            with section_column:
                st.text("PROFILE")
            with biography_column:
                st.subheader("Short Biography")
                st.markdown(profile["Short Biography"])
