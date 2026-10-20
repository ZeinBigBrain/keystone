CHAPTER = {
    "title": "Working with text",
    "summary": "Indexing and slicing strings, string methods, number formatting, split and join.",
}

LESSONS = [
    {
        "id": "string-index",
        "title": "Strings are sequences",
        "kind": "code",
        "body": """
A string is a sequence of characters, so everything you learned about indexing and slicing lists works on strings too:

```python
code = "CP09-A"
code[0]      # 'C'
code[-1]     # 'A'
code[:4]     # 'CP09'
len(code)    # 6
```

You can loop over a string one character at a time with `for ch in code:`.

## Your task

Write `initials(full_name)` that returns the initials of a two-word name, each followed by a full stop.

`initials("Ada Lovelace")` returns `"A.L."`. The name might be typed in lowercase, but the initials should always be capitals. (`.upper()` makes text uppercase.)

`full_name.split()` gives you the two words as a list.
""",
        "starter": "def initials(full_name):\n    pass\n",
        "tests": '''
def test_values():
    "Returns capital initials with full stops"
    f = need("initials")
    for name, want in [("Ada Lovelace", "A.L."), ("grace hopper", "G.H."), ("Alan Turing", "A.T.")]:
        v, _ = capture(f, name)
        check(v == want, "initials(%r) returned %r, expected %r." % (name, v, want))
''',
        "solution": 'def initials(full_name):\n    first, last = full_name.split()\n    return f"{first[0].upper()}.{last[0].upper()}."\n',
        "hints": [
            "`first, last = full_name.split()` unpacks the two words.",
            "Take `[0]` of each word, `.upper()` it, and join them with full stops.",
        ],
    },
    {
        "id": "string-methods",
        "title": "String methods",
        "kind": "code",
        "body": """
Strings come with a lot of built-in methods. A few you'll use constantly:

| Method | Does | Example result |
|---|---|---|
| `s.upper()` / `s.lower()` | change case | `"Abc".lower()` gives `"abc"` |
| `s.strip()` | remove spaces from both ends | `"  hi ".strip()` gives `"hi"` |
| `s.replace(a, b)` | swap every `a` for `b` | `"a-b".replace("-", "+")` gives `"a+b"` |
| `s.startswith(x)` | True or False | `"RFI-12".startswith("RFI")` gives `True` |
| `s.count(x)` | how many times `x` appears | `"banana".count("a")` gives `3` |
| `s.find(x)` | index of first `x`, or -1 | `"banana".find("n")` gives `2` |

Methods can be chained, and Python runs them left to right:

```python
"  hello world ".strip().upper()   # 'HELLO WORLD'
```

## Your task

Package codes get typed in all sorts of ways. Write `clean_code(raw)` that tidies one up:

1. remove spaces at either end
2. make it uppercase
3. replace any remaining single spaces with dashes

So `"  cp 09 a "` becomes `"CP-09-A"`.
""",
        "starter": "def clean_code(raw):\n    pass\n",
        "tests": '''
def test_values():
    "Cleans several messy codes"
    f = need("clean_code")
    for raw, want in [("  cp 09 a ", "CP-09-A"), ("cp10", "CP10"), ("Zone 3 north", "ZONE-3-NORTH"), ("X", "X")]:
        v, _ = capture(f, raw)
        check(v == want, "clean_code(%r) returned %r, expected %r." % (raw, v, want))
''',
        "solution": 'def clean_code(raw):\n    return raw.strip().upper().replace(" ", "-")\n',
        "hints": [
            "Chain the three methods in the order given.",
            '`raw.strip().upper().replace(" ", "-")`',
        ],
    },
    {
        "id": "immutable",
        "title": "Strings don't change",
        "kind": "quiz",
        "body": """
Like tuples, strings **can't be changed** once they exist. Methods like `.upper()` don't change the string. They build and return a new one.

That's why this is a common bug:

```python
name = "sara"
name.upper()      # result thrown away
print(name)       # still 'sara'
```

The fix is to keep the result: `name = name.upper()`.
""",
        "question": "What does this print?\n\n```python\nref = \"  rfi-0042  \"\nref.strip()\nprint(len(ref))\n```",
        "options": ["`8`", "`12`", "`10`", "An error"],
        "answer": 1,
        "explain": "`ref.strip()` makes a new, trimmed string, but nothing stores it. `ref` still has its two leading and two trailing spaces, so its length is 12. `ref = ref.strip()` would make it 8.",
    },
    {
        "id": "format-numbers",
        "title": "Formatting numbers",
        "kind": "code",
        "body": """
Inside an f-string, a colon after the value lets you control how it's shown:

```python
x = 1234.5678
f"{x:.2f}"     # '1234.57'     2 decimal places
f"{x:,.2f}"    # '1,234.57'    plus thousands separators
f"{x:.0f}"     # '1235'        no decimals (rounded)
f"{0.256:.1%}" # '25.6%'       as a percentage
```

You can also pad things to a fixed width, which lines up columns nicely:

```python
f"{'Sand':<10}|"   # 'Sand      |'  left-aligned in 10 characters
f"{42:>6}|"        # '    42|'      right-aligned in 6
```

## Your task

Write `money(amount)` that returns an amount formatted like `"SAR 1,234.50"`: the text `SAR`, a space, thousands separators and exactly two decimal places.
""",
        "starter": "def money(amount):\n    pass\n",
        "tests": '''
def test_values():
    "Formats amounts correctly"
    f = need("money")
    for a, want in [(1234.5, "SAR 1,234.50"), (0, "SAR 0.00"), (1000000, "SAR 1,000,000.00"),
                    (19.999, "SAR 20.00"), (7.1, "SAR 7.10")]:
        v, _ = capture(f, a)
        check(v == want, "money(%r) returned %r, expected %r." % (a, v, want))
''',
        "solution": 'def money(amount):\n    return f"SAR {amount:,.2f}"\n',
        "hints": [
            "The format spec you want is `,.2f`.",
            '`return f"SAR {amount:,.2f}"`',
        ],
    },
    {
        "id": "validating",
        "title": "Checking text",
        "kind": "code",
        "body": """
Some handy True-or-False checks on strings:

| Method | True when |
|---|---|
| `s.isdigit()` | every character is a digit (and there's at least one) |
| `s.isalpha()` | every character is a letter |
| `s.startswith(x)` / `s.endswith(x)` | it begins or ends with `x` |
| `x in s` | `x` appears anywhere in `s` |

## Your task

RFI references in a document register look like `RFI-0042`: the letters `RFI-` followed by exactly four digits.

Write `is_valid_ref(ref)` that returns `True` for a valid reference and `False` for anything else. Lowercase `rfi-0042` doesn't count as valid.
""",
        "starter": "def is_valid_ref(ref):\n    pass\n",
        "tests": '''
def test_good():
    "Accepts valid references"
    f = need("is_valid_ref")
    for r in ["RFI-0042", "RFI-0000", "RFI-9999"]:
        v, _ = capture(f, r)
        check(v is True, "is_valid_ref(%r) returned %r, expected True." % (r, v))

def test_bad():
    "Rejects everything else"
    f = need("is_valid_ref")
    for r in ["rfi-0042", "RFI-042", "RFI-00420", "RFI-00A2", "RFI0042", "NCR-0042", "", "RFI-", " RFI-0042"]:
        v, _ = capture(f, r)
        check(v is False, "is_valid_ref(%r) returned %r, expected False." % (r, v))
''',
        "solution": 'def is_valid_ref(ref):\n    return ref.startswith("RFI-") and len(ref) == 8 and ref[4:].isdigit()\n',
        "hints": [
            "Three things must all be true: it starts with `RFI-`, its total length is 8, and the part after the dash is digits.",
            '`ref[4:]` is everything after `RFI-`.',
        ],
    },
    {
        "id": "split-join",
        "title": "split and join",
        "kind": "code",
        "body": """
`split()` breaks a string into a list. With no argument it splits on any whitespace. Give it a separator to split on that instead:

```python
"a,b,,c".split(",")    # ['a', 'b', '', 'c']
"one two".split()      # ['one', 'two']
```

`join()` goes the other way. It's called on the **separator**, which surprises most people:

```python
" + ".join(["a", "b", "c"])   # 'a + b + c'
```

`join` only works on lists of strings. To join numbers, convert them first: `", ".join(str(n) for n in nums)`.

## Your task

Write `tidy_row(line)` that takes one line of a CSV file, splits it on commas, strips the spaces off each value, and joins them back together with `" | "` between them.

`tidy_row("  Sand , 12,  t ")` returns `"Sand | 12 | t"`.
""",
        "starter": "def tidy_row(line):\n    pass\n",
        "tests": '''
def test_values():
    "Splits, strips and re-joins"
    f = need("tidy_row")
    for line, want in [("  Sand , 12,  t ", "Sand | 12 | t"), ("a,b", "a | b"), ("solo", "solo"), ("x, ,y", "x |  | y")]:
        v, _ = capture(f, line)
        check(v == want, "tidy_row(%r) returned %r, expected %r." % (line, v, want))
''',
        "solution": 'def tidy_row(line):\n    parts = [p.strip() for p in line.split(",")]\n    return " | ".join(parts)\n',
        "hints": [
            '`line.split(",")` gives the pieces. Strip each one, using a loop or a comprehension.',
            '`" | ".join(parts)` puts them back together.',
        ],
    },
]
