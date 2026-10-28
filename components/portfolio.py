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
        body = remove_image_markdown(markdown[heading.start() : section_end]).strip()
        projects[title] = PortfolioProject(
            title=title,
            body=body,
            preview_relative_path=PROJECT_MEDIA[title],
        )

    return projects


def _metadata_value(body: str, label: str) -> str | None:
    pattern = re.compile(rf"^\*\*{re.escape(label)}\*\*:\s*(.+)$", re.MULTILINE)
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


def _render_dossier(project: PortfolioProject, asset_dir: Path) -> None:
    """Render one selected project without altering its prepared writing."""
    key = _project_key(project.title)
    status = _metadata_value(project.body, "Status")
    role = _metadata_value(project.body, "Role")
    repository = _metadata_link(project.body, "Repository")
    live_demo = _metadata_link(project.body, "Live demo")
    preview_path = asset_dir / project.preview_relative_path

    with st.container(border=True, key=f"portfolio_dossier_{key}"):
        details_column, media_column = st.columns([1, 1.6], gap="large")
        with details_column:
            st.subheader(project.title)
            identity = "  |  ".join(
                item
                for item in (
                    f"Status: {status}" if status else None,
                    f"Role: {role}" if role else None,
                )
                if item
            )
            if identity:
                st.caption(identity)

            if repository or live_demo:
                actions = st.columns(2 if repository and live_demo else 1)
                if repository:
                    with actions[0]:
                        st.link_button(
                            "Repository",
                            repository,
                            icon=":material/open_in_new:",
                            key=f"portfolio_repository_{key}",
                        )
                if live_demo:
                    with actions[-1]:
                        st.link_button(
                            "Live demo",
                            live_demo,
                            icon=":material/play_circle:",
                            key=f"portfolio_demo_{key}",
                        )

        with media_column:
            if preview_path.is_file():
                with st.container(border=True, key=f"portfolio_media_frame_{key}"):
                    st.image(
                        str(preview_path),
                        caption=f"{project.title} preview",
                        width="stretch",
                    )
            else:
                st.warning(f"Preview image for {project.title} could not be loaded.")

        st.divider()
        st.markdown(_project_details(project.body))


def _render_project_group(
    projects: dict[str, PortfolioProject],
    titles: tuple[str, ...],
    group_key: str,
    asset_dir: Path,
) -> None:
    available_projects = [projects[title] for title in titles if title in projects]
    for title in titles:
        if title not in projects:
            st.warning(f"Project content for {title} could not be loaded.")

    if not available_projects:
        return

    selected_title = st.radio(
        f"Choose a {group_key} project",
        [project.title for project in available_projects],
        horizontal=True,
        label_visibility="collapsed",
        key=f"portfolio_{group_key}_index",
    )
    _render_dossier(projects[selected_title], asset_dir=asset_dir)


def render_portfolio(content_dir: Path, asset_dir: Path) -> None:
    """Render the supplied portfolio as two interactive project dossiers."""
    st.header("Portfolio")
    source = load_markdown(content_dir / "my-portfolio.md")
    if source is None:
        st.warning("Portfolio content could not be loaded.")
        return

    projects = parse_portfolio_projects(source)
    if not projects:
        st.warning("No project sections could be read from the portfolio content.")
        return

    featured_tab, more_tab = st.tabs(["Featured Projects", "More Projects"])
    with featured_tab:
        _render_project_group(projects, FEATURED_TITLES, "featured", asset_dir)
    with more_tab:
        _render_project_group(projects, MORE_PROJECT_TITLES, "more", asset_dir)
