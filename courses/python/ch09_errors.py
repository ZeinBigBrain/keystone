CHAPTER = {
    "title": "Errors and debugging",
    "summary": "Reading tracebacks, catching exceptions, raising your own, and hunting bugs.",
}

LESSONS = [
    {
        "id": "tracebacks",
        "title": "Reading an error",
        "kind": "read",
        "body": """
Errors aren't failures, they're Python telling you exactly what went wrong and where. The trick is to read them from the **bottom up**.

```
Traceback (most recent call last):
  File "report.py", line 9, in <module>
    print(average(scores))
  File "report.py", line 4, in average
    return total / len(numbers)
ZeroDivisionError: division by zero
```

1. **Last line:** the type of error and a short message. Here, a division by zero.
2. **Lines above it:** the chain of calls that led there, with the most recent at the bottom. The crash happened on line 4, inside `average`, which was called from line 9.

The ones you'll meet most:

| Error | Usually means |
|---|---|
| `SyntaxError` | the code isn't valid Python (missing bracket, colon, quote) |
| `IndentationError` | indentation doesn't line up |
| `NameError` | a name that doesn't exist (often a typo) |
| `TypeError` | the wrong type for an operation, like `"5" + 5` |
| `ValueError` | right type, bad value, like `int("abc")` |
| `IndexError` | list index past the end |
| `KeyError` | dict key that isn't there |
| `ZeroDivisionError` | dividing by zero |
| `AttributeError` | a method or attribute the object doesn't have, like `[1].upper()` |

> A tip that saves a lot of time: when the error points at a line that looks fine, check the line **above** it. A missing closing bracket often only gets noticed on the next line.
""",
    },
    {
        "id": "which-error",
        "title": "Name that error",
        "kind": "quiz",
        "body": "Use the table from the last lesson if you need it.",
        "question": "Which error does `int(\"12.5\")` raise?",
        "options": ["`TypeError`", "`ValueError`", "`SyntaxError`", "None, it returns `12`"],
        "answer": 1,
        "explain": "`int()` happily accepts a string, so the type is fine. The problem is the value: `\"12.5\"` isn't a whole number, so you get `ValueError: invalid literal for int() with base 10`. `int(float(\"12.5\"))` would work and give `12`.",
    },
    {
        "id": "try-except",
        "title": "try and except",
        "kind": "code",
        "body": """
When you know something might fail, you can catch the error instead of letting the program crash:

```python
try:
    result = 10 / count
except ZeroDivisionError:
    result = 0
```

Python runs the `try` block. If the named error happens inside it, Python jumps to the matching `except` block instead of crashing. If nothing goes wrong, the `except` block is skipped.

Always name the error you're expecting. A bare `except:` catches **everything**, including typos in your own code, which hides bugs.

You can catch several types at once with a tuple: `except (ValueError, TypeError):`.

## Your task

Write `parse_number(text)` that turns text into a float. If the text isn't a valid number, return `None` instead of crashing.

`parse_number("3.5")` gives `3.5`, `parse_number(" 7 ")` gives `7.0`, and `parse_number("seven")` gives `None`.
""",
        "starter": "def parse_number(text):\n    return float(text)\n",
        "tests": '''
def test_good():
    "Converts valid numbers"
    f = need("parse_number")
    for t, want in [("3.5", 3.5), (" 7 ", 7.0), ("-2", -2.0), ("1e3", 1000.0)]:
        v, _ = capture(f, t)
        check(v == want, "parse_number(%r) returned %r, expected %r." % (t, v, want))

def test_bad():
    "Returns None for text that isn't a number"
    f = need("parse_number")
    for t in ["seven", "", "3,5", "12 kg"]:
        try:
            v, _ = capture(f, t)
        except ValueError:
            check(False, "parse_number(%r) crashed with ValueError. Catch it with try/except." % t)
        check(v is None, "parse_number(%r) returned %r, expected None." % (t, v))

def test_specific():
    "Catches ValueError specifically, not everything"
    check("except ValueError" in CODE or "except (ValueError" in CODE,
          "Name the error you're catching: except ValueError:")
''',
        "solution": "def parse_number(text):\n    try:\n        return float(text)\n    except ValueError:\n        return None\n",
        "hints": [
            "Put the `return float(text)` inside a `try:` block.",
            "Add `except ValueError:` with `return None` under it.",
        ],
    },
    {
        "id": "raise",
        "title": "Raising your own errors",
        "kind": "code",
        "body": """
Your own functions can raise errors too. It's the right move when a function is given something it can't sensibly deal with:

```python
def set_age(age):
    if age < 0:
        raise ValueError("age can't be negative")
    return age
```

Raising early, with a clear message, is far better than quietly carrying on with a bad value and getting a confusing result three functions later.

## Your task

Write `safe_load(load_kn, limit_kn)` that checks a load against a limit:

- if `load_kn` is negative, raise a `ValueError` (any message)
- if `load_kn` is greater than `limit_kn`, raise a `ValueError` with a message that includes both numbers, like `"load 120 kN exceeds limit 100 kN"`
- otherwise, return the **utilisation** as `load_kn / limit_kn`
""",
        "starter": "def safe_load(load_kn, limit_kn):\n    pass\n",
        "tests": '''
def raises(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return str(e)
    return None

def test_ok():
    "Returns the utilisation for safe loads"
    f = need("safe_load")
    for args, want in [((50, 100), 0.5), ((100, 100), 1.0), ((0, 80), 0.0)]:
        v, _ = capture(f, *args)
        check(v is not None and abs(v - want) < 1e-9, "safe_load%r returned %r, expected %r." % (args, v, want))

def test_negative():
    "Raises ValueError for a negative load"
    check(raises(need("safe_load"), -5, 100) is not None, "safe_load(-5, 100) should raise ValueError.")

def test_over():
    "Raises ValueError mentioning both numbers when over the limit"
    msg = raises(need("safe_load"), 120, 100)
    check(msg is not None, "safe_load(120, 100) should raise ValueError.")
    check("120" in msg and "100" in msg, "The message should include both numbers. It was: %r" % msg)
''',
        "solution": 'def safe_load(load_kn, limit_kn):\n    if load_kn < 0:\n        raise ValueError("load can\'t be negative")\n    if load_kn > limit_kn:\n        raise ValueError(f"load {load_kn} kN exceeds limit {limit_kn} kN")\n    return load_kn / limit_kn\n',
        "hints": [
            "Two `if` checks, each with `raise ValueError(...)`, then the `return` at the end.",
            'Use an f-string for the second message: `f"load {load_kn} kN exceeds limit {limit_kn} kN"`.',
        ],
    },
    {
        "id": "debugging",
        "title": "Bug hunt",
        "kind": "code",
        "body": """
Not every bug causes an error. The nastiest ones run fine and give the wrong answer.

When something gives the wrong result:

1. Pick a small input where you know the right answer.
2. Add `print()` lines to see what values your variables actually have along the way.
3. Find the first point where what you see differs from what you expected. The bug is just before it.

That's what the **Run** button is for. Use it a lot here.

## Your task

This function should return the average of the passing marks only (40 and above), rounded to 1 decimal place, or `0` if nobody passed. It runs without crashing, but it has **three** bugs.

For `[35, 40, 80, 90]` the answer should be `70.0`.
""",
        "starter": "def pass_average(marks):\n    total = 0\n    count = 0\n    for m in marks:\n        if m > 40:\n            total += m\n        count += 1\n    if count == 0:\n        return 0\n    return round(total / len(marks), 1)\n\n\nprint(pass_average([35, 40, 80, 90]))\n",
        "tests": '''
def test_example():
    "pass_average([35, 40, 80, 90]) is 70.0"
    v, _ = capture(need("pass_average"), [35, 40, 80, 90])
    check(v == 70.0, "Got %r." % (v,))

def test_more():
    "Works on other inputs"
    f = need("pass_average")
    for data, want in [([10, 20], 0), ([], 0), ([41, 42], 41.5), ([40], 40.0), ([39, 55, 61, 77], 64.3)]:
        v, _ = capture(f, data)
        check(v == want, "pass_average(%r) returned %r, expected %r." % (data, v, want))
''',
        "solution": "def pass_average(marks):\n    total = 0\n    count = 0\n    for m in marks:\n        if m >= 40:\n            total += m\n            count += 1\n    if count == 0:\n        return 0\n    return round(total / count, 1)\n\n\nprint(pass_average([35, 40, 80, 90]))\n",
        "hints": [
            "Is a mark of exactly 40 a pass? Look at the comparison.",
            "Look at the indentation of `count += 1`. Which marks is it counting?",
            "What should the total be divided by: every mark, or only the passing ones?",
        ],
    },
]
