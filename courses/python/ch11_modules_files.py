CHAPTER = {
    "title": "Modules and files",
    "summary": "Using Python's standard library, and reading and writing files.",
}

LESSONS = [
    {
        "id": "imports",
        "title": "Importing modules",
        "kind": "code",
        "body": """
Python comes with a large **standard library**: modules full of ready-made functions. You load one with `import`:

```python
import math
print(math.sqrt(16))   # 4.0
print(math.pi)         # 3.141592653589793
```

Or pull out just the names you want:

```python
from math import sqrt, pi
print(sqrt(16))
```

A few modules worth knowing about early:

| Module | For |
|---|---|
| `math` | `sqrt`, `pi`, `ceil`, `floor`, trig functions, `isclose` |
| `random` | random numbers and picks |
| `datetime` | dates, times and the gaps between them |
| `statistics` | `mean`, `median`, `stdev` |
| `csv`, `json` | reading and writing those file formats |
| `pathlib` | working with file paths |

## Your task

Write `bags_needed(volume_m3, m3_per_bag)` that returns how many whole bags you need to cover a volume. You can't buy part of a bag, so always round **up**. Use `math.ceil`.

`bags_needed(1.0, 0.3)` is 4, because 3 bags only covers 0.9.

> **Watch out for floats here.** Remember from Variables and types that decimals aren't stored exactly. `0.9 / 0.3` comes out as `3.0000000000000004`, so `math.ceil` rounds it up to 4 when the right answer is 3. The checks include that case. The fix is to round the division to a sensible number of places first, then take the ceiling: `math.ceil(round(volume_m3 / m3_per_bag, 9))`.
""",
        "starter": "def bags_needed(volume_m3, m3_per_bag):\n    pass\n",
        "tests": '''
def test_values():
    "Rounds up to whole bags"
    f = need("bags_needed")
    for args, want in [((1.0, 0.3), 4), ((0.9, 0.3), 3), ((2, 0.5), 4), ((0.01, 1), 1), ((10, 3), 4)]:
        v, _ = capture(f, *args)
        check(v == want, "bags_needed%r returned %r, expected %d." % (args, v, want))
        check(isinstance(v, int), "Return a whole number (an int).")

def test_import():
    "Uses the math module"
    check("import math" in CODE or "from math import" in CODE, "Import math and use math.ceil.")
''',
        "solution": "import math\n\n\ndef bags_needed(volume_m3, m3_per_bag):\n    return math.ceil(round(volume_m3 / m3_per_bag, 9))\n",
        "hints": [
            "Put `import math` at the top of your code, outside the function.",
            "`math.ceil(volume_m3 / m3_per_bag)`. Watch out though: `0.9 / 0.3` is `3.0000000000000004` in floating point, so ceil gives 4. Rounding the division to a few decimal places first fixes it.",
        ],
    },
    {
        "id": "dates",
        "title": "Dates",
        "kind": "code",
        "body": """
The `datetime` module handles dates properly, including month lengths and leap years, so you never have to.

```python
from datetime import date, timedelta

start = date(2026, 10, 1)
finish = date(2026, 12, 25)
print((finish - start).days)            # 85
print(start + timedelta(days=30))       # 2026-10-31
print(start.strftime("%d %b %Y"))       # 01 Oct 2026
print(date.fromisoformat("2026-03-15")) # text to a date
```

Subtracting two dates gives a `timedelta`, and its `.days` is the gap. `.weekday()` gives 0 for Monday through 6 for Sunday.

## Your task

Write `working_days(start_iso, end_iso)` that counts the weekdays (Monday to Friday) from the start date up to **and including** the end date. Both come in as `"YYYY-MM-DD"` text.

1 October 2026 is a Thursday, so `working_days("2026-10-01", "2026-10-07")` is 5 (Thu, Fri, Mon, Tue, Wed).
""",
        "starter": "from datetime import date, timedelta\n\n\ndef working_days(start_iso, end_iso):\n    day = date.fromisoformat(start_iso)\n    end = date.fromisoformat(end_iso)\n    count = 0\n    # loop while day hasn't gone past end:\n    #     if day is Monday to Friday (weekday() below 5), add 1 to count\n    #     move day on by one (timedelta(days=1))\n    return count\n\n\nprint(working_days(\"2026-10-01\", \"2026-10-07\"))   # should print 5\n",
        "tests": '''
def test_values():
    "Counts weekdays inclusively"
    f = need("working_days")
    cases = [(("2026-10-01", "2026-10-07"), 5), (("2026-10-03", "2026-10-04"), 0),
             (("2026-10-05", "2026-10-05"), 1), (("2026-10-01", "2026-10-31"), 22),
             (("2026-12-28", "2027-01-08"), 10)]
    for args, want in cases:
        v, _ = capture(f, *args)
        check(v == want, "working_days%r returned %r, expected %d." % (args, v, want))
''',
        "solution": "from datetime import date, timedelta\n\n\ndef working_days(start_iso, end_iso):\n    day = date.fromisoformat(start_iso)\n    end = date.fromisoformat(end_iso)\n    count = 0\n    while day <= end:\n        if day.weekday() < 5:\n            count += 1\n        day += timedelta(days=1)\n    return count\n",
        "hints": [
            "Turn both strings into dates with `date.fromisoformat()`.",
            "Loop `while day <= end`, counting days where `day.weekday() < 5`, and step forward with `day += timedelta(days=1)`.",
        ],
    },
    {
        "id": "files",
        "title": "Writing and reading files",
        "kind": "code",
        "body": """
`open()` gives you a file to read or write. The safe way to use it is with a `with` block, which closes the file for you when the block ends, even if something goes wrong:

```python
with open("notes.txt", "w") as f:     # "w" = write (replaces the file)
    f.write("first line\\n")
    f.write("second line\\n")

with open("notes.txt") as f:          # reading is the default
    for line in f:
        print(line.strip())
```

| Mode | Means |
|---|---|
| `"r"` | read (the default) |
| `"w"` | write, wiping whatever was there |
| `"a"` | append to the end |

`write()` doesn't add a new line for you. You have to put `\\n` on the end yourself. When reading, each line comes back with its `\\n` still attached, which is why `.strip()` is so common.

Exercises here run inside the app's `data/sandbox` folder, so any files you make end up there.

## Your task

1. Write `save_list(path, items)` that writes each item in the list on its own line.
2. Write `load_list(path)` that reads the file back and returns a list of the lines, without the `\\n` characters, skipping any blank lines.

The checks will save a list and load it back to make sure you get the same thing.
""",
        "starter": "def save_list(path, items):\n    with open(path, \"w\") as f:\n        # write each item followed by \"\\n\"\n        pass\n\n\ndef load_list(path):\n    result = []\n    # open the file, go through its lines, strip each one,\n    # and append the ones that aren't blank\n    return result\n\n\nsave_list(\"shopping.txt\", [\"milk\", \"tea\", \"dates\"])\nprint(load_list(\"shopping.txt\"))\n",
        "tests": '''
import os

def test_round_trip():
    "Saving then loading gives the same list back"
    items = ["rebar", "cement", "sand and gravel"]
    need("save_list")("ks_test_items.txt", items)
    got = need("load_list")("ks_test_items.txt")
    check(got == items, "Saved %r but loaded %r." % (items, got))

def test_file_format():
    "Each item is on its own line in the file"
    need("save_list")("ks_test_items2.txt", ["a", "b"])
    with open("ks_test_items2.txt") as f:
        text = f.read()
    check(text.splitlines() == ["a", "b"], "The file contained %r. Put a newline after each item." % text)

def test_blank_lines():
    "load_list skips blank lines"
    with open("ks_test_items3.txt", "w") as f:
        f.write("x\\n\\ny\\n   \\n")
    try:
        got = need("load_list")("ks_test_items3.txt")
        check(got == ["x", "y"], "load_list returned %r, expected ['x', 'y']." % (got,))
    finally:
        for n in ("", "2", "3"):
            try:
                os.remove("ks_test_items%s.txt" % n)
            except OSError:
                pass
''',
        "solution": 'def save_list(path, items):\n    with open(path, "w") as f:\n        for item in items:\n            f.write(item + "\\n")\n\n\ndef load_list(path):\n    result = []\n    with open(path) as f:\n        for line in f:\n            line = line.strip()\n            if line:\n                result.append(line)\n    return result\n\n\nsave_list("shopping.txt", ["milk", "tea", "dates"])\nprint(load_list("shopping.txt"))\n',
        "hints": [
            'For saving: `with open(path, "w") as f:` then loop and `f.write(item + "\\n")`.',
            "For loading: loop over the file, `.strip()` each line, and only append the ones that aren't empty.",
        ],
    },
    {
        "id": "with-quiz",
        "title": "Why use with?",
        "kind": "quiz",
        "body": "One quick question to close the chapter.",
        "question": "What's the main reason to open files with a `with` block?",
        "options": [
            "It makes reading faster",
            "It closes the file automatically, even if an error happens",
            "It's the only way to write to a file",
            "It stops other programs from deleting the file",
        ],
        "answer": 1,
        "explain": "When the `with` block ends, for any reason, the file is closed. Without it you'd have to remember to call `f.close()` yourself, and an error halfway through could leave the file open with some of your writes not saved.",
    },
]
