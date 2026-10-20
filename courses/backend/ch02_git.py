import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Git and GitHub",
    "summary": "Commits and history, branches and merging, conflicts, remotes and pull requests, undoing mistakes, and .gitignore.",
}

CONFLICT = """# Site API

Small API for the site materials register.

<<<<<<< HEAD
Run it with: python app.py --port 8000
=======
Run it with: uvicorn main:app --reload
>>>>>>> switch-to-fastapi

Contact: site office
"""

LESSONS = [
    {
        "id": "git-what",
        "title": "What Git does",
        "kind": "read",
        "body": """
**Git** records the history of a folder of files. Every time you reach a sensible point, you take a snapshot called a **commit**. You can look back at any commit, see exactly what changed, and undo mistakes. Every serious software project uses it.

## Three places a change can be

1. **Working folder:** the files as they are on disk right now.
2. **Staging area:** the changes you've picked for the next commit (`git add`).
3. **History:** commits, saved permanently (`git commit`).

The staging step lets you commit some changes and not others, so each commit is one tidy, logical step.

## A repository

A folder Git is tracking is a **repository** (repo). The history lives in a hidden `.git` folder inside it. Delete that and the history is gone, but your files stay.

## One-time setup

Git stamps every commit with your name and email. Tell it once per computer:

```
git config --global user.name "Sara Ahmed"
git config --global user.email "sara@example.com"
```

Install Git from git-scm.com (Windows) or with `xcode-select --install` (Mac).
""",
    },
    {
        "id": "first-commit",
        "title": "Your first commit",
        "kind": "code",
        "lang": "text",
        "body": """
```
git init                          (start tracking this folder, once)
git add app.py                    (stage one file)
git add .                         (or stage everything that changed)
git commit -m "Add first version" (save the snapshot with a message)
```

Commit messages describe **what the commit does**, in a few words: "Add materials endpoint", "Fix rounding in totals". Future you will search them.

## Your task

In a new project folder, write the commands to: start a repository, stage `README.md`, and commit it with the message `Add readme`.
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "init, add, commit"
    in_order([
        ("git init", ["git init"]),
        ("staging README.md", ["git add README.md", "git add .", "git add -A"]),
        ("the commit with its message", ['git commit -m "Add readme"']),
    ])
''',
        "solution": "git init\ngit add README.md\ngit commit -m \"Add readme\"\n",
        "hints": [
            "`git init`, `git add README.md`, `git commit -m \"Add readme\"`.",
        ],
    },
    {
        "id": "staging-quiz",
        "title": "Forgetting to stage",
        "kind": "quiz",
        "body": "A slip everyone makes in their first week.",
        "question": "You edit `app.py`, then run `git commit -m \"Fix totals\"` without running `git add`. What happens?",
        "options": [
            "The edit is committed anyway",
            "Git commits nothing and says there are no changes added to commit",
            "Git deletes your edit",
            "Git stages and commits every file in the folder",
        ],
        "answer": 1,
        "explain": "Only staged changes go into a commit. Git tells you \"no changes added to commit\". Run `git add app.py` first. (`git commit -am \"...\"` stages and commits every already-tracked file in one go.)",
    },
    {
        "id": "status-log",
        "title": "Seeing what's going on",
        "kind": "code",
        "lang": "text",
        "body": """
Three commands you'll run constantly:

| Command | Shows |
|---|---|
| `git status` | which files changed, and which are staged |
| `git diff` | the exact lines changed but not yet staged |
| `git diff --staged` | the lines staged for the next commit |
| `git log --oneline` | the history, one commit per line |

When in doubt, `git status`. It usually tells you what to do next, too.

## Your task

Write the commands to: see which files have changed, see the exact unstaged line changes, then see the history one commit per line.
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "status, diff, log"
    in_order([
        ("git status", ["git status"]),
        ("git diff", ["git diff"]),
        ("the one-line history", ["git log --oneline"]),
    ])
''',
        "solution": "git status\ngit diff\ngit log --oneline\n",
        "hints": [
            "`git status`, `git diff`, `git log --oneline`.",
        ],
    },
    {
        "id": "branches",
        "title": "Branches and merging",
        "kind": "code",
        "lang": "text",
        "body": """
A **branch** is a separate line of work. You make one for each feature or fix, commit on it freely, and **merge** it back into `main` when it's ready. Meanwhile `main` stays working.

```
git switch -c add-materials     (create a branch and switch to it)
... edit, git add, git commit ...
git switch main                 (back to main)
git merge add-materials         (bring the branch's commits into main)
git branch -d add-materials     (tidy up the finished branch)
```

Older guides use `git checkout -b name` instead of `git switch -c name`. They do the same thing.

## Your task

Write the commands to: create and switch to a branch called `fix-totals`, stage everything, commit with the message `Fix totals rounding`, switch back to `main`, and merge the branch.
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "branch, commit, switch, merge"
    in_order([
        ("creating and switching to fix-totals", ["git switch -c fix-totals", "git checkout -b fix-totals"]),
        ("staging", ["git add .", "git add -A"]),
        ("the commit", ['git commit -m "Fix totals rounding"']),
        ("switching back to main", ["git switch main", "git checkout main"]),
        ("merging fix-totals", ["git merge fix-totals"]),
    ])
''',
        "solution": "git switch -c fix-totals\ngit add .\ngit commit -m \"Fix totals rounding\"\ngit switch main\ngit merge fix-totals\n",
        "hints": [
            "Five lines. The merge runs while you're on `main`, naming the branch to bring in.",
        ],
    },
    {
        "id": "conflict",
        "title": "Resolving a conflict",
        "kind": "code",
        "lang": "text",
        "body": """
If two branches change the **same lines** differently, Git can't guess which to keep. The merge stops and marks the clash in the file:

```
<<<<<<< HEAD
the line as it is on your current branch
=======
the line as it is on the branch you're merging in
>>>>>>> other-branch
```

To resolve it:

1. Edit the file to what it **should** say. That might be one side, the other, or a mix.
2. Delete all three marker lines (`<<<<<<<`, `=======`, `>>>>>>>`).
3. `git add` the file, then `git commit` to finish the merge.

## Your task

The editor holds `README.md` mid-merge. The team agreed to switch to FastAPI, so keep the **uvicorn** line, drop the old one, and remove the markers. Everything else stays as it is.
""",
        "starter": CONFLICT,
        "tests": '''
def test_markers():
    "No conflict markers left"
    for m in ("<<<<<<<", "=======", ">>>>>>>"):
        check(m not in RAW_CODE, "There's still a %s line. Delete all three marker lines." % m)

def test_content():
    "Kept the uvicorn line and everything else"
    text = RAW_CODE
    check("Run it with: uvicorn main:app --reload" in text, "Keep the uvicorn line.")
    check("python app.py --port 8000" not in text, "Remove the old python app.py line.")
    for keep in ("# Site API", "Small API for the site materials register.", "Contact: site office"):
        check(keep in text, "Keep the line %r." % keep)
''',
        "solution": "# Site API\n\nSmall API for the site materials register.\n\nRun it with: uvicorn main:app --reload\n\nContact: site office\n",
        "hints": [
            "Delete four lines: the `<<<<<<<` line, the old run line, the `=======` line and the `>>>>>>>` line.",
        ],
    },
    {
        "id": "remotes-quiz",
        "title": "Remotes",
        "kind": "quiz",
        "body": """
So far everything has been on your own computer. A **remote** is a copy of the repo somewhere else, usually on **GitHub** (or GitLab, or Azure DevOps). It's your backup and how a team shares work.

- `git push` sends your new commits up to the remote.
- `git pull` brings other people's new commits down to you.
- `origin` is the usual name for "the main remote".
- `git clone URL` copies an existing remote repo to your computer, history and all.
""",
        "question": "You've made three commits locally. Your colleague can't see them on GitHub. What's missing?",
        "options": ["`git pull`", "`git push`", "`git merge`", "`git init`"],
        "answer": 1,
        "explain": "Commits stay on your machine until you push them. `git push` sends them to the remote, and then your colleague can `git pull` them.",
    },
    {
        "id": "push",
        "title": "Connecting to GitHub",
        "kind": "code",
        "lang": "text",
        "body": """
After creating an empty repository on GitHub, it shows you its URL. Connect your local repo to it and push:

```
git remote add origin https://github.com/sara/site-api.git
git push -u origin main
```

The `-u` links your `main` to the remote's `main`, so after that a plain `git push` or `git pull` knows where to go.

## Your task

Write the commands to: add the remote `origin` at `https://github.com/sara/site-api.git`, push `main` to it with `-u`, and then (some days later) pull your colleagues' changes.
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "remote add, push -u, pull"
    in_order([
        ("adding the remote", ["git remote add origin https://github.com/sara/site-api.git"]),
        ("the first push", ["git push -u origin main", "git push --set-upstream origin main"]),
        ("pulling", ["git pull", "git pull origin main"]),
    ])
''',
        "solution": "git remote add origin https://github.com/sara/site-api.git\ngit push -u origin main\ngit pull\n",
        "hints": [
            "`git remote add origin <url>`, then `git push -u origin main`, then `git pull`.",
        ],
    },
    {
        "id": "pull-requests",
        "title": "Pull requests",
        "kind": "read",
        "body": """
On a team, you don't merge your own branch into `main` straight away. You push the branch and open a **pull request** (PR; GitLab calls it a merge request): a page on GitHub that says "here's my branch, please review it and merge it into main".

## The everyday loop

```
git switch -c add-deliveries-endpoint
... work, commit, work, commit ...
git push -u origin add-deliveries-endpoint
```

Then on GitHub:

1. Open a pull request from your branch into `main`. Describe what it does and how you checked it.
2. A teammate reviews the changes line by line and leaves comments.
3. Automatic checks (tests, linting) run on it.
4. You push more commits to the same branch to address comments. The PR updates by itself.
5. Once approved and green, it's merged, and the branch is deleted.

## Why bother?

A second pair of eyes catches bugs, and the PR becomes a record of *why* each change was made. It's also how open-source projects accept contributions from strangers.

Keep PRs small: one feature or fix each. A 50-line PR gets a careful review; a 2,000-line one gets "looks fine".
""",
    },
    {
        "id": "undo-quiz",
        "title": "Undoing safely",
        "kind": "quiz",
        "body": """
Different mistakes, different fixes:

| Situation | Command |
|---|---|
| Throw away unsaved edits to a file | `git restore app.py` |
| Unstage a file (keep the edits) | `git restore --staged app.py` |
| Fix the last commit's message (not pushed yet) | `git commit --amend -m "Better message"` |
| Undo a commit that's **already pushed** | `git revert <commit>` |

`git revert` makes a **new** commit that undoes the old one. History stays intact, so it's safe even when others have pulled. `git reset --hard` rewrites history instead, which is fine on your own unpushed work but causes chaos on a shared branch.
""",
        "question": "A commit you pushed yesterday broke the totals, and your colleagues have already pulled it. What's the safe way to undo it?",
        "options": [
            "`git reset --hard HEAD~1` then force-push",
            "`git revert` that commit, then push",
            "Delete the `.git` folder",
            "`git restore .`",
        ],
        "answer": 1,
        "explain": "`git revert` adds a new commit that reverses the bad one, so everyone's history still lines up. Resetting and force-pushing rewrites shared history, and colleagues' next pull turns into a mess.",
    },
    {
        "id": "undo",
        "title": "Undo commands",
        "kind": "code",
        "lang": "text",
        "body": """
The table from the last lesson, put to use.

## Your task

Write one command for each, in this order:

1. you've edited `config.py` and want to throw those edits away
2. you staged `secrets.txt` by mistake and want to unstage it (keeping the file)
3. the latest commit is pushed and needs undoing (refer to it as `HEAD`)
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "restore, restore --staged, revert"
    in_order([
        ("discarding the edits to config.py", ["git restore config.py", "git checkout -- config.py"]),
        ("unstaging secrets.txt", ["git restore --staged secrets.txt", "git reset secrets.txt", "git reset HEAD secrets.txt"]),
        ("reverting the last commit", ["git revert HEAD"]),
    ])
''',
        "solution": "git restore config.py\ngit restore --staged secrets.txt\ngit revert HEAD\n",
        "hints": [
            "`git restore config.py`, `git restore --staged secrets.txt`, `git revert HEAD`.",
        ],
    },
    {
        "id": "gitignore",
        "title": ".gitignore",
        "kind": "code",
        "lang": "text",
        "body": """
Some files must **never** go into Git: secrets, big generated files, and things that only make sense on your machine. List them in a file called `.gitignore` in the repo's top folder, one pattern per line:

```
# virtual environment
.venv/

# Python's cache
__pycache__/

# local database and logs
*.db
*.log

# secrets
.env
```

- A name ending in `/` matches a folder.
- `*` matches anything: `*.log` is every file ending in `.log`.
- Lines starting with `#` are comments.

> If a secret has already been committed, adding it to `.gitignore` doesn't remove it from history. Change the secret (new password, new key) straight away.

## Your task

Write a `.gitignore` that ignores: the `.venv` folder, `__pycache__` folders, every `.db` file, and the `.env` file.
""",
        "starter": "# .gitignore\n",
        "tests": '''
def lines():
    return [l.strip() for l in RAW_CODE.splitlines() if l.strip() and not l.strip().startswith("#")]

def test_patterns():
    "All four patterns"
    got = lines()
    def has(*opts):
        return any(o in got for o in opts)
    check(has(".venv/", ".venv", "/.venv/", "/.venv"), "Ignore the .venv folder: .venv/")
    check(has("__pycache__/", "__pycache__", "**/__pycache__/"), "Ignore Python's cache folders: __pycache__/")
    check(has("*.db"), "Ignore every database file: *.db")
    check(has(".env", "/.env"), "Ignore the secrets file: .env")
''',
        "solution": "# .gitignore\n.venv/\n__pycache__/\n*.db\n.env\n",
        "hints": [
            "Four lines: `.venv/`, `__pycache__/`, `*.db`, `.env`.",
        ],
    },
]
