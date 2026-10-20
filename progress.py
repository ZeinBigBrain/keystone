"""
Progress, XP, levels, streaks and achievements. Stored in data/progress.json.

XP rules
    read lesson     5 XP
    quiz            10 XP first try, 3 XP after a wrong answer
    code exercise   30 XP, minus 20% per hint used (never below 40%)
                    0 XP if you looked at the solution before passing
Levels: level L starts at 50 * L * (L - 1) XP  (L2 = 100, L3 = 300, L4 = 600 ...)
Streak: consecutive days on which you completed at least one lesson.

Keeping progress safe
    Progress is keyed by lesson id ("py:while" and so on), so lessons can be
    added, reordered or reworded without touching anyone's record. Never
    rename or delete a lesson id: tools/validate.py checks every id against
    courses/lesson_ids.txt and fails if one has gone.
    A copy of progress.json goes into data/backups each time the app starts
    (only when it has changed since the last copy), and before "Reset all".
    If progress.json is ever damaged, the newest backup is loaded instead.
"""
import datetime
import json
import os
import shutil
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "data", "progress.json")
BACKUP_DIR = os.path.join(HERE, "data", "backups")
KEEP_START_BACKUPS = 30
_lock = threading.Lock()


def _empty():
    return {"version": 1, "lessons": {}, "days": [], "achievements": {},
            "last_lesson": None}


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("lessons", {}), dict):
        raise ValueError("not a Keystone progress file")
    return data


def _backups():
    """Backup files, newest first."""
    if not os.path.isdir(BACKUP_DIR):
        return []
    files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
             if f.startswith("progress-") and f.endswith(".json")]
    return sorted(files, key=os.path.getmtime, reverse=True)


def load():
    if not os.path.exists(PATH):
        return _empty()
    try:
        data = _read(PATH)
    except (ValueError, OSError):
        # Keep the damaged file for reference, then fall back to the newest
        # backup that reads cleanly rather than starting from nothing.
        bad = PATH + ".damaged"
        try:
            os.replace(PATH, bad)
        except OSError:
            pass
        data = None
        for b in _backups():
            try:
                data = _read(b)
                break
            except (ValueError, OSError):
                continue
        if data is None:
            return _empty()
        save(data)
    base = _empty()
    base.update(data)
    return base


def backup(reason="start"):
    """Copy progress.json into data/backups. For start-up copies, skip it if
    nothing changed since the last one, and keep only the newest few."""
    if not os.path.exists(PATH):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(PATH, "rb") as f:
        current = f.read()
    tag = "-%s.json" % reason
    same_kind = [b for b in _backups() if b.endswith(tag)]
    if reason == "start" and same_kind:
        try:
            with open(same_kind[0], "rb") as f:
                if f.read() == current:
                    return same_kind[0]
        except OSError:
            pass
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, "progress-%s%s" % (stamp, tag))
    shutil.copy2(PATH, dest)
    if reason == "start":
        for old in [b for b in _backups() if b.endswith(tag)][KEEP_START_BACKUPS:]:
            try:
                os.remove(old)
            except OSError:
                pass
    return dest


def save(data):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, PATH)


def today():
    return datetime.date.today().isoformat()


def lesson_state(data, lid):
    return data["lessons"].setdefault(lid, {
        "done": False, "xp": 0, "attempts": 0, "fails": 0,
        "hints": 0, "solution_seen": False, "code": None,
        "quiz_wrong": 0, "completed_at": None,
    })


# ---------- derived numbers ----------

def total_xp(data):
    return sum(s.get("xp", 0) for s in data["lessons"].values())


def level_for(xp):
    level = 1
    while xp >= 50 * (level + 1) * level:
        level += 1
    return level


def level_bounds(level):
    return 50 * level * (level - 1), 50 * (level + 1) * level


def streaks(data):
    days = sorted(set(data["days"]))
    if not days:
        return 0, 0
    as_dates = [datetime.date.fromisoformat(d) for d in days]
    longest = run = 1
    for a, b in zip(as_dates, as_dates[1:]):
        run = run + 1 if (b - a).days == 1 else 1
        longest = max(longest, run)
    # Current streak only counts if the last active day is today or yesterday
    last = as_dates[-1]
    gap = (datetime.date.today() - last).days
    if gap > 1:
        return 0, longest
    cur = 1
    for i in range(len(as_dates) - 1, 0, -1):
        if (as_dates[i] - as_dates[i - 1]).days == 1:
            cur += 1
        else:
            break
    return cur, longest


