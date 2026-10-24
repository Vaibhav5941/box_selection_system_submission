# Submission Guide

Nothing here has been uploaded anywhere. You must perform the GitHub push yourself.

## 1. Push to GitHub

Create an **empty** repository on GitHub first (no README/.gitignore/licence), then replace `<your-username>` and `<repo-name>`:

```bash
cd box_selection_system
git init
git add .
git status                      # check: no .venv/, db.sqlite3 or .env files are listed
git commit -m "Add AI-assisted box selection Django project"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

If Git asks for credentials, use a GitHub personal access token or SSH (`git@github.com:<your-username>/<repo-name>.git`) instead of your password.

## 2. Build the submission ZIP

From the **parent** folder of `box_selection_system/` (excludes virtualenv, caches, database, secrets, previous ZIPs):

```bash
zip -r box_selection_system_submission.zip box_selection_system \
  -x "box_selection_system/.venv/*" "box_selection_system/venv/*" \
     "*/__pycache__/*" "*.pyc" "box_selection_system/db.sqlite3" \
     "box_selection_system/.env" "box_selection_system/.env.*" \
     "box_selection_system/staticfiles/*" "box_selection_system/.git/*" "*.zip" ".DS_Store"
unzip -l box_selection_system_submission.zip   # inspect the contents
```

Alternative if the project is already committed to Git:

```bash
git archive --format=zip --prefix=box_selection_system/ -o ../box_selection_system_submission.zip HEAD
```

Before zipping, fill in `AI_USAGE.md` (no TODOs left) and re-run `python manage.py test`, pasting the output into `TEST_OUTPUT.md` if you changed anything.

## 3. AI chat transcript

Do not retype, summarise or edit the transcript, because evaluators want the genuine record.

- **Chat apps (e.g. claude.ai):** check whether the app offers a share, export or account-data-download option (menu names vary by app and plan, so look in the conversation menu and in settings). If not, select the entire conversation, copy it and paste it unchanged into a plain-text file such as `chat_transcript.txt`.
- **Terminal/IDE tools:** use that tool's own export or session-log feature, or copy the scrollback verbatim.
- Save the file as it came out, add it to the ZIP/repo, and reference it from `AI_USAGE.md`.
- If the platform offers no export, say so honestly in `AI_USAGE.md` rather than reconstructing the conversation from memory.

## 4. Learning reflection

Write it yourself using `LEARNING_REFLECTION_CHECKLIST.md` as prompts.
