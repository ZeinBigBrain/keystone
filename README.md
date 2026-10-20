# Keystone

A free coding course that runs on your own computer: Python, SQL, Python for engineering, and back-end development. You work in your browser, with lessons, an editor, auto-graded exercises, XP and streaks. Nothing goes online and there's no account to make.

## Download

### [Click here to download Keystone](https://github.com/ZeinBigBrain/keystone/archive/refs/heads/main.zip)

That's it. You don't need a GitHub account, and you don't need to install Python first.

## Install on Windows

1. Open your **Downloads** folder, right-click **keystone-main.zip** and choose **Extract All**, then **Extract**.
2. Open the new **keystone-main** folder and double-click **start.bat**.
3. If a blue box says "Windows protected your PC", click **More info**, then **Run anyway**.
4. If it asks to install Python, press **Y** and wait a minute.
5. Keystone opens in your browser. Keep the black window open while you study.

Next time, just double-click **start.bat** again.

## Install on Mac

1. Open your **Downloads** folder and double-click **keystone-main.zip**.
2. Open the **keystone-main** folder, then **right-click** (or Control-click) **start.command** and choose **Open**. Click **Open** again in the box that appears.
3. If it asks to install Python, type **y**, press Return, and enter your Mac password when asked.
4. Keystone opens in your browser. Keep the Terminal window open while you study.

Next time, just double-click **start.command**.

Stuck? **[INSTALL.txt](INSTALL.txt)** has more detail and fixes for common problems.

## What's inside

| Track | Chapters | Lessons |
|---|---|---|
| 1. Python fundamentals | 12 | 93 |
| 2. SQL and databases | 12 | 104 |
| 3. Python for engineering | 11 | 88 |
| 4. Back-end development | 12 | 103 |

Each new idea comes in small steps: first on its own, then inside a function with a worked example, then in a bigger task. When a check fails, you get a plain-English tip about what probably went wrong.

The engineering and back-end tracks need a few extra packages. Each of those tracks has a lesson with an **Install** button that does it for you (it needs internet once).

## Updating

Download the zip again and extract it **over** your old folder, replacing the files. Your progress lives in the `data` folder, which isn't part of the download, so it's kept. Anything you've passed stays passed.

## Your progress

Everything is saved in the `data` folder inside Keystone's folder, with a backup copy made each time it starts. To move to a new computer, copy the `data` folder across.

---

## For teachers and contributors

Lessons are plain Python files in `courses/<track>/`. Each `chNN_*.py` is one chapter with a `CHAPTER` dict and a `LESSONS` list. The top of `content.py` lists every field a lesson can have (`lang`, `setup`, `files`, `prelude`, `timeout`, `widget` and so on). Edits show up when you refresh the page.

After changing lessons, check them:

```
python tools/validate.py          every track
python tools/validate.py sql      one track (py, sql, eng or be)
```

This confirms every solution passes and no starter passes by accident. It also protects saved progress: every lesson id ever released is listed in `courses/lesson_ids.txt`, and validation fails if one disappears. Change titles, text and order freely, but never rename or delete a lesson id.

| File | Does |
|---|---|
| `start.bat`, `start.command` | Launchers, which install Python if needed |
| `server.py` | Local web server and API |
| `runner.py`, `harness.py` | Run learners' code in a separate process and check it |
| `packages.py` | One-click package installer for tracks 3 and 4 |
| `progress.py` | XP, levels, streaks, achievements and backups |
| `content.py` | Loads the course files |
| `app/` | The browser interface |
| `courses/` | Lesson content, one folder per track |
| `tools/validate.py` | Course checker |

The app itself uses only Python's standard library (Python 3.8 or newer).
