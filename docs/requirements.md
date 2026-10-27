# Project Requirement

***Transcribed from CSIT349 - Applied AI instructions on October 27, 2026***

## Project: Autobiography and Portfolio App built on Streamlit

Build a Streamlit app that shows your autobiography and a small portfolio. Use as many Streamlit components as you can, with each one supporting the site. Submit your code, or deploy on Streamlit Community Cloud and submit the link for bonus points. Grading looks at how fully you use Streamlit, the design of the page, and the content.

### Install and run

```Python
pip install streamlit pandas numpy
streamlit run app.py
```

Create app.py and start from this. Replace it with your own site.

```Python
import streamlit as st

st.set_page_config(
	page_title="Your Name | Portfolio",
	page_icon="👋",
	layout="wide",
)

st.title("Your Name")
st.write("Replace this with your autobiography and portfolio.")
```

### What the app should show

- About you: name, program and year, a short biography, and a photo or a clearly labeled stand-in.
- Autobiography: background, education, interests, and a few milestones, in your own words.
- Skills, in text and in a table or chart that uses your own numbers.
- At least three projects. For each one: title, your role, tools used, and the outcome or a link.
- A contact or feedback form that responds after it is submitted.
- Your name and section somewhere visible on the page.

### Components

Use the pieces from the lecture, then add a few more. Suggested set:

- Text (title, header, write or markdown), a table, and a chart.
- Button, slider, selectbox, checkbox, text input, text area, and radio or multiselect.
- A sidebar and columns.
- At least four extras, such as an image, tabs, metrics, a form, session state, a download button, or a theme.

Use them for your own story and projects, in place of the sample demos from the slides.

### Design

Give the page a clear title, group the sections, and place related items side by side so the app reads as a short personal site.

### Submit

***Option A.*** Zip app.py, requirements.txt, and any images. Leave out .venv and any secrets or API keys. Put your name and section in the submission comment.

***Option B (bonus).*** Submit a public Community Cloud link instead of the code. Push the app to a public GitHub repo with a requirements.txt, sign in at https://share.streamlit.io, and deploy app.py. The link should open when your computer is off.

Work individually. The writing and the projects must be your own.

### Rubrics (100 points, +10 bonus)

| **Criterion** | **Points** | **Full Credit**                                                       |
| ------------------- | ---------------- | --------------------------------------------------------------------------- |
| Content             | 40               | Autobiography plus at least three projects, specific and written by you.    |
| Components          | 35               | The lecture set above is used on purpose, plus at least four extras.        |
| Design              | 25               | Clear title, grouped sections, an image, and a layout that is easy to scan. |
| Bonus               | +10              | A public .streamlit.app link loads the same app.                            |
