"""
Keystone - a local, gamified coding course app.
Run:  py server.py   (or double-click start.bat on Windows)
Then it opens http://127.0.0.1:8765 in your browser.
"""
import json
import mimetypes
import os
import socket
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

if sys.version_info < (3, 8):
    sys.exit("Keystone needs Python 3.8 or newer. You have %s." % sys.version.split()[0])

sys.dont_write_bytecode = True  # keep __pycache__ folders out of the app

import content
import packages
import progress
from runner import run_code

HERE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(HERE, "app")
SOLUTION_UNLOCK_FAILS = 3


class Handler(BaseHTTPRequestHandler):
    server_version = "Keystone/1.0"

    def log_message(self, fmt, *args):  # keep the console quiet
        pass

    # ---------- helpers ----------
    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 2_000_000:
            raise ValueError("Request too large")
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _lesson(self, lid):
        cat = content.get()
        les = cat["lessons"].get(lid)
        if not les:
            raise KeyError("No lesson called %s" % lid)
        return cat, les

    # ---------- GET ----------
    def do_GET(self):
        url = urlparse(self.path)
        try:
            if url.path == "/api/catalog":
                cat = content.get()
                return self._send(200, {"tracks": cat["tracks"], "order": cat["order"]})
            if url.path == "/api/progress":
                cat = content.get()
                with progress.locked():
                    data = progress.load()
                return self._send(200, progress.summary(data, cat))
            if url.path == "/api/packages":
                group = parse_qs(url.query).get("group", ["engineering"])[0]
                return self._send(200, packages.status(group))
            if url.path == "/api/lesson":
                lid = parse_qs(url.query).get("id", [""])[0]
                cat, les = self._lesson(lid)
                with progress.locked():
                    data = progress.load()
                    st = dict(progress.lesson_state(data, lid))
                    data["last_lesson"] = lid
                    progress.save(data)
                out = content.public_lesson(les)
                out["state"] = {
                    "done": st["done"], "xp": st["xp"], "hints_used": st["hints"],
                    "fails": st["fails"], "solution_seen": st["solution_seen"],
                    "code": st["code"],
                }
                out["hints"] = les.get("hints", [])[:st["hints"]]
                out["solution_unlocked"] = (st["fails"] >= SOLUTION_UNLOCK_FAILS
                                            or st["done"]) and les["kind"] == "code"
                if les["kind"] == "quiz" and st["done"]:
                    out["answer"] = les["answer"]
                    out["explain"] = les.get("explain", "")
                return self._send(200, out)
            return self._static(url.path)
        except KeyError as e:
            return self._send(404, {"error": str(e)})
        except Exception as e:  # show content errors in the UI, not a blank page
            return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

    def _static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        full = os.path.normpath(os.path.join(APP_DIR, path.lstrip("/")))
        if not full.startswith(APP_DIR) or not os.path.isfile(full):
            return self._send(404, "Not found", "text/plain")
        # Explicit types: on Windows, mimetypes reads the registry and can get .js wrong
        known = {".html": "text/html", ".css": "text/css", ".js": "text/javascript",
                 ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon"}
        ext = os.path.splitext(full)[1].lower()
        ctype = known.get(ext) or mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            ctype += "; charset=utf-8"
        with open(full, "rb") as f:
            return self._send(200, f.read(), ctype)

    # ---------- POST ----------
    def do_POST(self):
        url = urlparse(self.path)
        try:
            body = self._json_body()
            handler = {
                "/api/run": self.api_run,
                "/api/submit": self.api_submit,
                "/api/answer": self.api_answer,
                "/api/read": self.api_read,
                "/api/hint": self.api_hint,
                "/api/solution": self.api_solution,
                "/api/save": self.api_save,
                "/api/reset-lesson": self.api_reset_lesson,
                "/api/reset-all": self.api_reset_all,
                "/api/install-packages": lambda body: packages.start_install(body.get("group", "engineering")),
            }.get(url.path)
            if not handler:
                return self._send(404, {"error": "Unknown endpoint"})
            return self._send(200, handler(body))
        except KeyError as e:
            return self._send(404, {"error": str(e)})
        except Exception as e:
            return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

    def api_run(self, body):
        _cat, les = self._lesson(body["id"])
        code = body.get("code", "")
        with progress.locked():
            data = progress.load()
            progress.lesson_state(data, les["full_id"])["code"] = code
            progress.save(data)
        return run_code(code, "", "run", les)

    def api_submit(self, body):
        cat, les = self._lesson(body["id"])
        if les["kind"] != "code":
            raise ValueError("Not a code lesson")
        code = body.get("code", "")
        result = run_code(code, les.get("tests", ""), "submit", les)
        with progress.locked():
            data = progress.load()
            st = progress.lesson_state(data, les["full_id"])
            st["code"] = code
            st["attempts"] += 1
            result["earned"] = 0
            result["first_time"] = False
            if result["passed"]:
                xp = progress.code_xp(les["xp"], st)
                if progress.mark_done(data, les["full_id"], xp):
                    result["earned"] = xp
                    result["first_time"] = True
            else:
                if not st["done"]:
                    st["fails"] += 1
            result["fails"] = st["fails"]
            result["solution_unlocked"] = st["fails"] >= SOLUTION_UNLOCK_FAILS or st["done"]
            result["new_achievements"] = progress.update_achievements(data, cat)
            progress.save(data)
            result["progress"] = progress.summary(data, cat)
        return result

    def api_answer(self, body):
        cat, les = self._lesson(body["id"])
        if les["kind"] != "quiz":
            raise ValueError("Not a quiz")
        choice = int(body.get("choice", -1))
        correct = choice == les["answer"]
        out = {"correct": correct, "earned": 0, "first_time": False}
        with progress.locked():
            data = progress.load()
            st = progress.lesson_state(data, les["full_id"])
            if correct:
                xp = les["xp"] if st["quiz_wrong"] == 0 else min(3, les["xp"])
                if progress.mark_done(data, les["full_id"], xp):
                    out["earned"] = xp
                    out["first_time"] = True
                out["explain"] = les.get("explain", "")
                out["answer"] = les["answer"]
            elif not st["done"]:
                st["quiz_wrong"] += 1
            out["new_achievements"] = progress.update_achievements(data, cat)
            progress.save(data)
            out["progress"] = progress.summary(data, cat)
        return out

    def api_read(self, body):
        cat, les = self._lesson(body["id"])
        out = {"earned": 0, "first_time": False}
        with progress.locked():
            data = progress.load()
            if progress.mark_done(data, les["full_id"], les["xp"]):
                out["earned"] = les["xp"]
                out["first_time"] = True
            out["new_achievements"] = progress.update_achievements(data, cat)
            progress.save(data)
            out["progress"] = progress.summary(data, cat)
        return out

    def api_hint(self, body):
        _cat, les = self._lesson(body["id"])
        hints = les.get("hints", [])
        with progress.locked():
            data = progress.load()
            st = progress.lesson_state(data, les["full_id"])
            if st["hints"] < len(hints) and not st["done"]:
                st["hints"] += 1
            elif st["done"]:
                st["hints"] = len(hints)  # free to browse once finished
            progress.save(data)
            shown = hints[:st["hints"]]
        return {"hints": shown, "hint_count": len(hints),
                "xp_now": progress.code_xp(les["xp"], st) if les["kind"] == "code" else les["xp"]}

    def api_solution(self, body):
        _cat, les = self._lesson(body["id"])
        with progress.locked():
            data = progress.load()
            st = progress.lesson_state(data, les["full_id"])
            if not (st["done"] or st["fails"] >= SOLUTION_UNLOCK_FAILS):
                return {"error": "The solution unlocks after %d failed submissions." % SOLUTION_UNLOCK_FAILS}
            if not st["done"]:
                st["solution_seen"] = True
            progress.save(data)
        return {"solution": les.get("solution", "")}

    def api_save(self, body):
        _cat, les = self._lesson(body["id"])
        with progress.locked():
            data = progress.load()
            progress.lesson_state(data, les["full_id"])["code"] = body.get("code", "")
            progress.save(data)
        return {"ok": True}

    def api_reset_lesson(self, body):
        _cat, les = self._lesson(body["id"])
        with progress.locked():
            data = progress.load()
            st = progress.lesson_state(data, les["full_id"])
            st["code"] = None
            progress.save(data)
        return {"starter": les.get("starter", "")}

    def api_reset_all(self, body):
        if body.get("confirm") != "RESET":
            raise ValueError("Confirmation missing")
        with progress.locked():
            backup = progress.backup("before-reset")
            progress.save(progress._empty())
        return {"ok": True, "backup": os.path.basename(backup) if backup else None}


def find_port(preferred=8765):
    for port in [preferred] + list(range(8766, 8800)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit("No free port found between 8765 and 8799.")


def main():
    # Fail early and clearly if the course files have a mistake in them
    try:
        cat = content.get()
    except Exception as e:
        print("There's a problem in the course files:\n  %s: %s" % (type(e).__name__, e))
        input("Press Enter to close.")
        return
    n = len(cat["lessons"])
    try:
        with progress.locked():
            progress.backup("start")
    except OSError as e:
        print("Couldn't back up your progress (%s). Carrying on." % e)
    port = find_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = "http://127.0.0.1:%d" % port
    print("Keystone is running at %s  (%d lessons loaded)" % (url, n))
    print("Leave this window open while you study. Close it (or press Ctrl+C) to stop.")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
