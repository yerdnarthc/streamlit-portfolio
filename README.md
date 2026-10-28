# Streamlit Autobiography and Portfolio

A personal Streamlit website presenting an autobiography, skills, and selected software projects. It also includes a local-only feedback form for demonstrating interactive form handling without transmitting or storing visitor responses.

## Run locally

Create and activate a virtual environment before installing the project dependencies. From the project root, run:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print the local address in the terminal, usually `http://localhost:8501`.

## Content and media

The app reads personal written content from `contents/` and images and other media from `assets/`. Keep those directories alongside `app.py` when running or submitting the project.
