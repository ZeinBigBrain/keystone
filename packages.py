"""
One-click installer for the packages the engineering and back-end tracks use.

The app calls status() to show what's installed, and start_install() to run
pip in the background with the same Python that runs Keystone. It installs
only what's missing, into the user's own package folder (no admin rights
needed), or into the active virtual environment if there is one.
"""
import importlib.util
import os
import subprocess
import sys
import threading

# group -> [(import name, pip name)]
GROUPS = {
    "engineering": [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("scipy", "scipy"),
        ("openpyxl", "openpyxl"),   # lets pandas read and write .xlsx files
    ],
    "backend": [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),     # runs FastAPI apps
        ("httpx", "httpx"),         # FastAPI's TestClient needs it
        ("requests", "requests"),
    ],
}
PACKAGES = GROUPS["engineering"]  # default group

_state = {"running": False, "log": "", "ok": None}
_lock = threading.Lock()


_CHECK = r"""
import importlib, json
out = {}
for mod in %r:
    try:
        m = importlib.import_module(mod)
        out[mod] = str(getattr(m, "__version__", "installed"))
    except Exception:
        out[mod] = None
print(json.dumps(out))
"""


def _installed(group="engineering"):
    """{import name: version or None}. Asked of a fresh Python, so packages
    installed a moment ago (or into a brand-new user folder) are seen."""
    import json
    mods = [m for m, _ in GROUPS.get(group, PACKAGES)]
    try:
        out = subprocess.run([sys.executable, "-c", _CHECK % (mods,)],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=120,
                             **({"creationflags": 0x08000000} if os.name == "nt" else {}))
        return json.loads(out.stdout.decode().strip().splitlines()[-1])
    except Exception:
        return {m: (importlib.util.find_spec(m) and "installed") for m in mods}


def status(group="engineering"):
    found = _installed(group)
    rows = [{"name": pip_name, "installed": bool(found.get(mod)), "version": found.get(mod)}
            for mod, pip_name in GROUPS.get(group, PACKAGES)]
    with _lock:
        st = dict(_state)
    return {"packages": rows, "python": sys.version.split()[0],
            "running": st["running"], "log": st["log"][-4000:], "ok": st["ok"]}


def _in_venv():
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def _run(args):
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw)
    for raw in p.stdout:
        line = raw.decode("utf-8", errors="replace")
        with _lock:
            _state["log"] += line
    return p.wait()


def _worker(missing):
    try:
        # Make sure pip itself is there (some Python installs leave it out)
        if importlib.util.find_spec("pip") is None:
            with _lock:
                _state["log"] += "pip is missing, installing it first...\n"
            _run([sys.executable, "-m", "ensurepip", "--upgrade"])
        args = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
        if not _in_venv():
            args.append("--user")
        args += missing
        with _lock:
            _state["log"] += "Running: pip install %s\n\n" % " ".join(missing)
        code = _run(args)
        importlib.invalidate_caches()
        with _lock:
            _state["ok"] = code == 0
            _state["log"] += "\nDone." if code == 0 else \
                "\nThe install didn't finish (exit code %d). Check your internet connection and try again." % code
    except Exception as e:
        with _lock:
            _state["ok"] = False
            _state["log"] += "\nCouldn't run pip: %s" % e
    finally:
        with _lock:
            _state["running"] = False


def start_install(group="engineering"):
    with _lock:
        if _state["running"]:
            return {"started": False, "reason": "already running"}
    found = _installed(group)
    missing = [pip_name for mod, pip_name in GROUPS.get(group, PACKAGES) if not found.get(mod)]
    with _lock:
        if _state["running"]:
            return {"started": False, "reason": "already running"}
        if not missing:
            _state.update(log="Everything is already installed.\n", ok=True)
            return {"started": False, "reason": "nothing to install"}
        _state.update(running=True, log="", ok=None)
    threading.Thread(target=_worker, args=(missing,), daemon=True).start()
    return {"started": True, "missing": missing}
