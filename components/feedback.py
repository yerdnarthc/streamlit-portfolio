"""Local feedback form for the portfolio app."""

import streamlit as st


def render_feedback() -> None:
    """Render the visitor feedback form without transmitting its contents."""
    st.header("Feedback")
    st.caption(
        "Share a note about the portfolio. Nothing is transmitted or saved outside "
        "this browser session; only a short confirmation is retained locally."
    )

    with st.form("feedback_form", border=True):
        visitor_name = st.text_input("Your name")
        st.radio(
            "What would you like to share?",
            ["Feedback", "Project question", "General message"],
        )
        st.multiselect(
            "Related sections",
            ["Autobiography", "Skills", "Portfolio"],
        )
        message = st.text_area("Your message")
        submitted = st.form_submit_button("Send feedback", type="primary")

    if submitted and (not visitor_name.strip() or not message.strip()):
        st.session_state.pop("feedback_confirmation", None)
        st.error("Please enter your name and a message.")
    elif submitted:
        st.session_state["feedback_confirmation"] = (
            f"Thanks, {visitor_name.strip()}! Your message was received "
            "in this browser session."
        )

    confirmation = st.session_state.get("feedback_confirmation")
    if confirmation:
        st.success(confirmation)
