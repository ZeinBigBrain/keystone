CHAPTER = {
    "title": "Variables and types",
    "summary": "Storing values, the main data types, converting between them, and f-strings.",
}

LESSONS = [
    {
        "id": "variables",
        "title": "Variables",
        "kind": "code",
        "body": """
A **variable** is a name that points at a value. You create one with `=`:

```python
crates = 14
price = 3.5
print(crates * price)   # 49.0
```

Read `=` as "now refers to", not "equals". The right-hand side is worked out first, then the name on the left is attached to the result.

Once a variable exists you can use its name anywhere you'd use the value. That's the point: write the number once, refer to it by name everywhere else, and change it in one place when it changes.

## Your task

A shelf is 6 metres long and each metre of it can hold 12.5 kg.

1. Create a variable `length` set to `6`.
2. Create a variable `capacity_per_m` set to `12.5`.
3. Create `total_capacity`, calculated from the two variables above (don't type 75).
4. Print `total_capacity`.
""",
        "starter": "# Create your variables here\n",
        "tests": '''
def test_length():
    "length is 6"
    check(need("length") == 6, "length should be 6.")

def test_cap():
    "capacity_per_m is 12.5"
    check(need("capacity_per_m") == 12.5, "capacity_per_m should be 12.5.")

def test_total():
    "total_capacity is worked out from the other two"
    check(need("total_capacity") == 75, "total_capacity should come out at 75.0.")
    check("75" not in CODE, "Calculate total_capacity from the variables instead of typing 75.")

def test_print():
    "Prints the total"
    check(LINES and LINES[-1] in ("75.0", "75"), "The last thing printed should be 75.0.")
''',
        "solution": "length = 6\ncapacity_per_m = 12.5\ntotal_capacity = length * capacity_per_m\nprint(total_capacity)\n",
        "hints": [
            "Variable names go on the left of `=`, values on the right.",
            "`total_capacity = length * capacity_per_m`",
        ],
    },
    {
        "id": "names",
        "title": "Naming rules",
        "kind": "quiz",
        "body": """
Variable names can use letters, digits and underscores. They can't start with a digit, can't contain spaces or dashes, and can't be one of Python's own keywords like `if`, `for` or `class`.

Names are case-sensitive, so `Total` and `total` are two different variables.

The usual Python style is lowercase words joined by underscores: `max_load`, `days_left`, `file_name`. This is called *snake_case*.
""",
        "question": "Which of these is a valid variable name?",
        "options": ["`2nd_floor`", "`floor-2`", "`floor_2`", "`floor 2`"],
        "answer": 2,
        "explain": "`floor_2` only uses letters, digits and an underscore, and starts with a letter. `2nd_floor` starts with a digit, `floor-2` would be read as `floor` minus `2`, and spaces aren't allowed at all.",
    },
    {
        "id": "types",
        "title": "Types of value",
        "kind": "read",
        "body": """
Every value in Python has a **type**. The four you'll meet constantly:

| Type | What it holds | Examples |
|---|---|---|
| `int` | whole numbers | `0`, `42`, `-7` |
| `float` | numbers with a decimal point | `3.5`, `0.1`, `-2.0` |
| `str` | text (a string) | `"hello"`, `'B2'`, `""` |
| `bool` | true or false | `True`, `False` |

You can ask Python for the type of anything:

```python
print(type(42))      # <class 'int'>
print(type(42.0))    # <class 'float'>
print(type("42"))    # <class 'str'>
```

Those are three different values even though they look alike. `42` is a number you can do maths with. `"42"` is two characters of text.

There's one more you'll see a lot: `None`. It means "no value here". Functions that don't hand anything back give you `None`, and it's a common way of saying "not set yet".

## Division always gives a float

`/` always returns a float, even when the answer is whole: `8 / 2` is `4.0`. If you want a whole number, use `//`.

## Floats aren't exact

Computers store decimals in binary, which can't represent most of them exactly. So:

```python
print(0.1 + 0.2)   # 0.30000000000000004
```

This isn't a Python bug. Every language does it. It matters when you compare floats, and later lessons show how to deal with it. For now, just don't be alarmed when you see it.
""",
    },
    {
        "id": "type-quiz",
        "title": "Guess the type",
        "kind": "quiz",
        "body": "Quick check on what you just read.",
        "question": "What does `print(type(9 / 3))` show?",
        "options": ["`<class 'int'>`", "`<class 'float'>`", "`<class 'str'>`", "`3`"],
        "answer": 1,
        "explain": "`/` always produces a float, so `9 / 3` is `3.0`. Use `9 // 3` if you want the int `3`.",
    },
    {
        "id": "converting",
        "title": "Converting between types",
        "kind": "code",
        "body": """
Data often arrives as text, from a file, a form or a spreadsheet export. Text that *looks* like a number still behaves like text:

```python
boxes = "12"
print(boxes * 2)   # 1212  (the text repeated twice)
print(boxes + 1)   # TypeError: can only concatenate str (not "int") to str
```

Python won't guess what you meant. You convert explicitly:

| Function | Does | Example |
|---|---|---|
| `int(x)` | to a whole number | `int("12")` gives `12` |
| `float(x)` | to a decimal number | `float("2.5")` gives `2.5` |
| `str(x)` | to text | `str(12)` gives `"12"` |

`int()` on a float chops off the decimal part rather than rounding: `int(7.9)` is `7`. For proper rounding there's `round(7.9)`, which gives `8`.

## Your task

The two values below came out of a text file, so they're strings. Work out the total weight of all the bags as a number and store it in `total_kg`, then print it.

The answer should be `1250.0`.
""",
        "starter": 'bags = "50"\nkg_per_bag = "25"\n\ntotal_kg = bags * kg_per_bag\nprint(total_kg)\n',
        "tests": '''
def test_total():
    "total_kg is the number 1250"
    t = need("total_kg")
    check(isinstance(t, (int, float)), "total_kg should be a number, but it's a %s." % type(t).__name__)
    check(t == 1250, "total_kg should be 1250 but it's %r." % t)

def test_untouched():
    "bags and kg_per_bag are still the original strings"
    check(need("bags") == "50" and need("kg_per_bag") == "25",
          "Leave the two text values as they are and convert them in the calculation.")
''',
        "solution": 'bags = "50"\nkg_per_bag = "25"\n\ntotal_kg = float(bags) * float(kg_per_bag)\nprint(total_kg)\n',
        "hints": [
            "Run the starter first. The error tells you Python can't multiply two strings.",
            "Wrap each one in `float()` inside the calculation.",
        ],
    },
    {
        "id": "fstrings",
        "title": "f-strings",
        "kind": "code",
        "body": """
Mixing text and values with `+` gets messy fast, because every number needs `str()` around it. **f-strings** are the clean way. Put an `f` before the opening quote and drop values in with curly brackets:

```python
item = "cement"
qty = 40
print(f"Delivered {qty} bags of {item}")
# Delivered 40 bags of cement
```

Anything inside `{}` is real Python, so you can do sums in there too:

```python
print(f"{qty} bags is {qty * 25} kg")
# 40 bags is 1000 kg
```

## Your task

Using the variables in the starter code, print exactly:

```
Room B12 is 4.5 m by 4 m, so 18.0 m2
```

Use an f-string, and calculate the area inside it or in a variable. Don't type any of the numbers into the text.
""",
        "starter": 'room = "B12"\nwidth = 4.5\nlength = 4\n\n# print the sentence here\n',
        "tests": '''
def test_line():
    "Prints the sentence exactly"
    want = "Room B12 is 4.5 m by 4 m, so 18.0 m2"
    check(LINES == [want], "Expected:\\n%s\\nGot:\\n%s" % (want, OUTPUT.strip()))

def test_fstring():
    "Uses an f-string with the variables"
    check('f"' in CODE or "f'" in CODE, "Use an f-string: put f before the opening quote.")
    check("{room}" in CODE.replace(" ", ""), "Put {room} inside the f-string instead of typing B12.")
    check("18.0" not in CODE, "Let Python work out the area.")
''',
        "solution": 'room = "B12"\nwidth = 4.5\nlength = 4\n\nprint(f"Room {room} is {width} m by {length} m, so {width * length} m2")\n',
        "hints": [
            'Start with `print(f"Room {room} is ...")` and keep going.',
            "The area is `{width * length}` inside the f-string.",
        ],
    },
    {
        "id": "updating",
        "title": "Updating a variable",
        "kind": "code",
        "body": """
A variable can be pointed at a new value at any time, including one based on its old value:

```python
score = 10
score = score + 5    # now 15
```

That pattern is so common there's a shorthand for it:

| Long form | Short form |
|---|---|
| `x = x + 3` | `x += 3` |
| `x = x - 3` | `x -= 3` |
| `x = x * 3` | `x *= 3` |
| `x = x / 3` | `x /= 3` |

## Your task

A water tank starts at 1200 litres. During the day:

- 350 litres are pumped in
- 800 litres are used
- 125 litres are pumped in

Update `level` after each event using `+=` and `-=` (one line per event), then print the final level.
""",
        "starter": "level = 1200\n\n# update level for each event\n\nprint(level)\n",
        "tests": '''
def test_final():
    "Final level is 875"
    check(need("level") == 875, "level should end at 875 but it's %r." % ns.get("level"))
    check(LINES and LINES[-1] == "875", "Print the final level.")

def test_shorthand():
    "Uses += and -="
    check(CODE.count("+=") >= 2 and "-=" in CODE, "Use += for the two top-ups and -= for the water used.")
''',
        "solution": "level = 1200\n\nlevel += 350\nlevel -= 800\nlevel += 125\n\nprint(level)\n",
        "hints": [
            "Three lines, one per event, each starting with `level`.",
            "`level += 350`, then `level -= 800`, then `level += 125`.",
        ],
    },
]
