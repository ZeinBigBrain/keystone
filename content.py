"""
Loads course content.

courses/catalog.py lists the tracks (in learning order). A track that has a
"folder" is playable: every chNN_*.py file in that folder is one chapter and
defines CHAPTER (dict) and LESSONS (list of dicts). Files are re-read whenever
they change on disk, so you can edit or add lessons while the app is running.

Lesson fields:
    id        unique within the course (letters, digits, dashes)
    title
    kind      "read" | "quiz" | "code"
    body      lesson text (Markdown)
    -- code lessons --
    starter   starting code in the editor
    tests     test code (see harness.py for the helpers it can use)
    solution  a correct answer (unlocks after 3 failed submits)
    hints     list of hints, from gentle to blunt
    lang      "python" (default), "sql" (runs against an SQLite database built
              from setup) or "text" (not run; the checks read what was typed)
    setup     SQL script that builds the database for a "sql" lesson
    files     {filename: text} written into the sandbox before each run
    prelude   hidden Python run before the learner's code, in the same
              namespace (used to start a local test server for HTTP lessons)
    timeout   seconds before a run is stopped (default 6)
    widget    optional panel shown under a read lesson ("packages" shows the
              engineering package installer)
    -- quiz lessons --
    question, options (list), answer (index into options), explain
    xp        optional, overrides the default for its kind
"""
import importlib.util
import os
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.join(HERE, "courses")

DEFAULT_XP = {"read": 5, "quiz": 10, "code": 30}

_lock = threading.Lock()
_cache = {"key": None, "data": None}


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fingerprint():
    parts = []
    for root, _dirs, files in os.walk(COURSES):
        for f in files:
            if f.endswith((".py", ".sql", ".csv")):
                p = os.path.join(root, f)
                parts.append((p, os.path.getmtime(p)))
    return tuple(sorted(parts))


def _build():
    catalog = _load_module(os.path.join(COURSES, "catalog.py"), "ks_catalog")
    tracks = []
    lessons = {}  # full id "track:lesson" -> lesson dict (with extra keys)
    for t in catalog.TRACKS:
        track = {
            "id": t["id"],
            "title": t["title"],
            "blurb": t.get("blurb", ""),
            "prereq": t.get("prereq", ""),
            "chapters": [],
            "playable": bool(t.get("folder")),
        }
        if t.get("folder"):
            folder = os.path.join(COURSES, t["folder"])
            files = sorted(f for f in os.listdir(folder)
                           if f.startswith("ch") and f.endswith(".py"))
            for n, f in enumerate(files):
                mod = _load_module(os.path.join(folder, f), "ks_%s_%d" % (t["id"], n))
                ch = {
                    "title": mod.CHAPTER["title"],
                    "summary": mod.CHAPTER.get("summary", ""),
                    "lessons": [],
                    "planned_topics": [],
                }
                for les in mod.LESSONS:
                    fid = "%s:%s" % (t["id"], les["id"])
                    if fid in lessons:
                        raise ValueError("Duplicate lesson id: " + fid)
                    entry = dict(les)
                    entry["full_id"] = fid
                    entry["track"] = t["id"]
                    entry["chapter"] = ch["title"]
                    entry["xp"] = les.get("xp", DEFAULT_XP[les["kind"]])
                    lessons[fid] = entry
                    ch["lessons"].append({
                        "id": fid,
                        "title": les["title"],
                        "kind": les["kind"],
                        "xp": entry["xp"],
                    })
                track["chapters"].append(ch)
        else:
            for ch in t.get("outline", []):
                track["chapters"].append({
                    "title": ch["title"],
                    "summary": ch.get("summary", ""),
                    "lessons": [],
                    "planned_topics": ch.get("topics", []),
                })
        tracks.append(track)

    # Sequence for "next lesson" and chapter lookups
    order = [lid for tr in tracks for ch in tr["chapters"] for lid in
             [l["id"] for l in ch["lessons"]]]
    return {"tracks": tracks, "lessons": lessons, "order": order}


def get():
    with _lock:
        key = _fingerprint()
        if key != _cache["key"]:
            _cache["data"] = _build()
            _cache["key"] = key
        return _cache["data"]


def public_lesson(lesson):
    """What the browser is allowed to see (no tests, solution or hints)."""
    out = {
        "id": lesson["full_id"],
        "title": lesson["title"],
        "kind": lesson["kind"],
        "body": lesson.get("body", ""),
        "chapter": lesson["chapter"],
        "track": lesson["track"],
        "xp": lesson["xp"],
        "hint_count": len(lesson.get("hints", [])),
        "widget": lesson.get("widget"),
    }
    if lesson["kind"] == "code":
        out["starter"] = lesson.get("starter", "")
        out["lang"] = lesson.get("lang", "python")
    if lesson["kind"] == "quiz":
        out["question"] = lesson["question"]
        out["options"] = lesson["options"]
    return out
