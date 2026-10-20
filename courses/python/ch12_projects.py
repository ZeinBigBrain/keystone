CHAPTER = {
    "title": "Putting it together",
    "summary": "Two bigger exercises that use everything from the course, then what comes next.",
}

LESSONS = [
    {
        "id": "sort-key",
        "title": "Sorting by your own rule",
        "kind": "code",
        "body": """
The first project needs one tool you haven't met yet: telling `sorted()` *what* to sort by.

Give `sorted()` a `key` function. Python calls it on every item and sorts by whatever it returns:

```python
jobs = [("paint", 3), ("wire", 1), ("tile", 2)]

def by_days(job):
    return job[1]            # sort by the second value, the days

print(sorted(jobs, key=by_days))
# [('wire', 1), ('tile', 2), ('paint', 3)]
```

Note it's `key=by_days`, with no brackets. You're handing over the function itself for `sorted` to call, not calling it yourself.

## Two rules at once

If the key function returns a tuple, Python sorts by the first value, and only looks at the second when the first ones are equal:

```python
def by_days_then_name(job):
    return (job[1], job[0])
```

For **biggest first** on a number, put a minus sign in front of it: `(-job[1], job[0])` sorts by days from most to fewest, and alphabetically when two jobs take the same number of days.

You'll also see the same key written in one line as `key=lambda job: (-job[1], job[0])`. A `lambda` is just a small unnamed function. Use whichever you find easier to read.

## Your task

Write `rank(scores)`, where `scores` is a list of `(name, points)` tuples. Return a new list sorted by points, **highest first**. When two people have the same points, put them in alphabetical order.
""",
        "starter": "def by_points(pair):\n    # return what to sort by: points (biggest first), then name\n    pass\n\n\ndef rank(scores):\n    return sorted(scores, key=by_points)\n\n\nprint(rank([(\"Omar\", 7), (\"Lina\", 9), (\"Adel\", 7)]))\n",
        "tests": '''
def test_order():
    "Highest points first, ties alphabetical"
    f = need("rank")
    data = [("Omar", 7), ("Lina", 9), ("Adel", 7), ("Zed", 1)]
    v, _ = capture(f, list(data))
    want = [("Lina", 9), ("Adel", 7), ("Omar", 7), ("Zed", 1)]
    check(v == want, "rank(...) returned %r\\nexpected %r" % (v, want))
    v, _ = capture(f, [])
    check(v == [], "rank([]) should be [].")

def test_no_change():
    "Doesn't change the original list"
    data = [("b", 1), ("a", 2)]
    capture(need("rank"), data)
    check(data == [("b", 1), ("a", 2)], "The original list was changed. Use sorted(), not .sort().")
''',
        "solution": "def by_points(pair):\n    return (-pair[1], pair[0])\n\n\ndef rank(scores):\n    return sorted(scores, key=by_points)\n\n\nprint(rank([(\"Omar\", 7), (\"Lina\", 9), (\"Adel\", 7)]))\n",
        "hints": [
            "`pair[0]` is the name and `pair[1]` is the points.",
            "`return (-pair[1], pair[0])`",
        ],
    },
    {
        "id": "delivery-log",
        "title": "Project: delivery log",
        "kind": "code",
        "body": """
A store keeps a plain-text log of deliveries. Each line is `date,material,quantity`:

```
2026-10-01,cement,40
2026-10-01,sand,12
# sand was short, more due Friday
2026-10-02,cement,25

2026-10-03,sand,18
```

Some lines are comments (they start with `#`) and some are blank. Both should be ignored.

## Your task

Write `totals(log)` that takes the whole log as one string and returns a **list of tuples** `(material, total_quantity)`, sorted with the **biggest total first**. If two materials have the same total, put them in alphabetical order.

For the log above: `[("cement", 65), ("sand", 30)]`.

This one has several steps. Get each one working with **Run** and some `print()` calls before moving on:

1. split the log into lines (`log.splitlines()`)
2. skip blanks and comments (`.strip()` helps)
3. split each line on commas and add the quantity to a dict (the counting pattern from the dictionaries chapter)
4. turn the dict into a sorted list (the key function from the last lesson)
""",
        "starter": 'LOG = """2026-10-01,cement,40\n2026-10-01,sand,12\n# sand was short, more due Friday\n2026-10-02,cement,25\n\n2026-10-03,sand,18\n"""\n\n\ndef totals(log):\n    pass\n\n\nprint(totals(LOG))\n',
        "tests": '''
LOG = "2026-10-01,cement,40\\n2026-10-01,sand,12\\n# sand was short\\n2026-10-02,cement,25\\n\\n2026-10-03,sand,18\\n"

def test_example():
    "Works on the example log"
    v, _ = capture(need("totals"), LOG)
    check(v == [("cement", 65), ("sand", 30)], "Got %r" % (v,))

def test_ties():
    "Sorts biggest first, ties alphabetically"
    log = "d,rebar,10\\nd,brick,10\\nd,tiles,3\\n  \\nd,gravel,50\\n#d,ghost,999\\n"
    v, _ = capture(need("totals"), log)
    want = [("gravel", 50), ("brick", 10), ("rebar", 10), ("tiles", 3)]
    check(v == want, "Got %r\\nexpected %r" % (v, want))

def test_empty():
    "An empty log gives an empty list"
    v, _ = capture(need("totals"), "")
    check(v == [], "totals('') returned %r." % (v,))
''',
        "solution": 'LOG = """2026-10-01,cement,40\n2026-10-01,sand,12\n# sand was short, more due Friday\n2026-10-02,cement,25\n\n2026-10-03,sand,18\n"""\n\n\ndef totals(log):\n    sums = {}\n    for line in log.splitlines():\n        line = line.strip()\n        if not line or line.startswith("#"):\n            continue\n        _date, material, qty = line.split(",")\n        sums[material] = sums.get(material, 0) + int(qty)\n    return sorted(sums.items(), key=lambda pair: (-pair[1], pair[0]))\n\n\nprint(totals(LOG))\n',
        "hints": [
            "Inside the loop: `line = line.strip()`, then `if not line or line.startswith(\"#\"): continue`.",
            "`date, material, qty = line.split(\",\")` then add `int(qty)` to a dict.",
            "`sums.items()` gives `(material, total)` pairs. Sort them with a key function like `by_points` from the last lesson: `(-pair[1], pair[0])`.",
        ],
    },
    {
        "id": "gradebook",
        "title": "Project: gradebook",
        "kind": "code",
        "body": """
Last one. A class that pulls together dicts, lists, loops, errors and string formatting.

## Your task

Write a class `Gradebook` with these methods:

| Method | Does |
|---|---|
| `Gradebook()` | starts with no students |
| `add_mark(name, mark)` | records a mark for that student. A student can have many marks. If `mark` is below 0 or above 100, raise `ValueError` and don't record it. |
| `average(name)` | returns that student's average mark. If the student doesn't exist, return `None`. |
| `top_student()` | returns the name with the highest average. Ties go to whichever name comes first alphabetically. With no students, return `None`. |
| `report()` | returns a list of strings, one per student, **sorted by name**, like `"Mona: 72.5"` (average to 1 decimal place). |

A dict of name to list of marks is a good way to store things.
""",
        "starter": "class Gradebook:\n    def __init__(self):\n        pass\n\n    def add_mark(self, name, mark):\n        pass\n\n    def average(self, name):\n        pass\n\n    def top_student(self):\n        pass\n\n    def report(self):\n        pass\n\n\ng = Gradebook()\ng.add_mark(\"Mona\", 70)\ng.add_mark(\"Mona\", 75)\ng.add_mark(\"Ali\", 64)\nprint(g.average(\"Mona\"))\nprint(g.top_student())\nfor line in g.report():\n    print(line)\n",
        "tests": '''
def make():
    g = need("Gradebook")()
    for n, m in [("Mona", 70), ("Mona", 75), ("Ali", 64), ("Zara", 90), ("Ali", 80)]:
        g.add_mark(n, m)
    return g

def test_average():
    "average works, and gives None for unknown students"
    g = make()
    check(g.average("Mona") == 72.5, "average('Mona') returned %r." % g.average("Mona"))
    check(g.average("Ali") == 72, "average('Ali') returned %r." % g.average("Ali"))
    check(g.average("Nobody") is None, "average of an unknown student should be None.")

def test_invalid():
    "Marks outside 0 to 100 raise ValueError and aren't stored"
    g = make()
    for bad in (-1, 101):
        try:
            g.add_mark("Mona", bad)
        except ValueError:
            pass
        else:
            check(False, "add_mark('Mona', %r) should raise ValueError." % bad)
    check(g.average("Mona") == 72.5, "A rejected mark still changed Mona's average.")
    g.add_mark("Edge", 0)
    g.add_mark("Edge", 100)
    check(g.average("Edge") == 50, "0 and 100 are both allowed.")

def test_top():
    "top_student, including ties and an empty book"
    G = need("Gradebook")
    check(G().top_student() is None, "An empty gradebook should give None.")
    g = make()
    check(g.top_student() == "Zara", "top_student() returned %r." % g.top_student())
    g2 = G()
    g2.add_mark("Ola", 60)
    g2.add_mark("Ben", 60)
    check(g2.top_student() == "Ben", "On a tie, the alphabetically first name should win.")

def test_report():
    "report lines are sorted by name, 1 decimal place"
    r = make().report()
    want = ["Ali: 72.0", "Mona: 72.5", "Zara: 90.0"]
    check(r == want, "report() returned %r\\nexpected %r" % (r, want))
''',
        "solution": 'class Gradebook:\n    def __init__(self):\n        self.marks = {}\n\n    def add_mark(self, name, mark):\n        if mark < 0 or mark > 100:\n            raise ValueError(f"mark {mark} is outside 0 to 100")\n        self.marks.setdefault(name, []).append(mark)\n\n    def average(self, name):\n        if name not in self.marks:\n            return None\n        scores = self.marks[name]\n        return sum(scores) / len(scores)\n\n    def top_student(self):\n        best = None\n        for name in sorted(self.marks):\n            if best is None or self.average(name) > self.average(best):\n                best = name\n        return best\n\n    def report(self):\n        return [f"{name}: {self.average(name):.1f}" for name in sorted(self.marks)]\n\n\ng = Gradebook()\ng.add_mark("Mona", 70)\ng.add_mark("Mona", 75)\ng.add_mark("Ali", 64)\nprint(g.average("Mona"))\nprint(g.top_student())\nfor line in g.report():\n    print(line)\n',
        "hints": [
            "In `__init__`, `self.marks = {}`. In `add_mark`, check the range first, then append to that student's list, creating the list if it's their first mark.",
            "For `top_student`, loop over `sorted(self.marks)` and keep the best so far. Only replace it when you find a strictly higher average, and ties will stay with the earlier name.",
            'For `report`, an f-string with `:.1f` formats the average: `f"{name}: {avg:.1f}"`.',
        ],
    },
    {
        "id": "whats-next",
        "title": "What comes next",
        "kind": "read",
        "body": """
That's the whole Python fundamentals course. You can now write functions, use the main data structures, handle errors, and build your own classes. That's enough Python to do real work.

## Keep using it

The fastest way to lock this in is to use it on something you actually need, while it's still fresh. A few ideas:

- a script that renames or sorts a folder of files
- something that reads a CSV export and summarises it
- a small calculator for a formula you use a lot at work

You'll get stuck, look things up, and learn more in a week than another course would teach you.

## The next tracks

The menu shows the full path. In order:

1. **SQL and databases.** Storing data properly and asking questions of it. Python ships with SQLite, so nothing extra to install.
2. **Python for engineering.** NumPy, pandas, matplotlib and SciPy for numbers, data and plots.
3. **Back-end development.** HTTP, servers, APIs, Git, Docker and deployment.

Pick them up in that order. Each one starts gently and assumes only what this course covered.

## Things this course skipped

Worth looking up when you need them: `*args` and `**kwargs`, generators, decorators and type hints. Several of these come up properly in the later tracks, along with the `csv` and `json` modules.
""",
    },
]
