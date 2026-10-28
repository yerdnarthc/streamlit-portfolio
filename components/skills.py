"""Skills section renderer for the portfolio."""

from pathlib import Path

import streamlit as st

from utils.content import load_markdown, parse_skills_markdown


def render_skills(content_dir: Path) -> None:
    """Render the student's self-assessed skills, ratings, and explanations."""
    source = load_markdown(content_dir / "my-skills.md")
    if source is None:
        st.warning("The skills content could not be loaded.")
        return

    frame = parse_skills_markdown(source)
    if frame.empty:
        st.warning("No valid skill ratings were found in the skills content.")
        return

    st.header("Skills")
    st.caption("These ratings are my current self-assessment on a scale of 1–10.")
    st.divider()

    rating_column, highlight_column = st.columns([1, 2], gap="large")
    with rating_column:
        minimum_rating = st.slider(
            "Minimum skill rating", min_value=1, max_value=10, value=1
        )
    with highlight_column:
        highlighted_skill = st.selectbox("Highlight a skill", frame["Skill"].tolist())
        show_explanations = st.checkbox("Show how I use each skill", value=True)
        if show_explanations:
            explanation = frame.loc[
                frame["Skill"] == highlighted_skill, "How I Use It"
            ].iloc[0]
            st.subheader(highlighted_skill)
            st.write(explanation)

    filtered_frame = frame.loc[frame["Rating"] >= minimum_rating]
    if filtered_frame.empty:
        st.info("No skills match that minimum rating.")
        return

    st.divider()
    highest_rating, average_rating = st.columns(2)
    with highest_rating:
        st.metric("Highest Skill Rating", int(filtered_frame["Rating"].max()))
    with average_rating:
        st.metric("Average Skill Rating", f"{filtered_frame['Rating'].mean():.1f}/10")

    st.divider()
    st.subheader("Ratings")
    st.vega_lite_chart(
        filtered_frame[["Skill", "Rating"]],
        {
            "height": 420,
            "mark": {"type": "bar", "color": "#965a5a"},
            "encoding": {
                "x": {
                    "field": "Skill",
                    "type": "nominal",
                    "sort": None,
                    "axis": {
                        "labelAngle": 0,
                        "labelExpr": "split(datum.label, ' ')",
                        "labelLimit": 0,
                        "labelPadding": 10,
                        "title": None,
                    },
                },
                "y": {
                    "field": "Rating",
                    "type": "quantitative",
                    "scale": {"domain": [0, 10]},
                    "axis": {"title": "Self-assessed rating / 10", "tickMinStep": 1},
                },
                "tooltip": [{"field": "Skill"}, {"field": "Rating"}],
            },
            "config": {"font": "JetBrainsMono Nerd Font"},
        },
        width="stretch",
    )

    st.divider()
    st.subheader("Skills at a glance")
    table_columns = ["Skill", "Rating"]
    if show_explanations:
        table_columns.append("How I Use It")

    table_frame = filtered_frame[table_columns].copy()
    table_frame["Rating"] = table_frame["Rating"].astype(str)
    st.table(
        table_frame,
        border="horizontal",
        hide_index=True,
        width="stretch",
        height="content",
        alt="A table listing skills, self-assessed ratings, and how each skill is used.",
    )
