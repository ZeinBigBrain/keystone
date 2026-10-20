CHAPTER = {
    "title": "Dictionaries, sets and tuples",
    "summary": "Looking things up by key, counting, removing duplicates, and fixed groups of values.",
}

LESSONS = [
    {
        "id": "dict-basics",
        "title": "Dictionaries",
        "kind": "code",
        "body": """
A **dictionary** (`dict`) stores pairs: a **key** and its **value**. You look values up by key instead of by position.

```python
stock = {"cement": 40, "sand": 12, "rebar": 0}

print(stock["sand"])     # 12
stock["gravel"] = 25     # add a new pair
stock["sand"] -= 2       # change a value
print(len(stock))        # 4
```

Asking for a key that isn't there raises a `KeyError`. Two safe ways round that:

```python
"tiles" in stock            # False, so check first
stock.get("tiles")          # None instead of an error
stock.get("tiles", 0)       # 0, a default of your choosing
```

## Your task

Write `quantity(stock, item)` that returns how many of `item` there are, or `0` if the item isn't in the dictionary at all.
""",
        "starter": "def quantity(stock, item):\n    pass\n\n\nstore = {\"cement\": 40, \"sand\": 12}\nprint(quantity(store, \"sand\"))\nprint(quantity(store, \"tiles\"))\n",
        "tests": '''
S = {"cement": 40, "sand": 12, "rebar": 0}

def test_present():
    "Returns the count for items that exist"
    f = need("quantity")
    for k in S:
        v, _ = capture(f, dict(S), k)
        check(v == S[k], "quantity(stock, %r) returned %r, expected %r." % (k, v, S[k]))

def test_missing():
    "Returns 0 for missing items"
    v, _ = capture(need("quantity"), dict(S), "tiles")
    check(v == 0, "quantity(stock, 'tiles') returned %r, expected 0." % (v,))
''',
        "solution": "def quantity(stock, item):\n    return stock.get(item, 0)\n\n\nstore = {\"cement\": 40, \"sand\": 12}\nprint(quantity(store, \"sand\"))\nprint(quantity(store, \"tiles\"))\n",
        "hints": [
            "`.get()` lets you give a default for missing keys.",
            "`return stock.get(item, 0)`",
        ],
    },
    {
        "id": "dict-loops",
        "title": "Looping over a dictionary",
        "kind": "code",
        "body": """
Looping over a dict gives you its keys. Use `.items()` to get each key and value together:

```python
prices = {"tea": 2, "coffee": 3}
for name, price in prices.items():
    print(name, price)
```

Dicts remember the order things were added. If you want a different order, sort the keys:

```python
for name in sorted(prices):
    print(name, prices[name])
```

## Your task

Write `print_stock(stock)` that prints one line per item, **in alphabetical order**, like this:

```
cement: 40
rebar: 0
sand: 12
```

It should print, not return.
""",
        "starter": "def print_stock(stock):\n    pass\n\n\nprint_stock({\"sand\": 12, \"cement\": 40, \"rebar\": 0})\n",
        "tests": '''
def test_output():
    "Prints every item alphabetically as 'name: qty'"
    _, out = capture(need("print_stock"), {"sand": 12, "cement": 40, "rebar": 0, "brick": 500})
    want = "brick: 500\\ncement: 40\\nrebar: 0\\nsand: 12"
    check(out.strip() == want, "Expected:\\n%s\\nGot:\\n%s" % (want, out.strip()))
''',
        "solution": 'def print_stock(stock):\n    for item in sorted(stock):\n        print(f"{item}: {stock[item]}")\n\n\nprint_stock({"sand": 12, "cement": 40, "rebar": 0})\n',
        "hints": [
            "`for item in sorted(stock):` goes through the keys alphabetically.",
            '`print(f"{item}: {stock[item]}")` inside the loop.',
        ],
    },
    {
        "id": "count-top",
        "title": "Counting with a dictionary",
        "kind": "code",
        "body": """
Dictionaries are the natural way to count things. For each item: if it's new, start it at 1; otherwise add 1.

```python
counts = {}
for colour in ["red", "blue", "red"]:
    counts[colour] = counts.get(colour, 0) + 1
print(counts)
# {'red': 2, 'blue': 1}
```

Take that middle line slowly, right to left:

1. `counts.get(colour, 0)` looks up the count so far, or gives 0 if this colour hasn't been seen yet.
2. `+ 1` adds this one.
3. `counts[colour] = ...` stores the new count back under that key.

It's the running-total idea again, just with one total per key instead of a single number.

> **Common slip:** `counts[colour] += 1` on its own crashes with a `KeyError` the first time a colour turns up, because there's nothing there yet to add to. The `.get(..., 0)` version handles that.

## Your task

The starter has a list of materials, one entry per delivery. Count how many deliveries there were of each material into a dict called `counts`, then print it.
""",
        "starter": 'deliveries = ["sand", "cement", "sand", "rebar", "sand", "cement"]\ncounts = {}\n\n# loop over deliveries and count each one into counts\n\n\nprint(counts)\n',
        "tests": '''
def test_counts():
    "counts holds the right totals"
    c = need("counts")
    want = {"sand": 3, "cement": 2, "rebar": 1}
    check(c == want, "counts is %r, expected %r." % (c, want))

def test_loop():
    "Counts with a loop, not by typing the numbers"
    check("for " in CODE and ": 3" not in CODE, "Build counts with a loop over deliveries.")
''',
        "solution": 'deliveries = ["sand", "cement", "sand", "rebar", "sand", "cement"]\ncounts = {}\n\nfor item in deliveries:\n    counts[item] = counts.get(item, 0) + 1\n\nprint(counts)\n',
        "hints": [
            "`for item in deliveries:` and one line inside the loop.",
            "`counts[item] = counts.get(item, 0) + 1`",
        ],
    },
    {
        "id": "counting",
        "title": "Counting words",
        "kind": "code",
        "body": """
Now the same counting pattern inside a function, working on text.

```python
def letter_counts(word):
    counts = {}                     # inside the function
    for ch in word:
        counts[ch] = counts.get(ch, 0) + 1
    return counts                   # after the loop
```

You'll need to break text into words for this task. `"the cat sat".split()` gives `['the', 'cat', 'sat']`, and `.lower()` turns text to lowercase.

## Your task

Write `word_counts(text)` that returns a dict of how many times each word appears. Treat words the same regardless of case, so `"The"` and `"the"` both count as `"the"`.
""",
        "starter": "def word_counts(text):\n    pass\n",
        "tests": '''
def test_simple():
    "Counts each word"
    v, _ = capture(need("word_counts"), "go stop go go")
    check(v == {"go": 3, "stop": 1}, "word_counts('go stop go go') returned %r." % (v,))

def test_case():
    "Ignores upper and lower case"
    v, _ = capture(need("word_counts"), "The cat and THE dog and the bird")
    want = {"the": 3, "cat": 1, "and": 2, "dog": 1, "bird": 1}
    check(v == want, "Got %r\\nexpected %r" % (v, want))

def test_empty():
    "Empty text gives an empty dict"
    v, _ = capture(need("word_counts"), "")
    check(v == {}, "word_counts('') returned %r." % (v,))
''',
        "solution": "def word_counts(text):\n    counts = {}\n    for word in text.lower().split():\n        counts[word] = counts.get(word, 0) + 1\n    return counts\n",
        "hints": [
            "Loop over `text.lower().split()`.",
            "`counts[word] = counts.get(word, 0) + 1` inside the loop, and return `counts` at the end.",
        ],
    },
    {
        "id": "records-quiz",
        "title": "Reading nested data",
        "kind": "quiz",
        "body": """
When a list holds dictionaries, you reach in one step at a time: first a position in the list, then a key in the dict you land on.

```python
staff = [
    {"name": "Hana", "years": 6},
    {"name": "Karim", "years": 2},
]
staff[0]            # {'name': 'Hana', 'years': 6}
staff[0]["name"]    # 'Hana'
```

Read `staff[0]["name"]` left to right: take the list, go to item 0, then look up `"name"` in it.
""",
        "question": "Using the `staff` list above, what is `staff[1][\"years\"] + staff[0][\"years\"]`?",
        "options": ["`8`", "`\"26\"`", "`KeyError`", "`2`"],
        "answer": 0,
        "explain": "`staff[1][\"years\"]` is Karim's 2 and `staff[0][\"years\"]` is Hana's 6. Both are numbers, so they add to 8.",
    },
    {
        "id": "records",
        "title": "Lists of dictionaries",
        "kind": "code",
        "body": """
Real data is often a list of records, each one a dict with the same keys. It's basically a table: each dict is a row, each key a column.

```python
staff = [
    {"name": "Hana", "role": "engineer", "years": 6},
    {"name": "Karim", "role": "planner", "years": 2},
]

for person in staff:
    print(person["name"], "-", person["role"])
```

Inside a function, collecting matching names uses the same "start an empty list, append, return after the loop" shape you used for `over_limit`:

```python
def engineers(staff):
    names = []
    for p in staff:
        if p["role"] == "engineer":
            names.append(p["name"])
    return names
```

## Your task

Write `senior_names(staff, min_years)` that returns a list of the **names** of everyone with at least `min_years` of experience, sorted alphabetically.
""",
        "starter": "def senior_names(staff, min_years):\n    pass\n",
        "tests": '''
STAFF = [
    {"name": "Hana", "role": "engineer", "years": 6},
    {"name": "Karim", "role": "planner", "years": 2},
    {"name": "Dina", "role": "surveyor", "years": 9},
    {"name": "Adel", "role": "engineer", "years": 5},
]

def test_values():
    "Names of people with enough years, alphabetical"
    f = need("senior_names")
    v, _ = capture(f, STAFF, 5)
    check(v == ["Adel", "Dina", "Hana"], "senior_names(staff, 5) returned %r." % (v,))
    v, _ = capture(f, STAFF, 10)
    check(v == [], "senior_names(staff, 10) returned %r, expected []." % (v,))
    v, _ = capture(f, STAFF, 0)
    check(v == ["Adel", "Dina", "Hana", "Karim"], "senior_names(staff, 0) returned %r." % (v,))
''',
        "solution": 'def senior_names(staff, min_years):\n    return sorted(p["name"] for p in staff if p["years"] >= min_years)\n',
        "hints": [
            'Loop over `staff`. For each `p`, if `p["years"] >= min_years`, append `p["name"]` to a list.',
            "Return `sorted(...)` of that list.",
        ],
    },
    {
        "id": "tuples",
        "title": "Tuples",
        "kind": "quiz",
        "body": """
A **tuple** is like a list that can't be changed. It uses round brackets:

```python
point = (3, 4)
print(point[0])   # 3
```

Use a tuple for a small, fixed group of values that belong together, like a coordinate or an RGB colour.

You can **unpack** a tuple straight into variables:

```python
x, y = point
```

That's also how functions return more than one value. `return a, b` actually returns the tuple `(a, b)`, and the caller can unpack it with `q, r = divmod(17, 5)`.
""",
        "question": "What happens here?\n\n```python\nsize = (1200, 800)\nsize[0] = 1500\n```",
        "options": [
            "`size` becomes `(1500, 800)`",
            "`size` becomes `(1500, 1200, 800)`",
            "Python raises a `TypeError`",
            "Nothing happens, the line is ignored",
        ],
        "answer": 2,
        "explain": "Tuples can't be changed once made, so assigning to `size[0]` raises `TypeError: 'tuple' object does not support item assignment`. To \"change\" it you'd build a new tuple: `size = (1500, size[1])`.",
    },
    {
        "id": "sets",
        "title": "Sets",
        "kind": "code",
        "body": """
A **set** is an unordered collection with **no duplicates**. Curly brackets, but no colons:

```python
seen = {"Ali", "Mona", "Ali"}
print(seen)        # {'Ali', 'Mona'}
print(len(seen))   # 2
```

The quickest way to remove duplicates from a list is `set(my_list)`. Checking `x in some_set` is also very fast, even with millions of items.

Sets support maths-style operations:

```python
a = {1, 2, 3}
b = {2, 3, 4}
a & b    # {2, 3}       in both
a | b    # {1, 2, 3, 4} in either
a - b    # {1}          in a but not b
```

One trap: `{}` makes an empty **dict**, not an empty set. Use `set()` for that.

## Your task

Write two functions:

1. `unique_count(names)` returns how many different names are in the list.
2. `on_both(list_a, list_b)` returns a **sorted list** of the names that appear in both lists, each name once.
""",
        "starter": "def unique_count(names):\n    pass\n\n\ndef on_both(list_a, list_b):\n    pass\n",
        "tests": '''
def test_unique():
    "unique_count ignores repeats"
    f = need("unique_count")
    for data, want in [(["a", "b", "a", "c", "b"], 3), ([], 0), (["x"] * 5, 1)]:
        v, _ = capture(f, data)
        check(v == want, "unique_count(%r) returned %r, expected %d." % (data, v, want))

def test_both():
    "on_both gives a sorted list of shared names"
    f = need("on_both")
    v, _ = capture(f, ["Sara", "Tom", "Ali", "Tom"], ["Tom", "Zed", "Ali", "Ali"])
    check(v == ["Ali", "Tom"], "Got %r, expected ['Ali', 'Tom']." % (v,))
    v, _ = capture(f, ["a"], ["b"])
    check(v == [], "No overlap should give [], got %r." % (v,))
''',
        "solution": "def unique_count(names):\n    return len(set(names))\n\n\ndef on_both(list_a, list_b):\n    return sorted(set(list_a) & set(list_b))\n",
        "hints": [
            "`len(set(names))` for the first one.",
            "Turn both lists into sets, use `&`, then `sorted()` the result.",
        ],
    },
]
