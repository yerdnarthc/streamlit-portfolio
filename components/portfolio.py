"""Render the student's supplied projects as interactive portfolio dossiers."""

from dataclasses import dataclass
from pathlib import Path
import re

import streamlit as st

from utils.content import load_markdown, remove_image_markdown


@dataclass(frozen=True)
class PortfolioProject:
    """One source-preserved project section and its matching local media path."""

    title: str
    body: str
    preview_relative_path: Path


PROJECT_MEDIA = {
    "DeskDuck": Path("projects/deskduck/preview.png"),
    "Custom Neofetch-Style Github Profile": Path(
        "projects/custom-neofetch-style-github-profile/preview.png"
    ),
    "N-Queens Hill Climbing Visualizer": Path(
        "projects/n-queens-hill-climbing-visualizer/preview.png"
    ),
    "BantAI Buddy Extension": Path("projects/bantai-buddy-extension/preview.png"),
    "VWSim: Vacuum World Agent Simulator": Path("projects/vwsim/preview.png"),
}

FEATURED_TITLES = (
    "DeskDuck",
    "Custom Neofetch-Style Github Profile",
    "N-Queens Hill Climbing Visualizer",
)
MORE_PROJECT_TITLES = (
    "BantAI Buddy Extension",
    "VWSim: Vacuum World Agent Simulator",
)
PROJECT_HEADING = re.compile(r"^##\s+\d+\.\)\s+(?P<title>.+?)\s*$", re.MULTILINE)


def parse_portfolio_projects(markdown: str) -> dict[str, PortfolioProject]:
    """Return known project sections keyed by their source Markdown title."""
    headings = list(PROJECT_HEADING.finditer(markdown))
    projects: dict[str, PortfolioProject] = {}

    for index, heading in enumerate(headings):
        title = heading.group("title")
        if title not in PROJECT_MEDIA:
            continue

        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(markdown)
        section = markdown[heading.start() : section_end]
        section = re.split(r"(?m)^# (?!#)", section)[0]
        body = remove_image_markdown(section).strip()
        projects[title] = PortfolioProject(
            title=title,
            body=body,
            preview_relative_path=PROJECT_MEDIA[title],
        )

    return projects


def _metadata_value(body: str, label: str) -> str | None:
    pattern = re.compile(rf"^\*\*{re.escape(label)}(?:\*\*:\s*|:\*\*\s*|:\s*)(.+)$", re.MULTILINE)
    match = pattern.search(body)
    return match.group(1).strip() if match else None


def _metadata_link(body: str, label: str) -> str | None:
    value = _metadata_value(body, label)
    if value is None:
        return None

    match = re.search(r"\[[^\]]+\]\((https?://[^)]+)\)", value)
    return match.group(1) if match else None


def _project_details(body: str) -> str:
    """Return the prepared long-form project prose after the identity metadata."""
    overview = re.search(r"^### Overview\s*$", body, re.MULTILINE)
    return body[overview.start() :].strip() if overview else body


def _project_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")



def _sections(body: str) -> dict[str, str]:
    parts = re.split(r"(?m)^### (.+)\s*$", _project_details(body))
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def _select_project(title: str) -> None:
    st.session_state.portfolio_selected = title


def _preview(project: PortfolioProject, asset_dir: Path) -> None:
    path = asset_dir / project.preview_relative_path
    if path.is_file():
        st.image(str(path), width="stretch", alt=f"{project.title} application preview")
    else:
        st.caption(f"Preview unavailable for {project.title}.")


@st.dialog("Project preview", width="large")
def _enlarge_preview(project: PortfolioProject, asset_dir: Path) -> None:
    st.subheader(project.title)
    _preview(project, asset_dir)


def _gallery(projects: list[PortfolioProject], asset_dir: Path, compact: bool = False) -> None:
    if not projects:
        return
    for column, project in zip(st.columns(len(projects), gap="medium"), projects):
        with column:
            key = _project_key(project.title)
            active = st.session_state.portfolio_selected == project.title
            with st.container(key=f"work_card_{key}", border=False):
                if not compact:
                    with st.container(key=f"work_thumbnail_{key}"):
                        _preview(project, asset_dir)
                st.markdown(f"#### {project.title}")
                st.caption(_metadata_value(project.body, "Role") or "Role unavailable")
                st.caption(_metadata_value(project.body, "Status") or "Status unavailable")
                st.button(
                    "Viewing project" if active else "Explore project",
                    icon=":material/arrow_forward:",
                    key=f"explore_{key}",
                    type="primary" if active else "secondary",
                    on_click=_select_project,
                    args=(project.title,),
                    width="stretch",
                )


@st.fragment
def _portfolio_gallery(projects: dict[str, PortfolioProject], asset_dir: Path) -> None:
    if st.session_state.get("portfolio_selected") not in projects:
        st.session_state.portfolio_selected = next(iter(projects))
    with st.container(key="work_gallery"):
        _gallery([projects[t] for t in FEATURED_TITLES if t in projects], asset_dir)
        st.divider()
        project = projects[st.session_state.portfolio_selected]
        with st.container(key="work_detail"):
            st.subheader(project.title)
            st.caption(" · ".join(filter(None, [
                _metadata_value(project.body, "Role"),
                _metadata_value(project.body, "Status"),
            ])))
            with st.container(horizontal=True):
                for label in ("Repository", "Live demo"):
                    url = _metadata_link(project.body, label)
                    if url:
                        st.link_button(label, url, icon=":material/open_in_new:")
            sections = _sections(project.body)
            overview_column, preview_column = st.columns([2, 1], gap="large")
            with overview_column:
                st.markdown(sections.get("Overview", ""))
            with preview_column:
                with st.container(key="work_detail_preview"):
                    _preview(project, asset_dir)
                if (asset_dir / project.preview_relative_path).is_file():
                    st.button(
                        "Enlarge preview", icon=":material/zoom_in:",
                        on_click=_enlarge_preview, args=(project, asset_dir),
                        key="work_enlarge",
                    )
            labels = [label for label in sections if label != "Overview"]
            if labels:
                for tab, label in zip(st.tabs(labels), labels):
                    with tab:
                        st.markdown(sections[label])
        st.divider()
        st.subheader("More projects")
        _gallery([projects[t] for t in MORE_PROJECT_TITLES if t in projects], asset_dir, compact=True)


def render_portfolio(content_dir: Path, asset_dir: Path) -> None:
    """Present a compact gallery and an inline, selectable case study."""
    st.header("Portfolio")
    source = load_markdown(content_dir / "my-portfolio.md")
    if source is None:
        st.warning("Portfolio content could not be loaded.")
        return
    projects = parse_portfolio_projects(source)
    if not projects:
        st.warning("No project sections could be read from the portfolio content.")
        return
    for title in PROJECT_MEDIA:
        if title not in projects:
            st.warning(f"Project content for {title} could not be loaded.")
    _portfolio_gallery(projects, asset_dir)
