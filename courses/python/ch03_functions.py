CHAPTER = {
    "title": "Functions",
    "summary": "Packaging code so you can reuse it: parameters, return values, defaults and scope.",
}

LESSONS = [
    {
        "id": "def",
        "title": "Your first function",
        "kind": "code",
        "body": """
A **function** is a named block of code you can run whenever you like. You've already used some that come with Python, like `print()` and `type()`. Now you'll write your own.

```python
def say_hi():
    print("Hi there")

say_hi()
say_hi()
```

- `def` starts the definition, then the name, brackets and a colon.
- The body is **indented** by four spaces. Indentation is how Python knows which lines belong to the function. Get it wrong and you'll see an `IndentationError`.
- Defining a function doesn't run it. The two `say_hi()` lines at the bottom are what actually run it, twice.

The editor indents for you after a line ending in `:`. Press `Backspace` to step back out.

> **Common slips:** forgetting the colon after `def print_banner()`, forgetting the brackets when you call it (`print_banner` on its own does nothing), and indenting the call so it ends up inside the function. The call goes at the left edge, under the function.

## Your task

Define a function called `print_banner` that prints these three lines:

```
==========
 DAILY LOG
==========
```

Then call it once. (There's a space before `DAILY`.)
""",
        "starter": "# define print_banner here\n\n\n# then call it\n",
        "tests": '''
BANNER = ["==========", " DAILY LOG", "=========="]

def test_defined():
    "print_banner is a function"
    f = need("print_banner")
    check(callable(f), "print_banner should be a function, defined with def.")

def test_prints():
    "Calling it prints the banner"
    _, out = capture(need("print_banner"))
    lines = out.rstrip("\\n").split("\\n")
    check(lines == BANNER, "print_banner() printed:\\n%s\\nExpected:\\n%s" % (out, "\\n".join(BANNER)))

def test_called():
    "You called it once"
    check(LINES == BANNER, "Your program should print the banner exactly once. It printed:\\n" + OUTPUT)
''',
        "solution": 'def print_banner():\n    print("==========")\n    print(" DAILY LOG")\n    print("==========")\n\n\nprint_banner()\n',
        "hints": [
            "Start with `def print_banner():` and indent the three print lines under it.",
            "After the function, on a line with no indentation, write `print_banner()`.",
        ],
    },
    {
        "id": "parameters",
        "title": "Parameters",
        "kind": "code",
        "body": """
Functions get much more useful when you can hand them information. The names in the brackets are **parameters**:

```python
def order_line(qty, item):
    print(f"{qty} x {item}")

order_line(3, "hard hats")    # 3 x hard hats
order_line(10, "gloves")      # 10 x gloves
```

When you call `order_line(3, "hard hats")`, Python sets `qty = 3` and `item = "hard hats"` for that run of the function. The values you pass in are called **arguments**. They're matched to parameters by position: first to first, second to second.

## Your task

Write a function `label(code, floor)` that prints a line like this:

```
Room B12 (floor 2)
```

for `label("B12", 2)`. Call it however you like to test it. The checks will call it with their own values.
""",
        "starter": "def label(code, floor):\n    pass  # replace this line\n",
        "tests": '''
def test_b12():
    "label('B12', 2) prints Room B12 (floor 2)"
    _, out = capture(need("label"), "B12", 2)
    check(out.strip() == "Room B12 (floor 2)", "Got %r" % out.strip())

def test_other():
    "Works for other rooms too"
    _, out = capture(need("label"), "G01", 0)
    check(out.strip() == "Room G01 (floor 0)", "label('G01', 0) printed %r" % out.strip())
''',
        "solution": 'def label(code, floor):\n    print(f"Room {code} (floor {floor})")\n\n\nlabel("B12", 2)\n',
        "hints": [
            "`pass` means \"do nothing\". Replace it with a `print()` that uses `code` and `floor`.",
            '`print(f"Room {code} (floor {floor})")`',
        ],
    },
    {
        "id": "return",
        "title": "Returning a value",
        "kind": "code",
        "body": """
Printing shows a value on the screen, but the rest of your program can't use it. To hand a value **back** to whoever called the function, use `return`:

```python
def double(n):
    return n * 2

x = double(21)
print(x + 1)    # 43
```

`double(21)` is replaced by whatever the function returns, so `x` becomes `42`.

`return` also ends the function immediately. Any lines after it in the same block never run.

Most functions you write should return rather than print. A function that returns a number can be used in a sum, saved, compared or printed. One that only prints can only print.

> **Common slips:**
> - No `return` at all. The function then hands back `None`, and you'll see `None` where you expected a number.
> - `print(...)` instead of `return ...`. The value shows on screen, but whoever called the function gets `None`.
> - `return` indented wrongly. It must sit inside the function, lined up with the other lines in the body.

## Your task

Write `circle_area(radius)` that returns the area of a circle (pi times radius squared). Use the `PI` variable given. Don't print inside the function.
""",
        "starter": "PI = 3.14159\n\ndef circle_area(radius):\n    pass\n\n\nprint(circle_area(2))\n",
        "tests": '''
def test_two():
    "circle_area(2) returns about 12.566"
    v, _ = capture(need("circle_area"), 2)
    check(v is not None, "circle_area returned None. Did you use return?")
    check(abs(v - 12.56636) < 1e-6, "circle_area(2) returned %r, expected about 12.566." % v)

def test_other():
    "Works for other radii"
    v, _ = capture(need("circle_area"), 0.5)
    check(v is not None and abs(v - 0.7853975) < 1e-6, "circle_area(0.5) returned %r." % v)

def test_no_print():
    "Doesn't print inside the function"
    _, out = capture(need("circle_area"), 3)
    check(out == "", "circle_area printed something. Return the value instead.")
''',
        "solution": "PI = 3.14159\n\ndef circle_area(radius):\n    return PI * radius ** 2\n\n\nprint(circle_area(2))\n",
        "hints": [
            "Squared is `** 2`.",
            "`return PI * radius ** 2`",
        ],
    },
    {
        "id": "print-vs-return",
        "title": "Print or return?",
        "kind": "quiz",
        "body": "This trips up almost everyone at some point, so it's worth a question of its own.",
        "question": "What does this print?\n\n```python\ndef add(a, b):\n    print(a + b)\n\nresult = add(2, 3)\nprint(result)\n```",
        "options": ["`5` then `5`", "`5` then `None`", "`None` then `5`", "Just `5`"],
        "answer": 1,
        "explain": "Calling `add(2, 3)` runs its `print`, which shows `5`. But the function has no `return`, so it hands back `None`, and that's what `result` holds. Changing `print(a + b)` to `return a + b` would fix it.",
    },
    {
        "id": "using-results",
        "title": "Using what a function returns",
        "kind": "code",
        "body": """
Writing a function is half the job. The other half is calling it and doing something with the answer.

```python
def double(n):
    return n * 2

a = double(5)        # call it, keep the answer in a
b = double(8)
print(a + b)         # 26
print(double(3))     # call it straight inside print: 6
```

Two things to notice:

1. The function name is followed by brackets holding the values you're passing in. `double(5)` runs the function. `double` on its own doesn't.
2. Python works out `double(5)` first, then uses the answer wherever the call was written. So you can store it, add it, or put it straight inside `print()`.

> **Common slip:** `print(5)` or `print(100, 0.15)` prints the numbers you typed, not the function's answer. To print the answer, the function call itself has to go inside the brackets: `print(double(5))`.

## Your task

`beam_load(span, kn_per_m)` is already written for you. It returns the total load on a beam in kN.

1. Call `beam_load(6, 12.5)` and store the answer in a variable called `load_a`.
2. Call `beam_load(4, 20)` and store the answer in `load_b`.
3. Print the two loads added together.
4. Print the line `Beam A carries 75.0 kN`, using `load_a` inside an f-string rather than typing 75.0.
""",
        "starter": "def beam_load(span, kn_per_m):\n    return span * kn_per_m\n\n\n# 1. load_a = ...\n\n# 2. load_b = ...\n\n# 3. print the total of the two\n\n# 4. print the sentence about beam A\n",
        "tests": '''
def test_vars():
    "load_a and load_b hold the two answers"
    check(need("load_a") == 75, "load_a should be 75.0, the answer from beam_load(6, 12.5). It's %r." % ns.get("load_a"))
    check(need("load_b") == 80, "load_b should be 80, the answer from beam_load(4, 20). It's %r." % ns.get("load_b"))

def test_called():
    "Both come from calling beam_load"
    body = CODE.split("return span * kn_per_m", 1)[-1]
    check(body.count("beam_load(") >= 2, "Get each load by calling beam_load(...) with the numbers, not by working it out yourself.")

def test_output():
    "Prints the total, then the sentence"
    want = ["155.0", "Beam A carries 75.0 kN"]
    check(LINES == want, "Expected these two lines:\\n%s\\nYour code printed:\\n%s" % ("\\n".join(want), OUTPUT))
    check("75.0" not in CODE and "155" not in CODE, "Let Python fill in the numbers. Use load_a and load_b rather than typing them.")
''',
        "solution": 'def beam_load(span, kn_per_m):\n    return span * kn_per_m\n\n\nload_a = beam_load(6, 12.5)\nload_b = beam_load(4, 20)\nprint(load_a + load_b)\nprint(f"Beam A carries {load_a} kN")\n',
        "hints": [
            "Step 1 looks like `load_a = beam_load(6, 12.5)`. The function's answer lands in the variable.",
            '`print(load_a + load_b)`, then `print(f"Beam A carries {load_a} kN")`.',
        ],
    },
    {
        "id": "predict-calls",
        "title": "Predict the output",
        "kind": "quiz",
        "body": "Work it out on paper before you pick. Python runs the innermost call first.",
        "question": "What does this print?\n\n```python\ndef triple(n):\n    return n * 3\n\nprint(triple(2), 2)\nprint(triple(triple(1)))\n```",
        "options": ["`6 2` then `9`", "`6` then `9`", "`2 2` then `3`", "`6 2` then `3`"],
        "answer": 0,
        "explain": "The first line prints two things: the answer from `triple(2)`, which is `6`, and then the plain number `2`. On the second line, the inner `triple(1)` gives `3`, then `triple(3)` gives `9`.",
    },
    {
        "id": "defaults",
        "title": "Default values",
        "kind": "code",
        "body": """
A parameter can have a **default**, used whenever the caller leaves it out:

```python
def brew(cups, sugar=0):
    return f"{cups} cups, {sugar} sugar"

print(brew(2))       # 2 cups, 0 sugar
print(brew(2, 1))    # 2 cups, 1 sugar
print(brew(2, sugar=3))   # 2 cups, 3 sugar
```

The last line passes `sugar` **by name**. Named arguments are easier to read when a function takes several values.

Parameters with defaults have to come after the ones without.

> **Common slip:** to try your function, call it inside `print`: `print(with_vat(100, 0.2))`. Writing `print(100, 0.2)` just prints the two numbers and never runs your function.

## Your task

Write `with_vat(price, rate=0.15)` that returns the price including VAT. So `with_vat(100)` returns `115.0` and `with_vat(100, 0.2)` returns `120.0`.
""",
        "starter": "def with_vat(price, rate):\n    pass\n",
        "tests": '''
def close(a, b):
    return a is not None and abs(a - b) < 1e-9

def test_default():
    "with_vat(100) gives 115"
    v, _ = capture(need("with_vat"), 100)
    check(close(v, 115), "with_vat(100) returned %r." % v)

def test_rate():
    "with_vat(100, 0.2) gives 120"
    v, _ = capture(need("with_vat"), 100, 0.2)
    check(close(v, 120), "with_vat(100, 0.2) returned %r." % v)

def test_named():
    "with_vat(80, rate=0.05) gives 84"
    v, _ = capture(need("with_vat"), 80, rate=0.05)
    check(close(v, 84), "with_vat(80, rate=0.05) returned %r." % v)
''',
        "solution": "def with_vat(price, rate=0.15):\n    return price * (1 + rate)\n",
        "hints": [
            "The default goes in the def line: `rate=0.15`.",
            "Price including VAT is `price * (1 + rate)`.",
        ],
    },
    {
        "id": "scope",
        "title": "Scope",
        "kind": "quiz",
        "body": """
Variables created inside a function are **local** to it. They exist while the function runs and disappear when it returns. Code outside the function can't see them.

```python
def make_total():
    total = 99
    return total

make_total()
```

After that runs, there's no `total` outside the function. If you want the value, catch what the function returns: `t = make_total()`.

Functions *can* read variables defined outside them (like `PI` earlier), but relying on that too much makes code hard to follow. Passing values in as parameters is usually clearer.

Reading is allowed. Changing is a different story. If a function tries to update an outside variable with something like `total += 1`, Python stops with an `UnboundLocalError`. The fix is to create the variable inside the function. You'll meet this one properly in the Loops chapter.
""",
        "question": "What happens when this runs?\n\n```python\ndef setup():\n    crew = 12\n\nsetup()\nprint(crew)\n```",
        "options": ["It prints `12`", "It prints `None`", "It raises a `NameError`", "It prints nothing"],
        "answer": 2,
        "explain": "`crew` only existed inside `setup()`. Outside, Python has never heard of it, so `print(crew)` raises `NameError: name 'crew' is not defined`.",
    },
    {
        "id": "composing",
        "title": "Functions that use functions",
        "kind": "code",
        "body": """
Small functions that each do one thing can be combined into bigger ones. That keeps every piece short enough to check by eye.

```python
def square(n):
    return n * n

def sum_of_squares(a, b):
    return square(a) + square(b)
```

## Your task

1. Write `c_to_f(c)` that converts Celsius to Fahrenheit: multiply by 9, divide by 5, add 32.
2. Write `describe(c)` that returns a string like `"20 C is 68.0 F"`. It must call `c_to_f` to do the conversion rather than repeating the formula.
""",
        "starter": "def c_to_f(c):\n    pass\n\n\ndef describe(c):\n    pass\n\n\nprint(describe(20))\n",
        "tests": '''
def test_convert():
    "c_to_f works (0 -> 32, 100 -> 212, -40 -> -40)"
    f = need("c_to_f")
    for c, want in [(0, 32), (100, 212), (-40, -40), (37, 98.6)]:
        v, _ = capture(f, c)
        check(v is not None and abs(v - want) < 1e-9, "c_to_f(%r) returned %r, expected %r." % (c, v, want))

def test_describe():
    "describe(20) returns '20 C is 68.0 F'"
    v, _ = capture(need("describe"), 20)
    check(v == "20 C is 68.0 F", "describe(20) returned %r." % (v,))

def test_reuses():
    "describe calls c_to_f"
    src = CODE.split("def describe", 1)[-1]
    check("c_to_f(" in src, "Call c_to_f inside describe instead of repeating the formula.")
''',
        "solution": 'def c_to_f(c):\n    return c * 9 / 5 + 32\n\n\ndef describe(c):\n    return f"{c} C is {c_to_f(c)} F"\n\n\nprint(describe(20))\n',
        "hints": [
            "`c_to_f` is one line: `return c * 9 / 5 + 32`.",
            '`describe` returns an f-string with `{c_to_f(c)}` in it.',
        ],
    },
    {
        "id": "functions-checklist",
        "title": "When a function misbehaves",
        "kind": "read",
        "body": """
A short checklist for when a function doesn't do what you expect. Nearly every beginner bug with functions is one of these.

| What you see | Usually means |
|---|---|
| `None` where you expected a value | There's no `return`, or you used `print` instead of `return`. |
| `'True.'` or `'12'` in quotes in a check message | You returned text instead of a bool or a number. Drop the quotes and the f-string: `return True`, `return total`. |
| `NameError: name 'true' is not defined` | `True`, `False` and `None` start with a capital letter. |
| Nothing happens at all | You defined the function but never called it, or forgot the brackets when you did. |
| Your function's answer isn't printed | You wrote `print(100, 0.15)` instead of `print(with_vat(100, 0.15))`. The call has to sit inside `print()`. |
| A value is worked out but then lost | A line like `amount * 1.07` calculates and throws the answer away. Store it: `amount = amount * 1.07`. |
| `IndentationError` | Lines in the function body must all start at the same column, one level in from `def`. |

## A habit worth having

Before you submit, call your function yourself with an input where you know the answer, and print the result:

```python
print(c_to_f(100))   # expect 212.0
```

If that prints the wrong thing, you've found the bug without spending a submission.
""",
    },
]
