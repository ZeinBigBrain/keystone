import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "The command line",
    "summary": "Terminals and shells, moving around, files and folders, environment variables, and WSL.",
}

LESSONS = [
    {
        "id": "terminal",
        "title": "What the terminal is",
        "kind": "read",
        "body": """
Back-end work happens in a **terminal** much more than in windows and menus. Servers usually have no screen at all, and tools like Git, Docker and pip are built to be typed.

A terminal runs a **shell**: a program that reads the command you type, runs it, and shows the result.

| System | Shell you'll usually use | How to open it |
|---|---|---|
| Windows | PowerShell | Start menu, type "PowerShell" (or Windows Terminal) |
| Mac | zsh | Applications, Utilities, Terminal |
| Linux and servers | bash | it's usually what you connect to |

## Reading a command

```
git commit -m "Add materials list"
```

- `git` is the **program**.
- `commit` is a **subcommand** (what you want git to do).
- `-m` is an **option** (also called a flag), and `"Add materials list"` is its value.

Options usually start with `-` (short, like `-m`) or `--` (long, like `--message`). Most programs explain themselves with `--help`: `git --help`, `python -m pip --help`.

## How the exercises in this track work

Some lessons in this track are about commands and config files rather than Python. In those, you **type the commands** (one per line) or the file's contents into the editor and submit. The checks read what you wrote. They'll accept the common variations, like `git switch -c` or `git checkout -b`.

Then try them for real in your own terminal. That's where it sticks.
""",
    },
    {
        "id": "moving-around",
        "title": "Moving around",
        "kind": "code",
        "lang": "text",
        "body": """
The shell always has a **current folder** (the working directory). Commands act on it unless you say otherwise.

| Command | Does | PowerShell |
|---|---|---|
| `pwd` | print the current folder | same |
| `ls` | list what's in it | same (or `dir`) |
| `cd projects` | go into the `projects` folder | same |
| `cd ..` | go up one level | same |
| `cd ~` | go to your home folder | same |

PowerShell understands `pwd`, `ls` and `cd` too, so the same commands work on Windows, Mac and Linux.

Press **Tab** while typing a folder name and the shell completes it for you. It's faster and saves typos.

## Your task

Write these commands, one per line, in order:

1. show which folder you're in
2. list what's in it
3. go into the folder `projects`
4. go back up one level
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "The four commands, in order"
    in_order([
        ("the command that shows the current folder", ["pwd", "Get-Location"]),
        ("the command that lists the folder", ["ls", "dir", "ls -l", "ls -la", "Get-ChildItem"]),
        ("going into projects", ["cd projects", "cd ./projects", "cd projects/", "cd .\\\\projects"]),
        ("going up one level", ["cd ..", "cd ../"]),
    ])
''',
        "solution": "pwd\nls\ncd projects\ncd ..\n",
        "hints": [
            "Four lines: `pwd`, `ls`, `cd projects`, `cd ..`.",
        ],
    },
    {
        "id": "paths-quiz",
        "title": "Relative and absolute paths",
        "kind": "quiz",
        "body": """
An **absolute** path starts from the very top: `/home/sara/projects` on Mac and Linux, `C:\\Users\\Sara\\projects` on Windows.

A **relative** path starts from the current folder: `projects/site-api`. Two special names:

- `.` means "this folder"
- `..` means "the folder above"
""",
        "question": "You're in `/home/sara/projects`. Where does `cd ../docs` take you?",
        "options": ["`/home/sara/projects/docs`", "`/home/sara/docs`", "`/docs`", "`/home/docs`"],
        "answer": 1,
        "explain": "`..` goes up from `projects` to `/home/sara`, then `docs` goes down into `/home/sara/docs`.",
    },
    {
        "id": "files-folders",
        "title": "Files and folders",
        "kind": "code",
        "lang": "text",
        "body": """
| Command | Does |
|---|---|
| `mkdir site-api` | make a folder |
| `touch app.py` | make an empty file (Mac/Linux) |
| `ni app.py` | make an empty file (PowerShell, short for New-Item) |
| `cp a.py b.py` | copy a file |
| `mv a.py b.py` | move or rename a file |
| `rm b.py` | delete a file |
| `cat app.py` | show a file's contents (PowerShell too) |

## Your task

Write the commands, one per line, to:

1. make a folder called `site-api`
2. go into it
3. create an empty file `app.py`
4. copy `app.py` to `app_backup.py`
5. rename `app_backup.py` to `old_app.py`
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "The five commands, in order"
    in_order([
        ("making the folder", ["mkdir site-api"]),
        ("going into it", ["cd site-api", "cd site-api/", "cd ./site-api"]),
        ("creating app.py", ["touch app.py", "ni app.py", "New-Item app.py", "New-Item -Path app.py", "echo. > app.py", "type nul > app.py"]),
        ("copying to app_backup.py", ["cp app.py app_backup.py", "copy app.py app_backup.py", "Copy-Item app.py app_backup.py"]),
        ("renaming to old_app.py", ["mv app_backup.py old_app.py", "move app_backup.py old_app.py", "ren app_backup.py old_app.py", "Rename-Item app_backup.py old_app.py", "Move-Item app_backup.py old_app.py"]),
    ])
''',
        "solution": "mkdir site-api\ncd site-api\ntouch app.py\ncp app.py app_backup.py\nmv app_backup.py old_app.py\n",
        "hints": [
            "Renaming is a move: `mv old_name new_name`.",
            "`mkdir site-api`, `cd site-api`, `touch app.py`, `cp app.py app_backup.py`, `mv app_backup.py old_app.py`.",
        ],
    },
    {
        "id": "rm-quiz",
        "title": "Careful with rm",
        "kind": "quiz",
        "body": "One warning that's worth a whole question.",
        "question": "What happens to a file deleted with `rm` in a terminal?",
        "options": [
            "It goes to the Recycle Bin or Trash",
            "It's gone straight away, with no bin to restore it from",
            "It's hidden until you restart",
            "It's moved to your home folder",
        ],
        "answer": 1,
        "explain": "Terminal deletes skip the bin. `rm -r folder` deletes a folder and everything inside it, with no confirmation. Check the current folder with `pwd` first, and keep your work in Git so a mistake can be undone.",
    },
    {
        "id": "env-vars",
        "title": "Environment variables",
        "kind": "read",
        "body": """
An **environment variable** is a named setting the shell passes to every program it starts. You've already relied on one: `PATH`, the list of folders the shell searches when you type a program's name.

Back-end apps use them for configuration that changes between your laptop and the server, and for **secrets** that must never be written into code:

```
DATABASE_URL=postgresql://app@db.internal/site
API_KEY=sk_live_...
PORT=8000
```

## Setting one

| Shell | Set it for this terminal | Read it |
|---|---|---|
| bash / zsh | `export PORT=8000` | `echo $PORT` |
| PowerShell | `$env:PORT = "8000"` | `echo $env:PORT` |

A variable set like this only lasts until you close the terminal, and only programs started from that terminal see it. That's a feature: nothing leaks between projects.

## Reading one in Python

```python
import os

port = os.environ.get("PORT", "8000")   # a default if it isn't set
```

Values always arrive as **text**, so convert numbers yourself: `int(port)`.
""",
    },
    {
        "id": "env-python",
        "title": "Settings from the environment",
        "kind": "code",
        "body": """
A pattern you'll use in every app: read each setting from the environment, with a sensible default, and convert it to the right type.

```python
import os

def get_debug():
    value = os.environ.get("DEBUG", "false")
    return value.lower() in ("1", "true", "yes")
```

> **Common slip:** `os.environ["PORT"]` (square brackets) crashes with a `KeyError` when the variable isn't set. `.get()` with a default doesn't.

## Your task

Write `get_port()` that returns the `PORT` environment variable as an **int**, or `8000` if it isn't set.
""",
        "starter": "import os\n\n\ndef get_port():\n    pass\n\n\nprint(get_port())\n",
        "tests": '''
import os

def test_default():
    "8000 when PORT isn't set"
    os.environ.pop("PORT", None)
    v, _ = capture(need("get_port"))
    check(v == 8000 and isinstance(v, int), "With PORT unset, get_port() returned %r, expected the int 8000." % (v,))

def test_set():
    "Reads PORT and converts it"
    os.environ["PORT"] = "5050"
    try:
        v, _ = capture(need("get_port"))
    finally:
        os.environ.pop("PORT", None)
    check(v == 5050 and isinstance(v, int), "With PORT=5050, get_port() returned %r. Convert it with int()." % (v,))
''',
        "solution": "import os\n\n\ndef get_port():\n    return int(os.environ.get(\"PORT\", \"8000\"))\n\n\nprint(get_port())\n",
        "hints": [
            "`os.environ.get(\"PORT\", \"8000\")` gives text either way.",
            "`return int(os.environ.get(\"PORT\", \"8000\"))`",
        ],
    },
    {
        "id": "env-commands",
        "title": "Running with a setting",
        "kind": "code",
        "lang": "text",
        "body": """
Setting a variable, then running a program from the same terminal, is how you'll start apps locally:

```
export DATABASE_URL=sqlite:///dev.db
python app.py
```

## Your task

Write the two **bash** commands (one per line) that set `PORT` to `5050` and then run `python server.py`.
""",
        "starter": "# set PORT to 5050, then run server.py\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "export, then run"
    in_order([
        ("setting PORT", ["export PORT=5050", 'export PORT="5050"']),
        ("running the server", ["python server.py", "python3 server.py"]),
    ])
''',
        "solution": "export PORT=5050\npython server.py\n",
        "hints": [
            "No spaces around the `=` in bash: `export PORT=5050`.",
        ],
    },
    {
        "id": "wsl",
        "title": "A Linux shell on Windows (WSL)",
        "kind": "read",
        "body": """
Most servers run Linux, and most back-end tutorials assume a Linux shell. On Windows, **WSL** (Windows Subsystem for Linux) gives you a real Linux system alongside Windows, without a separate computer.

## Installing it

1. Open **PowerShell as administrator** (right-click, Run as administrator).
2. Run `wsl --install`
3. Restart when asked. Ubuntu installs by default.
4. Open "Ubuntu" from the Start menu and choose a username and password. This is a separate Linux account, not your Windows one.

## Using it

- Your Windows drives appear under `/mnt/`: `C:\\Users\\Sara` is `/mnt/c/Users/Sara`.
- Linux has its own Python. Install tools inside Ubuntu with `sudo apt update` then `sudo apt install python3-pip python3-venv git`.
- VS Code's "WSL" extension lets you edit files inside Linux as if they were local.

## Do you need it?

Not for this track. Everything here works in PowerShell or the Mac terminal. WSL becomes worth it when you start following Linux-based guides, or using tools that are awkward on Windows. Docker Desktop uses it behind the scenes anyway.
""",
    },
]
