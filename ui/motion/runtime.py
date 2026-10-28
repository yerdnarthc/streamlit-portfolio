"""Load the trusted local motion styles and mount one browser runtime."""

from pathlib import Path

import streamlit as st


MOTION_DIR = Path(__file__).parent
MOTION_STYLESHEET = MOTION_DIR / "motion.css"
MOTION_SCRIPT = MOTION_DIR / "motion.js"
_NOOP_SCRIPT = """
export default function () {
  return () => {};
}
"""

try:
    _motion_script = MOTION_SCRIPT.read_text(encoding="utf-8")
    _motion_script_available = True
except OSError:
    _motion_script = _NOOP_SCRIPT
    _motion_script_available = False


_MOTION_RUNTIME = st.components.v2.component(
    "portfolio_motion_runtime",
    html='<span class="portfolio-motion-runtime" aria-hidden="true"></span>',
    css="""
:host {
  display: none;
}

.portfolio-motion-runtime {
  display: none;
}
""",
    js=_motion_script,
)


def apply_motion_styles() -> None:
    """Inject the local motion stylesheet without taking up layout space."""
    if not MOTION_STYLESHEET.is_file():
        st.warning("The portfolio motion stylesheet could not be loaded.")
        return

    st.html(MOTION_STYLESHEET)


def mount_motion_runtime() -> None:
    """Mount the single lifecycle-managed motion component."""
    if not _motion_script_available:
        st.warning("The portfolio motion runtime could not be loaded.")
        return

    _MOTION_RUNTIME(key="portfolio_motion_runtime")
