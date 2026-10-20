CHAPTER = {
    "title": "Making decisions",
    "summary": "Comparisons, booleans, if / elif / else, returning early, and combining conditions.",
}

LESSONS = [
    {
        "id": "comparisons",
        "title": "Comparisons",
        "kind": "quiz",
        "body": """
Comparisons ask a yes-or-no question and give back a `bool`, either `True` or `False`.

| Operator | Means |
|---|---|
| `==` | equal to |
| `!=` | not equal to |
| `<` `>` | less than, greater than |
| `<=` `>=` | less than or equal, greater than or equal |

Watch the difference between `=` and `==`. One `=` stores a value. Two `==` compares.

```python
print(5 > 3)       # True
print(5 == 5.0)    # True, an int and a float can be equal
print("a" == "A")  # False, case matters
```
""",
        "question": "What does `print(10 == \"10\")` show?",
        "options": ["`True`", "`False`", "A `TypeError`", "`10`"],
        "answer": 1,
        "explain": "One is a number and the other is text, so they're never equal. Python doesn't raise an error for `==` between different types, it just says `False`. (It *would* raise an error for `10 < \"10\"`, because there's no sensible order between a number and text.)",
    },
    {
        "id": "if-top",
        "title": "if and else",
        "kind": "code",
        "body": """
`if` runs a block only when a condition is `True`. `else` catches everything else.

```python
wind_kmh = 55

if wind_kmh > 50:
    print("Stop crane work")
else:
    print("Crane can operate")
```

Same rules as functions: a colon at the end of the `if` and `else` lines, and the lines that belong to each branch are indented under it. `else` lines up with its `if`, never further in.

> **Common slips:** `if wind_kmh = 50:` uses one `=`, which stores a value, so Python gives a `SyntaxError`. Comparisons need `==`. And forgetting the colon after `else` is just as easy as forgetting it after `if`.

## Your task

The starter sets `temperature` to 38. Write an `if` / `else` that prints `Stop work for a break` when the temperature is **above** 35, and `Carry on` otherwise.

The checks will also try your code with other temperatures, so don't just print the first line.
""",
        "starter": "temperature = 38\n\n# if temperature is above 35, print: Stop work for a break\n# otherwise, print: Carry on\n",
        "tests": '''
import re, io, contextlib

def run_with(t):
    src = re.sub(r"^temperature\\s*=.*$", "temperature = %r" % t, RAW_CODE, count=1, flags=re.M)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, "<your code>", "exec"), {"__name__": "__main__"})
    return buf.getvalue().strip()

def test_hot():
    "38 degrees prints Stop work for a break"
    check(LINES == ["Stop work for a break"], "With temperature = 38 your code printed:\\n%s" % OUTPUT)

def test_other_values():
    "Works for other temperatures, including exactly 35"
    for t, want in [(20, "Carry on"), (35, "Carry on"), (35.5, "Stop work for a break")]:
        got = run_with(t)
        check(got == want, "With temperature = %r your code printed %r, expected %r." % (t, got, want))

def test_structure():
    "Uses if and else"
    import ast
    ifs = [n for n in ast.walk(ast.parse(RAW_CODE)) if isinstance(n, ast.If)]
    check(ifs and any(n.orelse for n in ifs), "Use an if with an else branch.")
''',
        "solution": 'temperature = 38\n\nif temperature > 35:\n    print("Stop work for a break")\nelse:\n    print("Carry on")\n',
        "hints": [
            "`if temperature > 35:` then an indented `print(...)`. Then `else:` lined up with the `if`.",
            'Four lines: `if temperature > 35:`, an indented `print("Stop work for a break")`, then `else:` at the left edge, and an indented `print("Carry on")`.',
        ],
    },
    {
        "id": "if-else",
        "title": "if and else inside a function",
        "kind": "code",
        "body": """
Same idea, now inside a function. Instead of printing, each branch can `return` its answer:

```python
def crane_status(wind_kmh):
    if wind_kmh > 50:
        return "stop"
    else:
        return "operate"
```

Look at the indentation. The `if` is one level in, because it belongs to the function. The `return` lines are two levels in, because they belong to the `if` and the `else`.

> **Common slips:** returning a word without quotes (`return pass` is an error, `return "pass"` returns the text), and putting `else:` at a different indentation from its `if`.

## Your task

Write `result(mark)` that returns `"pass"` when the mark is 40 or above, and `"fail"` otherwise. Be careful with exactly 40.
""",
        "starter": "def result(mark):\n    # if the mark is 40 or more, return \"pass\"\n    # otherwise, return \"fail\"\n    pass\n\n\nprint(result(40))   # should print pass\n",
        "tests": '''
def test_cases():
    "Returns pass for 40 and above, fail below"
    f = need("result")
    for m, want in [(0, "fail"), (39, "fail"), (39.5, "fail"), (40, "pass"), (41, "pass"), (100, "pass")]:
        v, _ = capture(f, m)
        check(v == want, "result(%r) returned %r, expected %r." % (m, v, want))
''',
        "solution": 'def result(mark):\n    if mark >= 40:\n        return "pass"\n    else:\n        return "fail"\n',
        "hints": [
            "`>=` means \"greater than or equal to\".",
            '`if mark >= 40:` then `return "pass"`, `else:` then `return "fail"`.',
        ],
    },
    {
        "id": "return-bool",
        "title": "Returning True or False",
        "kind": "code",
        "body": """
Lots of functions answer a yes-or-no question. Those should return a **bool**: `True` or `False`.

```python
def is_heavy(kg):
    if kg > 25:
        return True
    else:
        return False
```

That works, but there's a shorter way. `kg > 25` already *is* `True` or `False`, so you can return it directly:

```python
def is_heavy(kg):
    return kg > 25
```

Both versions behave the same. Use whichever you find clearer for now.

> **Common slips:**
> - `return true` gives a `NameError`. Python only knows `True` and `False` with a capital first letter.
> - `return "True"` (or `"True."`) returns a piece of text that happens to spell True. It isn't the bool, and checks that expect `True` will fail.
> - Printing `True` instead of returning it. The checks call your function and look at what comes back.

## Your task

Write `is_overloaded(load_kn, limit_kn)` that returns `True` when the load is **more than** the limit, and `False` otherwise. A load exactly at the limit is not overloaded.
""",
        "starter": "def is_overloaded(load_kn, limit_kn):\n    # return True if load_kn is more than limit_kn, otherwise False\n    pass\n\n\nprint(is_overloaded(120, 100))   # should print True\n",
        "tests": '''
def test_values():
    "True only when the load is over the limit"
    f = need("is_overloaded")
    for args, want in [((120, 100), True), ((100, 100), False), ((99.9, 100), False), ((0, 5), False), ((5.01, 5), True)]:
        v, _ = capture(f, *args)
        check(v is want, "is_overloaded%r returned %r, expected %r." % (args, v, want))
''',
        "solution": "def is_overloaded(load_kn, limit_kn):\n    return load_kn > limit_kn\n\n\nprint(is_overloaded(120, 100))\n",
        "hints": [
            "Compare the two numbers with `>`. Exactly equal shouldn't count.",
            "`return load_kn > limit_kn`",
        ],
    },
    {
        "id": "bool-quiz",
        "title": "Which one is a bool?",
        "kind": "quiz",
        "body": "A quick check on the slips from the last lesson.",
        "question": "A check expects your function to return the bool `True`. Which `return` line does that?",
        "options": ['`return "True"`', "`return true`", "`return True`", '`return "True."`'],
        "answer": 2,
        "explain": "Only `True`, with a capital T and no quotes, is the bool. The two with quotes are strings that happen to spell the word, and `true` in lowercase isn't a name Python knows, so it raises a `NameError`.",
    },
    {
        "id": "elif",
        "title": "elif",
        "kind": "code",
        "body": """
When there are more than two outcomes, chain them with `elif` ("else if"). Python checks each condition from the top and runs the **first** one that's true. The rest are skipped.

```python
def wind_action(kmh):
    if kmh >= 72:
        return "stop all lifting"
    elif kmh >= 50:
        return "stop crane work"
    elif kmh >= 38:
        return "secure loose materials"
    else:
        return "normal"
```

Because the checks run top to bottom, order matters. If the `>= 38` check came first, a 90 km/h wind would stop there and return the wrong answer.

## Your task

Write `grade(mark)` that returns a letter:

| Mark | Grade |
|---|---|
| 70 and above | `"A"` |
| 60 to 69 | `"B"` |
| 50 to 59 | `"C"` |
| 40 to 49 | `"D"` |
| below 40 | `"F"` |
""",
        "starter": "def grade(mark):\n    pass\n",
        "tests": '''
def test_bands():
    "Every band, including the boundaries"
    f = need("grade")
    cases = [(100, "A"), (70, "A"), (69, "B"), (60, "B"), (59.9, "C"), (50, "C"),
             (49, "D"), (40, "D"), (39, "F"), (0, "F")]
    for m, want in cases:
        v, _ = capture(f, m)
        check(v == want, "grade(%r) returned %r, expected %r." % (m, v, want))
''',
        "solution": 'def grade(mark):\n    if mark >= 70:\n        return "A"\n    elif mark >= 60:\n        return "B"\n    elif mark >= 50:\n        return "C"\n    elif mark >= 40:\n        return "D"\n    else:\n        return "F"\n',
        "hints": [
            "Start with the highest band and work down, the same way `wind_action` does. Each check only needs a single `>=`.",
            "`if mark >= 70: ... elif mark >= 60: ... elif mark >= 50: ...` and so on.",
        ],
    },
    {
        "id": "elif-order",
        "title": "Order matters",
        "kind": "quiz",
        "body": "Python stops at the first branch that's true. Trace this one line by line.",
        "question": "What does this print?\n\n```python\ndef size(n):\n    if n > 10:\n        return \"big\"\n    elif n > 100:\n        return \"huge\"\n    else:\n        return \"small\"\n\nprint(size(500))\n```",
        "options": ["`huge`", "`big`", "`small`", "`big` then `huge`"],
        "answer": 1,
        "explain": "500 is more than 10, so the first branch runs and returns `\"big\"`. The `elif` is never even looked at. For `\"huge\"` to be reachable, the `n > 100` check has to come first.",
    },
    {
        "id": "and-or-not",
        "title": "and, or, not",
        "kind": "code",
        "body": """
You can combine conditions:

- `a and b` is true only when **both** are true.
- `a or b` is true when **at least one** is true.
- `not a` flips true to false and false to true.

```python
if has_ticket and not banned:
    print("Come in")
```

For a range check Python lets you chain comparisons, which reads nicely:

```python
if 18 <= age <= 65:
    ...
```

## Your task

Concrete can be poured when the air temperature is between 5 and 32 degrees (both included) **and** it isn't raining.

Write `can_pour(temp_c, raining)` that returns `True` or `False`. `raining` will be a bool.
""",
        "starter": "def can_pour(temp_c, raining):\n    pass\n",
        "tests": '''
def test_cases():
    "Right answer across temperatures and weather"
    f = need("can_pour")
    cases = [((20, False), True), ((5, False), True), ((32, False), True),
             ((4.9, False), False), ((33, False), False), ((20, True), False),
             ((-3, True), False)]
    for args, want in cases:
        v, _ = capture(f, *args)
        check(v is want, "can_pour%r returned %r, expected %r." % (args, v, want))
''',
        "solution": "def can_pour(temp_c, raining):\n    return 5 <= temp_c <= 32 and not raining\n",
        "hints": [
            "You can return a condition directly: `return <condition>` gives back True or False.",
            "`5 <= temp_c <= 32 and not raining`",
        ],
    },
    {
        "id": "truthy",
        "title": "Truthy and falsy",
        "kind": "quiz",
        "body": """
`if` doesn't strictly need a bool. Python will treat any value as true or false:

- **Falsy:** `False`, `None`, `0`, `0.0`, empty text `""`, and empty collections like `[]` and `{}` (coming up in later chapters).
- **Truthy:** everything else.

So `if name:` is a short way of saying "if name isn't empty".
""",
        "question": "Which of these values is **falsy**?",
        "options": ['`"0"`', '`" "`', '`""`', "`-1`"],
        "answer": 2,
        "explain": '`""` is an empty string, so it\'s falsy. `"0"` and `" "` both contain a character, so they\'re truthy, even though they look empty-ish. Any non-zero number, including `-1`, is truthy.',
    },
    {
        "id": "early-return",
        "title": "Returning early",
        "kind": "code",
        "body": """
`return` ends a function on the spot. That means you don't always need `elif` and `else`. A row of plain `if` checks, each with its own `return`, does the same job:

```python
def ticket_price(age):
    if age < 5:
        return 0       # under 5s go free, and the function stops here
    if age >= 65:
        return 4       # only reached if the first check was False
    return 8           # everyone else
```

Read it from the top. As soon as one `if` matches, its `return` hands back the answer and nothing below it runs. If none match, Python reaches the last line, which is the "everyone else" answer. That last `return` sits at the function's own indentation, not inside any `if`.

This style is handy when a function has special cases to get out of the way first. You'll use exactly this shape for leap years next, and again in the Loops chapter.

## Your task

Write `shipping_cost(weight_kg)` using separate `if` checks that each return, plus a final `return` at the bottom. No `elif` or `else` this time.

| Weight | Cost |
|---|---|
| 0 or less | `0` (nothing to ship) |
| up to and including 2 kg | `5` |
| up to and including 10 kg | `12` |
| anything heavier | `25` |
""",
        "starter": "def shipping_cost(weight_kg):\n    pass\n",
        "tests": '''
def test_values():
    "Right cost for every band, including the edges"
    f = need("shipping_cost")
    for w, want in [(-1, 0), (0, 0), (0.5, 5), (2, 5), (2.1, 12), (10, 12), (10.5, 25), (500, 25)]:
        v, _ = capture(f, w)
        check(v == want, "shipping_cost(%r) returned %r, expected %r." % (w, v, want))

def test_style():
    "Uses separate ifs that return, without elif or else"
    check("elif" not in CODE and "else" not in CODE,
          "Try it with plain if checks that each return, and one last return at the bottom for the heaviest band.")
''',
        "solution": "def shipping_cost(weight_kg):\n    if weight_kg <= 0:\n        return 0\n    if weight_kg <= 2:\n        return 5\n    if weight_kg <= 10:\n        return 12\n    return 25\n",
        "hints": [
            "Start with the lightest case: `if weight_kg <= 0: return 0`. Each later check only runs if the ones above didn't return.",
            "Then `if weight_kg <= 2:` and `if weight_kg <= 10:`, and finally `return 25` lined up with the `if` lines.",
        ],
    },
    {
        "id": "leap-year",
        "title": "Leap years",
        "kind": "code",
        "body": """
Time to combine everything. The leap year rule has a catch inside a catch:

1. A year divisible by 4 is a leap year,
2. **except** years divisible by 100, which aren't,
3. **except** years divisible by 400, which are.

So 2024 is a leap year, 1900 isn't, and 2000 is.

"Divisible by" means the remainder is zero, which is the `%` operator: `year % 4 == 0`.

## Your task

Write `is_leap(year)` that returns `True` or `False`.

It's the same shape as `shipping_cost`: a few `if` checks that return early, then one last `return`. Check the most specific rule (400) first, then 100, and whatever is left depends only on 4.

> **Common slip:** checking 4 first. 1900 is divisible by 4, so it would return `True` before the 100 rule ever gets a look in.
""",
        "starter": "def is_leap(year):\n    # 1. divisible by 400? then it's a leap year\n    # 2. divisible by 100? then it isn't\n    # 3. otherwise it depends on 4\n    pass\n",
        "tests": '''
def test_cases():
    "Correct for ordinary, century and 400-year cases"
    f = need("is_leap")
    cases = {2024: True, 2023: False, 1900: False, 2000: True, 2100: False,
             2400: True, 1996: True, 1: False, 4: True}
    for y, want in cases.items():
        v, _ = capture(f, y)
        check(v is want, "is_leap(%d) returned %r, expected %r." % (y, v, want))
''',
        "solution": "def is_leap(year):\n    if year % 400 == 0:\n        return True\n    if year % 100 == 0:\n        return False\n    return year % 4 == 0\n",
        "hints": [
            "Check 400 first and return True. Then check 100 and return False. Whatever's left depends only on 4.",
            "The last line can be `return year % 4 == 0`, which gives True or False directly.",
        ],
    },
]
