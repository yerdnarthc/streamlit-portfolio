"""Render the student's portfolio projects with clean, production-grade craft.

Distilled editorial layout:
  - Clean project index switcher (zero capsules, zero clutter).
  - Balanced 2-column hero stage:
      Left: Typographic identity, metadata line, tool tags, sharp action buttons, and overview prose.
      Right: Properly scaled, framed preview viewport (contained, non-dominating) with zoom dialog.
  - Generously spaced deep-dive tabs (Contribution, Key Features, Outcome & Next Steps).
  - Clean typographic lists with muted rose square markers, zero extraneous accent colors.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import streamlit as st

from utils.content import load_markdown, remove_image_markdown


@dataclass(frozen=True)
class PortfolioProject:
    """One source-preserved project section and its matching local media path."""

    slug: str
    title: str
    body: str
    preview_path: Path
    preview_relative_path: Path


PROJECT_ORDER: list[str] = [
    "DeskDuck",
    "Custom Neofetch-Style Github Profile",
    "N-Queens Hill Climbing Visualizer",
    "BantAI Buddy Extension",
    "VWSim: Vacuum World Agent Simulator",
]

PROJECT_MEDIA: dict[str, Path] = {
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

INDEX_LABELS: dict[str, str] = {
    "DeskDuck": "DeskDuck",
    "Custom Neofetch-Style Github Profile": "Neofetch Profile",
    "N-Queens Hill Climbing Visualizer": "N-Queens Visualizer",
    "BantAI Buddy Extension": "BantAI Buddy",
    "VWSim: Vacuum World Agent Simulator": "VWSim Simulator",
}

PROJECT_HEADING = re.compile(r"^##\s+\d+\.\)\s+(?P<title>.+?)\s*$", re.MULTILINE)


def _slugify(title: str) -> str:
    """Return a clean URL-safe slug for widget keys and test selectors."""
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def parse_portfolio_projects(markdown: str, asset_dir: Path | None = None) -> dict[str, PortfolioProject]:
    """Return known project sections keyed by their source Markdown title."""
    headings = list(PROJECT_HEADING.finditer(markdown))
    projects: dict[str, PortfolioProject] = {}
    base_asset_dir = asset_dir or Path("assets")

    for index, heading in enumerate(headings):
        title = heading.group("title")
        if title not in PROJECT_MEDIA:
            continue

        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(markdown)
        section = markdown[heading.start() : section_end]
        section = re.split(r"(?m)^# (?!#)", section)[0]
        body = remove_image_markdown(section).strip()
        rel_path = PROJECT_MEDIA[title]

        projects[title] = PortfolioProject(
            slug=_slugify(title),
            title=title,
            body=body,
            preview_relative_path=rel_path,
            preview_path=base_asset_dir / rel_path,
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
    """Return the prepared long-form project prose after identity metadata."""
    overview = re.search(r"^### Overview\s*$", body, re.MULTILINE)
    return body[overview.start() :].strip() if overview else body


def _sections(body: str) -> dict[str, str]:
    """Return an ordered dict of project sections from markdown headings."""
    parts = re.split(r"(?m)^### (.+)\s*$", _project_details(body))
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def _extract_tool_chips(body: str) -> list[str]:
    """Extract individual tool names for chips rendering."""
    sections_dict = _sections(body)
    tools_raw = sections_dict.get("Tools Used", "")
    chips = re.findall(r"`([^`]+)`", tools_raw)
    if not chips:
        chips = [line.lstrip("- *").strip() for line in tools_raw.splitlines() if line.strip().startswith(("-", "*"))]
    return [c for c in chips if c]


@st.dialog("Project Preview", width="large")
def _enlarge_preview(project: PortfolioProject, asset_dir: Path) -> None:
    """Full-resolution dialog modal for inspecting project media."""
    st.subheader(project.title)
    meta = " · ".join(filter(None, [_metadata_value(project.body, "Role"), _metadata_value(project.body, "Status")]))
    if meta:
        st.caption(meta)
    img_path = asset_dir / project.preview_relative_path
    if img_path.is_file():
        st.image(str(img_path), width="stretch", alt=f"{project.title} full preview")
    else:
        st.warning(f"Preview unavailable for {project.title}.")


def _select_project(title: str) -> None:
    """Update active project in session state."""
    st.session_state.portfolio_selected = title


def _render_project_index(projects: dict[str, PortfolioProject]) -> None:
    """Clean, restrained horizontal project index selector."""
    ordered = [projects[t] for t in PROJECT_ORDER if t in projects]
    if not ordered:
        return

    with st.container(key="pf_index_bar"):
        cols = st.columns(len(ordered), gap="small")
        for col, p in zip(cols, ordered):
            with col:
                is_active = st.session_state.portfolio_selected == p.title
                label = INDEX_LABELS.get(p.title, p.title)
                st.button(
                    label,
                    key=f"explore_{p.slug}",
                    type="primary" if is_active else "secondary",
                    width="stretch",
                    on_click=_select_project,
                    args=(p.title,),
                )


def _render_project_stage(project: PortfolioProject, asset_dir: Path) -> None:
    """Balanced two-column hero stage: Identity & Overview on left, scaled preview on right."""
    status = _metadata_value(project.body, "Status") or "Active"
    role = _metadata_value(project.body, "Role") or "Solo Developer"
    repo_url = _metadata_link(project.body, "Repository")
    demo_url = _metadata_link(project.body, "Live demo")
    chips = _extract_tool_chips(project.body)
    img_path = asset_dir / project.preview_relative_path
    sections_dict = _sections(project.body)
    overview_text = sections_dict.get("Overview", "")

    info_col, preview_col = st.columns([1.1, 0.9], gap="large")

    with info_col:
        st.subheader(project.title)
        st.caption(f"{role}  ·  {status}")

        if chips:
            chips_html = "".join(f'<span class="pf-chip">{c}</span>' for c in chips)
            st.markdown(f'<div class="pf-chips-wrapper">{chips_html}</div>', unsafe_allow_html=True)

        with st.container(horizontal=True):
            if repo_url:
                st.link_button("Repository", repo_url, icon=":material/open_in_new:")
            if demo_url:
                st.link_button("Live Demo", demo_url, icon=":material/open_in_new:")

        if overview_text:
            st.markdown("#### Overview")
            st.markdown(overview_text)

    with preview_col:
        with st.container(key="pf_preview_frame"):
            if img_path.is_file():
                st.image(str(img_path), width="stretch", alt=f"{project.title} preview")
            else:
                st.caption(f"Preview unavailable for {project.title}.")

        if img_path.is_file():
            st.button(
                "Enlarge Preview",
                icon=":material/zoom_in:",
                key="pf_enlarge_btn",
                on_click=_enlarge_preview,
                args=(project, asset_dir),
            )


def _render_project_tabs(project: PortfolioProject) -> None:
    """Spacious, readable tabs for deep-dive sections."""
    sections_dict = _sections(project.body)
    tab_map = {
        "My Contribution": "Contribution",
        "Key Features": "Key Features",
        "Outcome and Next Steps": "Outcome & Next Steps",
    }
    available_labels = [k for k in ("My Contribution", "Key Features", "Outcome and Next Steps") if k in sections_dict]
    if not available_labels:
        available_labels = [k for k in sections_dict if k != "Overview" and k != "Tools Used"]

    if available_labels:
        st.divider()
        tab_names = [tab_map.get(k, k) for k in available_labels]
        tabs = st.tabs(tab_names)
        for tab, raw_key in zip(tabs, available_labels):
            with tab:
                st.markdown(sections_dict[raw_key])


@st.fragment
def _portfolio_theater(projects: dict[str, PortfolioProject], asset_dir: Path) -> None:
    """Self-contained interactive theater fragment for instant project switching."""
    if st.session_state.get("portfolio_selected") not in projects:
        st.session_state.portfolio_selected = next(iter(projects))

    active_project = projects[st.session_state.portfolio_selected]

    with st.container(key="pf_portfolio_root"):
        _render_project_index(projects)
        st.divider()
        _render_project_stage(active_project, asset_dir)
        _render_project_tabs(active_project)


def render_portfolio(content_dir: Path, asset_dir: Path) -> None:
    """Present the student's work as a clean, production-grade portfolio."""
    st.header("Portfolio")

    source = load_markdown(content_dir / "my-portfolio.md")
    if source is None:
        st.warning("Portfolio content could not be loaded.")
        return

    projects = parse_portfolio_projects(source, asset_dir)
    if not projects:
        st.warning("No project sections could be read from the portfolio content.")
        return

    for title in PROJECT_MEDIA:
        if title not in projects:
            st.warning(f"Project content for {title} could not be loaded.")

    _portfolio_theater(projects, asset_dir)
