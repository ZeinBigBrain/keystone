CHAPTER = {
    "title": "Getting started",
    "summary": "How the app works, your first lines of Python, and comments.",
}

LESSONS = [
    {
        "id": "welcome",
        "title": "How Keystone works",
        "kind": "read",
        "body": """
Every lesson here is one of three types.

- **Read** lessons explain something. Mark them as read to move on.
- **Quiz** lessons ask one question. You get full XP if you get it first time.
- **Code** lessons give you a task, an editor and a set of checks. These are where most of the learning happens.

## Running versus submitting

In a code lesson you'll see two buttons. **Run** just runs your code and shows what it printed, so you can poke at things as much as you like. **Submit** runs your code against the checks. Pass them all and the lesson is done.

Shortcuts: `Ctrl+Enter` runs, `Ctrl+Shift+Enter` submits.

## XP, levels and streaks

| Lesson type | XP |
|---|---|
| Read | 5 |
| Quiz | 10 first try, 3 after that |
| Code | 30 |

Hints are there when you're stuck, but each one knocks 20% off that exercise's XP. After three failed submissions the solution unlocks. Look at it before passing and the exercise is worth 0 XP, though it still counts as done.

Finish at least one lesson a day to keep your streak going. The flame in the top bar goes orange once you've done today's.

> Everything is saved to the `data` folder next to the app, including the code you type. Close the window halfway through an exercise and your code will still be there next time.
""",
    },
    {
        "id": "hello",
        "title": "Hello, world",
        "kind": "code",
        "body": """
Programs talk to us by printing text. In Python that's the `print()` function:

```python
print("Good morning")
```

The text inside the quotes is called a **string**. Python prints it exactly as written, without the quotes.

## Your task

Change the code so it prints exactly this:

```
Hello, world!
```

Capital H, a comma, and an exclamation mark at the end. The checks are strict about that.
""",
        "starter": 'print("hello")\n',
        "tests": '''
def test_output():
    "Prints exactly: Hello, world!"
    check(LINES == ["Hello, world!"], "Your code printed:\\n%r\\nExpected:\\n'Hello, world!'" % OUTPUT)
''',
        "solution": 'print("Hello, world!")\n',
        "hints": [
            "Only the text inside the quotes needs changing.",
            "Check capitals and punctuation: `Hello, world!`",
        ],
    },
    {
        "id": "several-lines",
        "title": "Several lines",
        "kind": "code",
        "body": """
Each `print()` call ends with a new line, so three calls give you three lines:

```python
print("one")
print("two")
print("three")
```

Python runs your code from top to bottom, one line at a time. The order you write things in is the order they happen.

## Your task

A site diary entry needs to print as three lines, in this order:

```
Date: Monday
Weather: dry
Crew on site: 12
```

Two of the lines are already there but in the wrong order, and one is missing.
""",
        "starter": 'print("Weather: dry")\nprint("Date: Monday")\n',
        "tests": '''
def test_count():
    "Prints three lines"
    check(len(LINES) == 3, "Expected 3 lines but got %d." % len(LINES))

def test_order():
    "Lines are in the right order with the right text"
    want = ["Date: Monday", "Weather: dry", "Crew on site: 12"]
    for n, (got, exp) in enumerate(zip(LINES, want), 1):
        check(got == exp, "Line %d is %r but should be %r." % (n, got, exp))
''',
        "solution": 'print("Date: Monday")\nprint("Weather: dry")\nprint("Crew on site: 12")\n',
        "hints": [
            "Swap the first two lines, then add a third `print()` underneath.",
            'The missing line is `print("Crew on site: 12")`.',
        ],
    },
    {
        "id": "quote-or-not",
        "title": "Quotes change everything",
        "kind": "quiz",
        "body": """
Anything inside quotes is text. Python doesn't look inside it, it just prints it.

Without quotes, Python treats what you wrote as code and works it out first. So `print(4 * 5)` prints `20`, because Python does the multiplication before printing.
""",
        "question": "What does this print?\n\n```python\nprint(\"6 + 4\")\nprint(6 + 4)\n```",
        "options": [
            "`10` then `10`",
            "`6 + 4` then `10`",
            "`6 + 4` then `6 + 4`",
            "An error, because you can't mix them",
        ],
        "answer": 1,
        "explain": "The first line has quotes, so it's a string and gets printed as-is. The second has none, so Python adds the numbers and prints `10`.",
    },
    {
        "id": "maths",
        "title": "Python as a calculator",
        "kind": "code",
        "body": """
Python handles arithmetic with the symbols you'd expect, plus a couple of extras:

| Symbol | Meaning | Example | Result |
|---|---|---|---|
| `+` | add | `7 + 2` | `9` |
| `-` | subtract | `7 - 2` | `5` |
| `*` | multiply | `7 * 2` | `14` |
| `/` | divide | `7 / 2` | `3.5` |
| `//` | divide, drop the remainder | `7 // 2` | `3` |
| `%` | remainder only | `7 % 2` | `1` |
| `**` | power | `7 ** 2` | `49` |

Brackets work like they do on paper: `(2 + 3) * 4` is `20`, while `2 + 3 * 4` is `14`.

## Your task

Print how many seconds there are in one week. Let Python work it out: write the sum, not the answer. Seven days, 24 hours, 60 minutes, 60 seconds.
""",
        "starter": "# Print the number of seconds in a week\n",
        "tests": '''
def test_value():
    "Prints 604800"
    check(LINES == ["604800"], "Your code printed %r. Expected 604800." % OUTPUT.strip())

def test_calculated():
    "Python does the maths (the number 604800 isn't typed in)"
    check("604800" not in CODE, "Write the multiplication out and let Python calculate it.")
    check("*" in CODE, "Use * to multiply.")
''',
        "solution": "print(7 * 24 * 60 * 60)\n",
        "hints": [
            "Multiply the four numbers together inside `print()`.",
            "`print(7 * 24 * 60 * 60)`",
        ],
    },
    {
        "id": "comments",
        "title": "Comments",
        "kind": "code",
        "body": """
A line that starts with `#` is a **comment**. Python skips it completely. Comments are notes for people, including you in three months' time.

```python
# Load in kN, from the 2nd floor schedule
print(45 * 1.5)  # factored load
```

The second example shows a comment can also sit at the end of a line of code.

Comments are also handy for switching a line off while you test something, without deleting it.

## Your task

Someone left a note in this code as plain text, so Python tries to run it and fails with a `SyntaxError`. Hit **Run** to see the error.

Turn the note into a comment (keep the words) so the program runs and prints `Total: 42`.
""",
        "starter": "This adds up the two piles of blocks\nprint(\"Total:\", 30 + 12)\n",
        "tests": '''
def test_runs():
    "The program runs and prints Total: 42"
    check(LINES == ["Total: 42"], "Expected 'Total: 42' but got %r." % OUTPUT.strip())

def test_note_kept():
    "The note is still there, as a comment"
    found = [l for l in RAW_CODE.splitlines() if l.strip().startswith("#") and "piles of blocks" in l]
    check(found, "Keep the note, just put # at the start of its line.")
''',
        "solution": "# This adds up the two piles of blocks\nprint(\"Total:\", 30 + 12)\n",
        "hints": [
            "Python reads `This adds up...` as code. What character makes Python skip a line?",
            "Put `#` at the very start of the first line.",
        ],
    },
]
