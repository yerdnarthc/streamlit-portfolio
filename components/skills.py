"""Skills section renderer for the portfolio."""

from pathlib import Path
import re

import streamlit as st

from utils.content import load_markdown, parse_skills_markdown


def _slugify(title: str) -> str:
    """Return a clean URL-safe slug for widget keys and test selectors."""
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


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

    with st.container(key="skills_page"):
        _render_skills_content(frame)


def _render_skills_content(frame) -> None:
    """Render the prepared skills interface inside its stable page wrapper."""
    st.header("Skills")
    st.caption("These ratings are my current self-assessment on a scale of 1–10.")
    _skills_theater(frame)


@st.fragment
def _skills_theater(frame) -> None:
    """Interactive theater fragment for instant skill filtering and spotlighting."""
    with st.container(key="skills_controls"):
        rating_column, highlight_column = st.columns([1, 2], gap="small")
        with rating_column:
            minimum_rating = st.slider(
                "Minimum skill rating", min_value=1, max_value=10, value=1
            )
        with highlight_column:
            highlighted_skill = st.selectbox(
                "Highlight a skill", frame["Skill"].tolist()
            )
            show_explanations = st.checkbox("Show how I use each skill", value=True)
            if show_explanations:
                skill_row = frame.loc[frame["Skill"] == highlighted_skill].iloc[0]
                explanation = skill_row["How I Use It"]
                rating = int(skill_row["Rating"])
                skill_slug = _slugify(highlighted_skill)
                with st.container(key=f"skills_spotlight_{skill_slug}"):
                    st.subheader(highlighted_skill)
                    st.html(f'<span class="skills-rating-badge">★ Rating: {rating} / 10</span>')
                    st.write(explanation)

    filtered_frame = frame.loc[frame["Rating"] >= minimum_rating]
    if filtered_frame.empty:
        with st.container(key="skills_empty_state"):
            st.info("No skills match that minimum rating.")
        return

    st.divider()
    with st.container(key="skills_metrics"):
        with st.container(key=f"skills_metrics_stage_{minimum_rating}"):
            highest_rating, average_rating = st.columns(2)
            with highest_rating:
                st.metric("Highest Skill Rating", int(filtered_frame["Rating"].max()))
            with average_rating:
                st.metric(
                    "Average Skill Rating", f"{filtered_frame['Rating'].mean():.1f}/10"
                )

    with st.container(key="skills_chart"):
        with st.container(key=f"skills_chart_stage_{minimum_rating}"):
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
                            "axis": {
                                "title": "Self-assessed rating / 10",
                                "tickMinStep": 1,
                            },
                        },
                        "tooltip": [{"field": "Skill"}, {"field": "Rating"}],
                    },
                    "config": {"font": "JetBrainsMono Nerd Font"},
                },
                width="stretch",
            )

    st.divider()
    with st.container(key="skills_table"):
        with st.container(key=f"skills_table_stage_{minimum_rating}"):
            st.subheader("Skills at a glance")
            table_columns = ["Skill", "Rating"]
            if show_explanations:
                table_columns.append("How I Use It")

            table_height = 40 * (len(filtered_frame) + 1)
            st.dataframe(
                filtered_frame[table_columns],
                column_config={
                    "Skill": st.column_config.TextColumn("Skill", width=320),
                    "Rating": st.column_config.NumberColumn(
                        "Rating", width="small", alignment="left", format="%d"
                    ),
                    "How I Use It": st.column_config.TextColumn(
                        "How I Use It", width=900
                    ),
                },
                hide_index=True,
                width="stretch",
                height=table_height,
                row_height=40,
            )