# ---------- achievements ----------

ACHIEVEMENTS = [
    ("first-step", "First step", "Complete your first lesson"),
    ("ten-down", "Getting going", "Complete 10 lessons"),
    ("fifty-down", "Half a hundred", "Complete 50 lessons"),
    ("clean-five", "No help needed", "Pass 5 code exercises without hints"),
    ("clean-twenty", "Self-reliant", "Pass 20 code exercises without hints"),
    ("streak-3", "Warming up", "Reach a 3-day streak"),
    ("streak-7", "One full week", "Reach a 7-day streak"),
    ("streak-30", "Habit formed", "Reach a 30-day streak"),
    ("level-5", "Level 5", "Reach level 5"),
    ("level-10", "Level 10", "Reach level 10"),
    ("chapter", "Chapter cleared", "Finish every lesson in a chapter"),
    ("course", "Course complete", "Finish every lesson in a course"),
]


def _earned(data, catalog):
    done = {k for k, v in data["lessons"].items() if v.get("done")}
    clean = sum(1 for k, v in data["lessons"].items()
                if v.get("done") and v.get("hints", 0) == 0
                and not v.get("solution_seen")
                and catalog["lessons"].get(k, {}).get("kind") == "code")
    cur, longest = streaks(data)
    lvl = level_for(total_xp(data))
    chapter_done = course_done = False
    for tr in catalog["tracks"]:
        ids_in_track = []
        for ch in tr["chapters"]:
            ids = [l["id"] for l in ch["lessons"]]
            ids_in_track += ids
            if ids and all(i in done for i in ids):
                chapter_done = True
        if ids_in_track and all(i in done for i in ids_in_track):
            course_done = True
    return {
        "first-step": len(done) >= 1,
        "ten-down": len(done) >= 10,
        "fifty-down": len(done) >= 50,
        "clean-five": clean >= 5,
        "clean-twenty": clean >= 20,
        "streak-3": longest >= 3,
        "streak-7": longest >= 7,
        "streak-30": longest >= 30,
        "level-5": lvl >= 5,
        "level-10": lvl >= 10,
        "chapter": chapter_done,
        "course": course_done,
    }


def update_achievements(data, catalog):
    """Record newly earned achievements. Returns the list of new ones."""
    new = []
    for key, ok in _earned(data, catalog).items():
        if ok and key not in data["achievements"]:
            data["achievements"][key] = today()
            new.append(key)
    names = {k: (t, d) for k, t, d in ACHIEVEMENTS}
    return [{"id": k, "title": names[k][0], "desc": names[k][1]} for k in new]


def summary(data, catalog):
    xp = total_xp(data)
    lvl = level_for(xp)
    lo, hi = level_bounds(lvl)
    cur, longest = streaks(data)
    done = sorted(k for k, v in data["lessons"].items() if v.get("done"))
    return {
        "xp": xp,
        "level": lvl,
        "level_floor": lo,
        "level_next": hi,
        "streak": cur,
        "longest_streak": longest,
        "active_today": today() in data["days"],
        "done": done,
        "last_lesson": data.get("last_lesson"),
        "achievements": [
            {"id": k, "title": t, "desc": d,
             "earned": data["achievements"].get(k)}
            for k, t, d in ACHIEVEMENTS
        ],
        "days": sorted(set(data["days"]))[-120:],
    }


def mark_done(data, lid, xp):
    st = lesson_state(data, lid)
    newly = not st["done"]
    if newly:
        st["done"] = True
        st["xp"] = xp
        st["completed_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        if today() not in data["days"]:
            data["days"].append(today())
    return newly


def code_xp(base, st):
    if st.get("solution_seen"):
        return 0
    factor = max(0.4, 1 - 0.2 * st.get("hints", 0))
    return int(round(base * factor))


def locked():
    return _lock
