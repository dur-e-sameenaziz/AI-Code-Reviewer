# Smart Code Reviewer

This is a simple Django app for Challenge 1: Smart Code Reviewer.

A user can paste a short code snippet, pick a language, and get a quick review focused on readability, structure, and maintainability before a human reviewer sees it.

## Features

- Code review form
- OpenAI API call
- Scores for readability, structure, and maintainability
- Severity-tagged risks
- Markdown text box for copying the result

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your `OPENAI_API_KEY` in `.env`.

Run the app:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Verification

```bash
python manage.py check
python manage.py test
```

## Screenshots

![Smart Code Reviewer screenshot](screenshots/AI-Code-Reviewer.png)

## 100-Word Summary

I built Smart Code Reviewer, a small Django app that gives developers structured AI feedback before human review. Users paste a short code snippet, choose a language, and receive scores for readability, structure, and maintainability, plus severity-tagged risks, practical improvements, a positive note, and an overall verdict. I kept the scope intentionally simple: one form, one review result, and no saved history or GitHub integration. The goal is not to replace human reviewers, but to catch routine quality issues early so teams can spend review time on architecture, product context, edge cases, and maintainable implementation decisions.

## Notes

- If `OPENAI_API_KEY` is missing, the app shows a friendly error.
- Public dataset: not applicable. The app reviews user-provided or dummy code snippets.
