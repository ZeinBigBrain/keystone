"""
Checks every lesson in every playable track.

    py tools/validate.py            (every track)
    py tools/validate.py sql        (just one track, by its id: py, sql, eng, be)

For each code lesson: the solution must pass all checks, and the starter code
must NOT pass (otherwise the exercise is free). Quizzes must have a valid
answer index. Run this after adding or editing lessons.

It also protects saved progress: every id listed in courses/lesson_ids.txt
must still exist (progress is stored by lesson id, so renaming or deleting one
would orphan it). When everything passes, new ids are added to that file.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

import content  # noqa: E402
from runner import run_code  # noqa: E402


IDS_FILE = os.path.join(ROOT, "courses", "lesson_ids.txt")


def known_ids():
    if not os.path.exists(IDS_FILE):
        return []
    with open(IDS_FILE, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def main():
    cat = content.get()
    problems = 0
    registered = known_ids()
    for lid in registered:
        if lid not in cat["lessons"]:
            problems += 1
            print("FAIL %s: this lesson id is gone. Saved progress uses it, so put it back "
                  "(you can change its title, text and position, never its id)." % lid)
    count = {"read": 0, "quiz": 0, "code": 0}
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for lid in cat["order"]:
        if only and not lid.startswith(only + ":"):
            continue
        les = cat["lessons"][lid]
        kind = les["kind"]
        count[kind] += 1
        if kind == "code":
            for field in ("starter", "tests", "solution"):
                if field not in les:
                    print("FAIL %s: missing %s" % (lid, field)); problems += 1
            if not les.get("hints"):
                print("WARN %s: no hints" % lid)
            res = run_code(les["solution"], les["tests"], "submit", les)
            if not res["passed"]:
                problems += 1
                print("FAIL %s: solution doesn't pass" % lid)
                if res.get("error"):
                    print("     error:", res["error"])
                for t in res["tests"]:
                    if not t["ok"]:
                        print("     %s -> %s" % (t["name"], t["message"]))
            res2 = run_code(les["starter"], les["tests"], "submit", les)
            if res2["passed"]:
                problems += 1
                print("FAIL %s: starter code already passes" % lid)
        elif kind == "quiz":
            if not (0 <= les["answer"] < len(les["options"])):
                problems += 1
                print("FAIL %s: answer index out of range" % lid)
    new_ids = [i for i in cat["order"] if i not in registered]
    if new_ids and not problems and not only:
        with open(IDS_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_ids) + "\n")
        print("Registered %d new lesson id(s) in courses/lesson_ids.txt." % len(new_ids))
    print("\n%d lessons (%d read, %d quiz, %d code). %s" % (
        sum(count.values()), count["read"], count["quiz"], count["code"],
        "All good." if not problems else "%d problem(s)." % problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
