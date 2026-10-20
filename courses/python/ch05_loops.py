CHAPTER = {
    "title": "Loops",
    "summary": "Repeating work with for and while: running totals, counting, searching, break, and the shapes these take inside a function.",
}

# How this chapter is paced
# Each loop pattern is met three times: at the top level first, then inside a
# function with a matching worked example and a scaffolded starter, then in a
# task that combines it with something else. Starter support fades as you go.

LESSONS = [
    {
        "id": "for-range",
        "title": "for loops and range()",
        "kind": "code",
        "body": """
A `for` loop runs its body once for each value in a sequence. `range()` makes a sequence of numbers:

```python
for i in range(3):
    print("lap", i)
# lap 0
# lap 1
# lap 2
```

`range(3)` gives 0, 1, 2. It starts at 0 and **stops before** the number you give it. That feels odd at first, but it means `range(n)` always loops exactly `n` times.

You can also give a start: `range(1, 4)` gives 1, 2, 3.

Everything indented under the `for` line runs every time round. The first line that isn't indented runs once, after the loop has finished.

## Your task

Print the 7 times table from 1 to 10, one line each, in this exact format:

```
7 x 1 = 7
7 x 2 = 14
...
7 x 10 = 70
```

Use a loop. Ten separate print lines won't pass.
""",
        "starter": "# print the 7 times table\n",
        "tests": '''
def test_lines():
    "Prints 7 x 1 = 7 through 7 x 10 = 70"
    want = ["7 x %d = %d" % (i, 7 * i) for i in range(1, 11)]
    check(LINES == want, "Expected 10 lines starting '7 x 1 = 7'. Got:\\n" + OUTPUT)

def test_loop():
    "Uses one print() inside a for loop"
    import ast
    tree = ast.parse(RAW_CODE)
    def is_print(n):
        return isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print"
    prints = [n for n in ast.walk(tree) if is_print(n)]
    in_loop = [n for loop in ast.walk(tree) if isinstance(loop, ast.For)
               for n in ast.walk(loop) if is_print(n)]
    check(in_loop, "Put your print() inside a for loop.")
    check(len(prints) == 1, "Use a single print() inside the loop rather than several print lines.")
''',
        "solution": 'for i in range(1, 11):\n    print(f"7 x {i} = {7 * i}")\n',
        "hints": [
            "`range(1, 11)` gives you 1 up to 10.",
            '`print(f"7 x {i} = {7 * i}")` inside the loop.',
        ],
    },
    {
        "id": "loop-indent",
        "title": "Inside or after the loop?",
        "kind": "quiz",
        "body": "Indentation decides whether a line runs every time round, or once at the end. Trace this one.",
        "question": "What does this print?\n\n```python\ntotal = 0\nfor n in range(1, 4):\n    total += n\n    print(total)\n```",
        "options": ["`1`, `3`, `6` on three lines", "Just `6`", "`1`, `2`, `3` on three lines", "`0`, `1`, `3` on three lines"],
        "answer": 0,
        "explain": "The `print` is indented, so it's part of the loop and runs every time round, showing the total so far: 1, then 1 + 2 = 3, then 3 + 3 = 6. To print only the final `6`, move the `print` back out to the left edge so it runs once, after the loop.",
    },
    {
        "id": "range-step",
        "title": "range() with a step",
        "kind": "quiz",
        "body": """
`range()` takes up to three numbers: `range(start, stop, step)`.

```python
range(0, 10, 2)    # 0, 2, 4, 6, 8
range(10, 0, -3)   # 10, 7, 4, 1
```

The stop value is never included, in either direction.
""",
        "question": "Which numbers does `range(2, 12, 3)` produce?",
        "options": ["2, 5, 8, 11", "2, 5, 8", "3, 6, 9, 12", "2, 5, 8, 11, 14"],
        "answer": 0,
        "explain": "Start at 2 and add 3 each time: 2, 5, 8, 11. The next would be 14, which is past the stop value of 12.",
    },
    {
        "id": "total-top",
        "title": "Running totals",
        "kind": "code",
        "body": """
A very common loop pattern: start a variable at zero, then add to it each time round.

```python
total = 0                  # 1. before the loop: start at zero
for n in range(1, 5):
    total += n             # 2. inside the loop: add this value
print(total)               # 3. after the loop: use the result
# 10  (1 + 2 + 3 + 4)
```

Each of the three lines has a fixed place, and putting one in the wrong place is the most common loop bug there is:

- `total = 0` **inside** the loop resets it every time round, so you end up with just the last number.
- `print(total)` **inside** the loop prints a running list instead of one answer (you saw this in the last quiz).

## Your task

Add up every whole number from 1 to 100 and print the total once, at the end. Let the loop do the adding: don't type the answer.
""",
        "starter": "total = 0\n\n# loop over the numbers 1 to 100 and add each one to total\n\n\n# print total once, after the loop (not indented)\n",
        "tests": '''
def test_value():
    "Prints 5050, once"
    check(LINES == ["5050"], "Expected a single line, 5050. Your code printed:\\n%s\\n(If you see lots of lines, your print is inside the loop.)" % OUTPUT)

def test_loop():
    "Uses a for loop"
    import ast
    check(any(isinstance(n, ast.For) for n in ast.walk(ast.parse(RAW_CODE))), "Use a for loop to do the adding.")
    check("5050" not in CODE, "Let the loop work out the total.")
''',
        "solution": "total = 0\n\nfor n in range(1, 101):\n    total += n\n\nprint(total)\n",
        "hints": [
            "`range(1, 101)` gives 1 up to 100. Inside the loop: `total += n`.",
            "The `print(total)` line goes at the left edge, after the loop, so it runs once.",
        ],
    },
    {
        "id": "total-func",
        "title": "Running totals inside a function",
        "kind": "code",
        "body": """
Now the same pattern inside a function. All three lines move inside the function, and the `print` turns into a `return`:

```python
def sum_of_squares(n):
    total = 0                  # 1. start at zero, INSIDE the function
    for i in range(1, n + 1):
        total += i * i         # 2. add to it, inside the loop
    return total               # 3. hand it back, AFTER the loop
```

Look at the indentation of each line:

| Line | Lined up with | Why |
|---|---|---|
| `total = 0` | the `for` | it belongs to the function and runs once |
| `total += ...` | one step in from the `for` | it runs every time round |
| `return total` | the `for` | it runs once, after the loop has finished |

> **Common slips:**
> - `total = 0` written *above* the `def`, outside the function. Python then refuses to let the function change it, and you get `UnboundLocalError`. Create it inside the function.
> - `return total` indented inside the loop. The function returns on the first time round, so you get only the first number.

## Your task

Write `sum_to(n)` that returns 1 + 2 + ... + n. So `sum_to(4)` returns 10. If `n` is 0, the answer is 0.
""",
        "starter": "def sum_to(n):\n    # 1. start a total at 0 (inside the function)\n    # 2. loop from 1 up to and including n, adding each number to the total\n    # 3. return the total (after the loop, lined up with the for)\n    pass\n\n\nprint(sum_to(4))   # should print 10\n",
        "tests": '''
def test_values():
    "Right totals"
    f = need("sum_to")
    for n, want in [(4, 10), (1, 1), (0, 0), (10, 55), (100, 5050)]:
        v, _ = capture(f, n)
        check(v == want, "sum_to(%d) returned %r, expected %d." % (n, v, want))

def test_shape():
    "Return is after the loop, not inside it"
    msg = loop_return_problem("sum_to")
    check(not msg, msg)
    check("sum(" not in CODE, "Use a loop with a running total rather than sum().")
''',
        "solution": "def sum_to(n):\n    total = 0\n    for i in range(1, n + 1):\n        total += i\n    return total\n\n\nprint(sum_to(4))\n",
        "hints": [
            "`range(1, n + 1)` goes from 1 up to and including n.",
            "Three lines inside the function: `total = 0`, then the loop with `total += i`, then `return total` lined up with the `for`.",
        ],
    },
    {
        "id": "unbound",
        "title": "Spot the error",
        "kind": "quiz",
        "body": "This is the error that catches nearly everyone the first time they put a loop in a function.",
        "question": "What happens when this runs?\n\n```python\ncount = 0\n\ndef add_up(n):\n    for i in range(n):\n        count += 1\n    return count\n\nprint(add_up(3))\n```",
        "options": ["It prints `3`", "It prints `0`", "It raises `UnboundLocalError`", "It raises `SyntaxError`"],
        "answer": 2,
        "explain": "Because the function *changes* `count` (with `+=`), Python treats `count` as the function's own variable. But the function never created one, so the first `count += 1` has nothing to add to. The fix is to move `count = 0` inside the function, just above the loop.",
    },
    {
        "id": "total-filter",
        "title": "Counting only some values",
        "kind": "code",
        "body": """
Put an `if` inside the loop and you can choose which values to add or count. Here's a total that only takes multiples of 7:

```python
def sum_sevens(limit):
    total = 0
    for n in range(1, limit + 1):
        if n % 7 == 0:         # only when n divides by 7...
            total += n         # ...add it (note the extra indent)
    return total
```

Counting is the same idea, except you add 1 each time instead of the number itself: `count += 1`.

## Your task

Write `count_multiples(limit, d)` that returns **how many** whole numbers from 1 up to and including `limit` divide exactly by `d`.

`count_multiples(20, 6)` is 3, because of 6, 12 and 18.
""",
        "starter": "def count_multiples(limit, d):\n    # same shape as sum_sevens, but count instead of add\n    pass\n",
        "tests": '''
def test_values():
    "Right counts"
    f = need("count_multiples")
    for args, want in [((20, 6), 3), ((10, 1), 10), ((5, 7), 0), ((21, 7), 3), ((100, 3), 33)]:
        v, _ = capture(f, *args)
        check(v == want, "count_multiples%r returned %r, expected %d." % (args, v, want))

def test_shape():
    "Return is after the loop"
    msg = loop_return_problem("count_multiples")
    check(not msg, msg)
''',
        "solution": "def count_multiples(limit, d):\n    count = 0\n    for n in range(1, limit + 1):\n        if n % d == 0:\n            count += 1\n    return count\n",
        "hints": [
            "Start `count = 0` inside the function. Loop over `range(1, limit + 1)`.",
            "Inside the loop: `if n % d == 0:` then `count += 1`. After the loop: `return count`.",
        ],
    },
    {
        "id": "accumulate",
        "title": "Multiples of 3 or 5",
        "kind": "code",
        "body": """
This one combines the last two lessons: a running total inside a function, with a condition that has two parts.

## Your task

Write `sum_multiples(limit)` that returns the sum of every number **below** `limit` that's divisible by 3 or by 5.

For example, below 10 those numbers are 3, 5, 6 and 9, so `sum_multiples(10)` returns `23`. A number like 15 that's divisible by both should only be counted once.

Note the word **below**: `limit` itself isn't included.
""",
        "starter": "def sum_multiples(limit):\n    pass\n",
        "tests": '''
def test_values():
    "Right totals for several limits"
    f = need("sum_multiples")
    for lim, want in [(10, 23), (1, 0), (4, 3), (16, 60), (1000, 233168)]:
        v, _ = capture(f, lim)
        check(v == want, "sum_multiples(%d) returned %r, expected %d." % (lim, v, want))

def test_shape():
    "Return is after the loop"
    msg = loop_return_problem("sum_multiples")
    check(not msg, msg)
''',
        "solution": "def sum_multiples(limit):\n    total = 0\n    for n in range(limit):\n        if n % 3 == 0 or n % 5 == 0:\n            total += n\n    return total\n",
        "hints": [
            "Loop over `range(limit)` and only add the number when `n % 3 == 0 or n % 5 == 0`.",
            "Set `total = 0` before the loop and `return total` after it (not inside it).",
        ],
    },
    {
        "id": "while-top",
        "title": "while loops",
        "kind": "code",
        "body": """
A `while` loop keeps going as long as its condition is true. Use it when you don't know in advance how many times you'll need to go round.

```python
balance = 100
months = 0
while balance > 0:        # keep going while there's still money
    balance -= 30         # change the thing the condition looks at
    months += 1           # count this time round
print(months)   # 4
```

## Writing the condition

The condition says when to **keep going**, not when to stop. Ask yourself "what's true while I still have work to do?". Here, there's still money, so `balance > 0`. Write the stopping point backwards (`balance <= 0`) and the loop never runs at all.

> **Common slips:**
> - A condition written the wrong way round, so the loop runs zero times.
> - Working out a new value but not storing it. `balance - 30` on its own line calculates and throws the answer away, so `balance` never changes and the loop runs forever. You need `balance -= 30` (or `balance = balance - 30`).
> - Putting `months = 0` inside the loop, which resets the count every time round.
>
> Keystone stops your code after a few seconds if a loop never ends.

## Your task

A crack is 2 mm wide and grows by 20% each week (multiply by 1.2). Print how many whole weeks it takes to reach **at least** 5 mm.
""",
        "starter": "width = 2.0\nweeks = 0\n\n# keep going while the crack is still under 5 mm:\n#     grow width by 20% (multiply it by 1.2 and store the result)\n#     add 1 to weeks\n\nprint(weeks)\n",
        "tests": '''
def test_value():
    "Prints 6"
    check(LINES == ["6"], "Expected 6. Your code printed:\\n%s" % OUTPUT)

def test_while():
    "Uses a while loop and really grows the width"
    import ast
    check(any(isinstance(n, ast.While) for n in ast.walk(ast.parse(RAW_CODE))), "This one's practice for while, so use a while loop.")
    check(need("weeks") == 6, "weeks should end at 6.")
    check(need("width") >= 5, "width should end at 5 mm or more. Did you store the new width each time round?")
''',
        "solution": "width = 2.0\nweeks = 0\n\nwhile width < 5:\n    width *= 1.2\n    weeks += 1\n\nprint(weeks)\n",
        "hints": [
            "While there's still work to do, the crack is under 5 mm: `while width < 5:`.",
            "Inside the loop: `width *= 1.2` and `weeks += 1`. The print stays at the left edge.",
        ],
    },
    {
        "id": "while-cond",
        "title": "Which way round?",
        "kind": "quiz",
        "body": "One question on writing the condition the right way round.",
        "question": "`x` starts at 1. You want to keep doubling it until it reaches **at least** 100. Which line should start the loop?",
        "options": ["`while x >= 100:`", "`while x < 100:`", "`while x == 100:`", "`while x > 1:`"],
        "answer": 1,
        "explain": "The condition describes when to keep going. While `x` is still under 100 there's more doubling to do, so `while x < 100:`. With `x >= 100` the loop wouldn't run at all, because 1 isn't 100 or more. `x > 1` would never become false, so it would run forever.",
    },
    {
        "id": "while",
        "title": "while inside a function",
        "kind": "code",
        "body": """
The same loop inside a function. As with running totals, the starting values move inside the function and the `print` becomes a `return` after the loop:

```python
def weeks_to_reach(width, limit):
    weeks = 0                  # inside the function, before the loop
    while width < limit:
        width *= 1.2
        weeks += 1
    return weeks               # after the loop, lined up with while
```

## Your task

Money growing at a fixed yearly rate doubles eventually. Write `years_to_double(rate)` that returns how many whole years it takes for an amount to reach **at least** double. `rate` is a fraction, so 7% is `0.07`.

Start with `amount = 1.0` and multiply by `(1 + rate)` each year. At 7% the answer is 11. At 10% it's 8.
""",
        "starter": "def years_to_double(rate):\n    # same shape as weeks_to_reach\n    pass\n\n\nprint(years_to_double(0.07))   # should print 11\n",
        "tests": '''
def test_values():
    "Right number of years for several rates"
    f = need("years_to_double")
    for r, want in [(0.07, 11), (0.10, 8), (1.0, 1), (0.5, 2), (0.01, 70)]:
        v, _ = capture(f, r)
        check(v == want, "years_to_double(%r) returned %r, expected %d." % (r, v, want))

def test_while():
    "Uses a while loop"
    check("while " in CODE, "This one's practice for while, so use a while loop.")
    msg = loop_return_problem("years_to_double")
    check(not msg, msg)
''',
        "solution": "def years_to_double(rate):\n    amount = 1.0\n    years = 0\n    while amount < 2:\n        amount *= 1 + rate\n        years += 1\n    return years\n\n\nprint(years_to_double(0.07))\n",
        "hints": [
            "Inside the function: `amount = 1.0` and `years = 0`, then keep looping `while amount < 2`.",
            "In the loop: `amount *= 1 + rate` and `years += 1`. After it: `return years`.",
        ],
    },
    {
        "id": "break-intro",
        "title": "Stopping early with break",
        "kind": "code",
        "body": """
Sometimes you know the answer before the loop has finished. `break` jumps straight out of the loop, and the program carries on from the first line after it.

```python
for n in range(1, 100):
    if n * n > 50:
        print(n)       # 8, the first number whose square is over 50
        break          # no point checking 9, 10, 11 ...
```

There's also `continue`, which skips the rest of this time round and moves on to the next value:

```python
for n in range(6):
    if n % 2 == 0:
        continue       # skip even numbers
    print(n)           # 1, 3, 5
```

`break` is the one you'll use most.

## Your task

A **divisor** of `n` is a number that divides it exactly, so `n % d == 0`. Starting at 2 and counting up, find the **smallest** divisor of `n`, print it, and stop the loop.

For `n = 91` that's 7. The checks will also try other values of `n`.
""",
        "starter": "n = 91\n\nfor d in range(2, n + 1):\n    # if d divides n exactly, print d and break out of the loop\n    pass\n",
        "tests": '''
import re, io, contextlib

def run_with(v):
    src = re.sub(r"^n\\s*=.*$", "n = %d" % v, RAW_CODE, count=1, flags=re.M)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, "<your code>", "exec"), {"__name__": "__main__"})
    return buf.getvalue().split()

def test_91():
    "Prints 7 for 91, and only 7"
    check(LINES == ["7"], "For n = 91 expected just 7. Your code printed:\\n%s\\n(Several numbers means the loop didn't stop. Use break.)" % OUTPUT)

def test_others():
    "Works for other numbers"
    for v, want in [(15, "3"), (97, "97"), (49, "7"), (2, "2")]:
        got = run_with(v)
        check(got == [want], "For n = %d expected %s, got %s." % (v, want, " ".join(got) or "nothing"))

def test_break():
    "Uses break"
    import ast
    check(any(isinstance(x, ast.Break) for x in ast.walk(ast.parse(RAW_CODE))), "Stop the loop with break once you've found it.")
''',
        "solution": "n = 91\n\nfor d in range(2, n + 1):\n    if n % d == 0:\n        print(d)\n        break\n",
        "hints": [
            "Replace `pass` with `if n % d == 0:` and indent two lines under it.",
            "Under the `if`: `print(d)` then `break`.",
        ],
    },
    {
        "id": "search-return",
        "title": "Searching inside a function",
        "kind": "code",
        "body": """
Inside a function, `return` does `break`'s job and hands back the answer at the same time. That gives a pattern you'll use constantly: **search, return as soon as you find it, and return something else if you never do.**

```python
def first_square_over(limit):
    for n in range(1, limit + 1):
        if n * n > limit:
            return n           # found it: stop and hand it back
    return None                # the loop finished without finding one
```

The two `return` lines are at different depths on purpose:

- The one **inside** the `if` runs the moment a match turns up.
- The one **after** the loop, lined up with `for`, only runs if the loop went all the way through without finding anything.

> **Common slip:** adding an `else: return None` under the `if`, inside the loop. Then the very first number that doesn't match ends the function, and the loop never looks at the second one. "Not found" can only be decided after checking everything, so it goes after the loop.

## Your task

Write `first_divisor(n)` that returns the smallest divisor of `n` between 2 and `n - 1`. If there isn't one (which happens when `n` is prime), return `None`.

`first_divisor(91)` is 7. `first_divisor(13)` is `None`.
""",
        "starter": "def first_divisor(n):\n    # loop d from 2 up to (but not including) n\n    #     if d divides n exactly, return d\n    # after the loop (lined up with the for): return None\n    pass\n\n\nprint(first_divisor(91))   # should print 7\nprint(first_divisor(13))   # should print None\n",
        "tests": '''
def test_found():
    "Returns the smallest divisor"
    f = need("first_divisor")
    for n, want in [(91, 7), (15, 3), (49, 7), (100, 2), (221, 13)]:
        v, _ = capture(f, n)
        check(v == want, "first_divisor(%d) returned %r, expected %d." % (n, v, want))

def test_none():
    "Returns None when there's no divisor"
    f = need("first_divisor")
    for n in (13, 2, 3, 97):
        v, _ = capture(f, n)
        check(v is None, "first_divisor(%d) returned %r, expected None (%d is prime)." % (n, v, n))

def test_shape():
    "The not-found return is after the loop"
    msg = loop_return_problem("first_divisor")
    check(not msg, msg)
''',
        "solution": "def first_divisor(n):\n    for d in range(2, n):\n        if n % d == 0:\n            return d\n    return None\n\n\nprint(first_divisor(91))\nprint(first_divisor(13))\n",
        "hints": [
            "`for d in range(2, n):` then `if n % d == 0: return d`.",
            "The last line, `return None`, lines up with the `for`, not with the `if`.",
        ],
    },
    {
        "id": "loop-return-bug",
        "title": "Find the bug",
        "kind": "quiz",
        "body": "This looks reasonable, but it has the slip from the last lesson. Trace what happens for 9.",
        "question": "What does this print?\n\n```python\ndef has_divisor(n):\n    for d in range(2, n):\n        if n % d == 0:\n            return True\n        else:\n            return False\n\nprint(has_divisor(9))\n```",
        "options": ["`True`", "`False`", "`None`", "An error"],
        "answer": 1,
        "explain": "The first time round, `d` is 2. 9 doesn't divide by 2, so the `else` returns `False` straight away, and the function never gets to try 3. The fix: delete the `else`, and put `return False` after the loop.",
    },
    {
        "id": "break",
        "title": "Is it prime?",
        "kind": "code",
        "body": """
A **prime** is a whole number above 1 that only divides by 1 and itself.

You already have almost all of this. `is_prime` is `first_divisor` with one guard clause in front. Here's a worked example with exactly the same shape, solving a different problem:

```python
def divisible_by_any(n, low, high):
    if low > high:                  # 1. guard: deal with the odd case first
        return False
    for d in range(low, high + 1):
        if n % d == 0:              # 2. found one: answer known, stop now
            return True
    return False                    # 3. checked them all, none found
```

For `is_prime` the three parts are:

1. **Guard:** numbers below 2 aren't prime. Check `n < 2` before the loop and return `False`.
2. **Search:** loop through possible divisors from 2. The moment one divides `n` exactly, it isn't prime: return `False`.
3. **After the loop:** nothing divided it, so return `True`.

> **Common slips:**
> - Putting the `n < 2` check *inside* the loop. For 0 and 1 the loop doesn't run at all, so the check never happens. It goes before the loop.
> - Testing the wrong variable, like `d < 2` instead of `n < 2`.
> - `return True` inside the loop (or in an `else`), which decides after checking only one divisor.

You only need to check divisors up to the square root of `n`, but going up to `n` is fine for now.

## Your task

Write `is_prime(n)` that returns `True` or `False`.
""",
        "starter": "def is_prime(n):\n    pass\n",
        "tests": '''
def test_small():
    "Correct for -3 to 30"
    f = need("is_prime")
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29}
    for n in range(-3, 31):
        v, _ = capture(f, n)
        check(v is (n in primes), "is_prime(%d) returned %r, expected %r." % (n, v, n in primes))

def test_big():
    "Handles a big prime (7919) and a big non-prime (7917)"
    f = need("is_prime")
    check(capture(f, 7919)[0] is True, "7919 is prime.")
    check(capture(f, 7917)[0] is False, "7917 = 3 x 7 x 13 x 29, so it isn't prime.")

def test_shape():
    "Decides 'prime' only after the loop"
    msg = loop_return_problem("is_prime")
    check(not msg, msg)
''',
        "solution": "def is_prime(n):\n    if n < 2:\n        return False\n    for d in range(2, int(n ** 0.5) + 1):\n        if n % d == 0:\n            return False\n    return True\n",
        "hints": [
            "Deal with `n < 2` first, before the loop. Then loop `for d in range(2, n):` and return False as soon as `n % d == 0`.",
            "If the loop finishes without finding a divisor, `return True` after it, lined up with the `for`.",
        ],
    },
    {
        "id": "loop-patterns",
        "title": "Loop patterns at a glance",
        "kind": "read",
        "body": """
Almost every loop you'll write for a while is one of these four. When you're stuck, work out which one you need, then copy its shape.

## Do something to each value

```python
for n in range(1, 4):
    print(n * 10)
```

## Running total or count

```python
def total_of(n):
    total = 0                # before the loop, inside the function
    for i in range(1, n + 1):
        total += i           # or count += 1, maybe under an if
    return total             # after the loop
```

## Repeat until something is true

```python
def steps_until(x, limit):
    steps = 0
    while x < limit:         # the condition for KEEPING GOING
        x *= 2               # change what the condition looks at
        steps += 1
    return steps
```

## Search and stop

```python
def first_match(n):
    if n < 1:                # optional guard first
        return None
    for d in range(2, n + 1):
        if n % d == 0:
            return d         # found: stop now
    return None              # not found: only decided after the loop
```

## Three questions to ask about every line

1. Should this run **once before**, **every time round**, or **once after** the loop? That decides its indentation.
2. Is this variable created **inside** the function? If the function changes it, it must be.
3. Am I **storing** the new value, or just working it out and losing it?
""",
    },
    {
        "id": "tea-break",
        "title": "Chapter project: tea break",
        "kind": "code",
        "body": """
A small project to pull this chapter together.

A site radio counts the minutes from 1 to 30. But:

- every 4th minute it says `Tea` instead of the number
- every 6th minute it says `Break` instead
- when both apply, it says `TeaBreak`

So the output starts `1, 2, 3, Tea, 5, Break, 7, Tea, 9, 10, 11, TeaBreak, ...` with each item on its own line.

## Your task

Print all 30 lines.

Think about which check has to come first. (Hint: if you check for 4 first, what happens at 12?)
""",
        "starter": "# print minutes 1 to 30\n",
        "tests": '''
def expected():
    out = []
    for i in range(1, 31):
        if i % 12 == 0: out.append("TeaBreak")
        elif i % 4 == 0: out.append("Tea")
        elif i % 6 == 0: out.append("Break")
        else: out.append(str(i))
    return out

def test_count():
    "Prints 30 lines"
    check(len(LINES) == 30, "Expected 30 lines, got %d." % len(LINES))

def test_values():
    "Every line is right"
    for n, (got, want) in enumerate(zip(LINES, expected()), 1):
        check(got == want, "Minute %d should be %r but you printed %r." % (n, want, got))
''',
        "solution": 'for i in range(1, 31):\n    if i % 4 == 0 and i % 6 == 0:\n        print("TeaBreak")\n    elif i % 4 == 0:\n        print("Tea")\n    elif i % 6 == 0:\n        print("Break")\n    else:\n        print(i)\n',
        "hints": [
            "Check the \"both\" case first, with `and`, then 4, then 6, then the plain number.",
            "Both 4 and 6 divide a number exactly when 12 does, so `i % 12 == 0` also works for the first check.",
        ],
    },
]
