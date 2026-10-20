"""Runs learner code in a separate Python process with a time limit."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "harness.py")
MARKER = "@@KEYSTONE_RESULT@@"
TIMEOUT_SECONDS = 6


SANDBOX = os.path.join(HERE, "data", "sandbox")


def run_code(code, tests="", mode="run", lesson=None):
    """lesson (optional) supplies per-lesson settings:
    lang ("python", "sql" or "text"), setup (SQL run before the learner's),
    files ({name: text} written into the sandbox first) and timeout (seconds)."""
    lesson = lesson or {}
    os.makedirs(SANDBOX, exist_ok=True)
    timeout = lesson.get("timeout", TIMEOUT_SECONDS)
    job = json.dumps({"code": code, "tests": tests, "mode": mode,
                      "lang": lesson.get("lang", "python"),
                      "setup": lesson.get("setup", ""),
                      "files": lesson.get("files", {}),
                      "prelude": lesson.get("prelude", "")})
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MPLBACKEND"] = "Agg"  # plots are saved or checked, never opened in a window
    # Submissions run in a fresh, empty folder so files left over from earlier
    # runs can't make a check pass. Plain runs use data/sandbox itself, so
    # you can open whatever your code writes.
    workdir = tempfile.mkdtemp(prefix="check-", dir=SANDBOX) if mode == "submit" else SANDBOX
    try:
        return _execute(job, timeout, workdir, env)
    finally:
        if workdir != SANDBOX:
            shutil.rmtree(workdir, ignore_errors=True)


def _execute(job, timeout, workdir, env):
    kwargs = {}
    if os.name == "nt":
        # Stops a console window flashing up on Windows
        kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    try:
        proc = subprocess.run(
            [sys.executable, "-I", HARNESS],
            input=job.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            cwd=workdir,
            env=env,
            **kwargs
        )
    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Your code took longer than %d seconds and was stopped. "
                     "Look for a loop that never ends." % timeout,
            "tests": [],
            "passed": False,
        }

    out = proc.stdout.decode("utf-8", errors="replace")
    idx = out.rfind(MARKER)
    if idx == -1:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        return {
            "output": out,
            "error": "The runner crashed. " + (err[-1500:] if err else "No details."),
            "tests": [],
            "passed": False,
        }
    try:
        return json.loads(out[idx + len(MARKER):].strip())
    except ValueError:
        return {"output": "", "error": "Couldn't read the runner's result.",
                "tests": [], "passed": False}
