CHAPTER = {
    "title": "Lists",
    "summary": "Ordered collections: indexing, slicing, changing, looping, and list comprehensions.",
}

LESSONS = [
    {
        "id": "list-basics",
        "title": "Making and reading lists",
        "kind": "code",
        "body": """
A **list** holds several values in order, inside square brackets:

```python
tools = ["drill", "level", "saw", "tape"]
```

Each item has a position called an **index**, and indexes start at **0**:

```python
print(tools[0])    # drill
print(tools[2])    # saw
print(tools[-1])   # tape  (negative counts from the end)
print(len(tools))  # 4
```

Asking for an index that doesn't exist, like `tools[4]` here, raises an `IndexError`.

## Your task

Using the `crew` list in the starter code, print three lines:

1. the first name
2. the last name (use a negative index, so it still works if the list changes)
3. how many people are in the list
""",
        "starter": 'crew = ["Omar", "Lina", "Sami", "Rana", "Yousef"]\n\n',
        "tests": '''
def test_lines():
    "Prints Omar, Yousef and 5"
    check(LINES == ["Omar", "Yousef", "5"], "Expected Omar, Yousef, 5 on three lines. Got:\\n" + OUTPUT)

def test_methods():
    "Uses [-1] and len()"
    check("[-1]" in CODE.replace(" ", ""), "Get the last name with crew[-1].")
    check("len(" in CODE, "Use len() for the count.")
''',
        "solution": 'crew = ["Omar", "Lina", "Sami", "Rana", "Yousef"]\n\nprint(crew[0])\nprint(crew[-1])\nprint(len(crew))\n',
        "hints": [
            "The first item is index 0.",
            "`print(crew[0])`, `print(crew[-1])`, `print(len(crew))`",
        ],
    },
    {
        "id": "slicing",
        "title": "Slicing",
        "kind": "quiz",
        "body": """
A **slice** grabs a section of a list and gives you a new list:

```python
n = [10, 20, 30, 40, 50]
n[1:3]    # [20, 30]   from index 1 up to (not including) 3
n[:2]     # [10, 20]   from the start
n[3:]     # [40, 50]   to the end
n[-2:]    # [40, 50]   the last two
n[::2]    # [10, 30, 50]  every second item
```

Same rule as `range()`: the stop index isn't included.
""",
        "question": "If `days = [\"Mon\", \"Tue\", \"Wed\", \"Thu\", \"Fri\"]`, what is `days[1:4]`?",
        "options": [
            '`["Mon", "Tue", "Wed", "Thu"]`',
            '`["Tue", "Wed", "Thu"]`',
            '`["Tue", "Wed", "Thu", "Fri"]`',
            '`["Tue", "Thu"]`',
        ],
        "answer": 1,
        "explain": "Index 1 is `Tue`, and the slice stops just before index 4 (`Fri`), giving Tue, Wed, Thu.",
    },
    {
        "id": "changing",
        "title": "Changing a list",
        "kind": "code",
        "body": """
Lists can be changed after they're made. The main tools:

| Code | Effect |
|---|---|
| `items.append(x)` | add `x` to the end |
| `items.insert(i, x)` | put `x` at index `i`, shifting the rest along |
| `items.remove(x)` | delete the first `x` found |
| `items.pop()` | remove and return the last item |
| `items.pop(i)` | remove and return the item at index `i` |
| `items[i] = x` | replace the item at index `i` |

These change the list **in place**. They don't make a new one.

## Your task

Here's a job queue. Apply these changes, in order, using the methods above:

1. Add `"inspect scaffold"` to the end.
2. Put `"safety briefing"` at the very front.
3. Remove `"order bricks"` (it's been cancelled).
4. Change `"paint wall"` to `"paint wall (2 coats)"`.

Then print the list. Don't just retype the whole list with the answer.
""",
        "starter": 'queue = ["order bricks", "fix door", "paint wall"]\n\n# your changes here\n\nprint(queue)\n',
        "tests": '''
WANT = ["safety briefing", "fix door", "paint wall (2 coats)", "inspect scaffold"]

def test_final():
    "The queue ends up in the right state"
    q = need("queue")
    check(q == WANT, "queue is %r\\nexpected %r" % (q, WANT))

def test_methods():
    "Uses append, insert and remove"
    for m in ("append(", "insert(", "remove("):
        check(m in CODE, "Use .%s) for one of the steps." % m[:-1])
''',
        "solution": 'queue = ["order bricks", "fix door", "paint wall"]\n\nqueue.append("inspect scaffold")\nqueue.insert(0, "safety briefing")\nqueue.remove("order bricks")\nqueue[queue.index("paint wall")] = "paint wall (2 coats)"\n\nprint(queue)\n',
        "hints": [
            "Step 2 is `queue.insert(0, ...)`. Step 3 is `queue.remove(...)`.",
            'After steps 1 to 3, `"paint wall"` is at index 2, so `queue[2] = "paint wall (2 coats)"` works. `queue.index("paint wall")` would find it for you.',
        ],
    },
    {
        "id": "loop-list-top",
        "title": "Going through a list",
        "kind": "code",
        "body": """
`for` works directly on a list. Each time round, the loop variable is the next item:

```python
loads = [12.5, 8, 20]
for load in loads:
    print(load, "kN")
# 12.5 kN
# 8 kN
# 20 kN
```

Compare that with the loops in the last chapter. `for i in range(3)` gave you numbers to count with. `for load in loads` gives you the items themselves, so you don't need an index at all.

If you do want a position number as well, `enumerate()` gives you both, starting from 0:

```python
for i, load in enumerate(loads):
    print(i, load)    # 0 12.5, then 1 8, then 2 20
```

## Your task

For the `loads` list in the starter, print one line per load in this format, then a final line with the total. Use a running total for the sum, like in the Loops chapter.

```
Load 1: 12.5 kN
Load 2: 8 kN
Load 3: 20 kN
Load 4: 4.5 kN
Total: 45.0 kN
```

The numbering starts at 1, so it's `i + 1` if you use `enumerate`.
""",
        "starter": "loads = [12.5, 8, 20, 4.5]\ntotal = 0\n\n# loop over loads: print each line and add the load to total\n\n\n# after the loop: print the total line\n",
        "tests": '''
def test_lines():
    "Prints each load, then the total"
    want = ["Load 1: 12.5 kN", "Load 2: 8 kN", "Load 3: 20 kN", "Load 4: 4.5 kN", "Total: 45.0 kN"]
    check(LINES == want, "Expected:\\n%s\\nGot:\\n%s" % ("\\n".join(want), OUTPUT))

def test_loop():
    "Uses a loop over the list"
    import ast
    fors = [n for n in ast.walk(ast.parse(RAW_CODE)) if isinstance(n, ast.For)]
    check(fors, "Use a for loop to go through loads.")
    check("45" not in CODE and "sum(" not in CODE, "Work out the total with a running total in the loop.")
''',
        "solution": 'loads = [12.5, 8, 20, 4.5]\ntotal = 0\n\nfor i, load in enumerate(loads):\n    print(f"Load {i + 1}: {load} kN")\n    total += load\n\nprint(f"Total: {total} kN")\n',
        "hints": [
            '`for i, load in enumerate(loads):` then `print(f"Load {i + 1}: {load} kN")` and `total += load`.',
            "The total line goes after the loop, at the left edge, so it prints once.",
        ],
    },
    {
        "id": "looping-lists",
        "title": "Looping over a list",
        "kind": "code",
        "body": """
Now the same thing inside a function that's handed a list. It's the running-total shape from the Loops chapter, with the list in place of `range()`:

```python
def total_length(bars):
    total = 0
    for b in bars:
        total += b
    return total
```

An empty list is falsy, so `if not numbers:` is a neat way to spot one before you divide by its length.

Python also has `sum()`, `min()` and `max()` built in, but writing the loop yourself once is worth it.

## Your task

Write `average(numbers)` that returns the mean of a list of numbers. Use a loop to add them up (not `sum()`).

If the list is empty, return `0` instead of crashing with a divide-by-zero.
""",
        "starter": "def average(numbers):\n    pass\n",
        "tests": '''
def test_values():
    "Correct averages"
    f = need("average")
    for nums, want in [([2, 4, 6], 4), ([5], 5), ([1, 2], 1.5), ([-3, 3, 9], 3)]:
        v, _ = capture(f, nums)
        check(v is not None and abs(v - want) < 1e-9, "average(%r) returned %r, expected %r." % (nums, v, want))

def test_empty():
    "Empty list gives 0"
    v, _ = capture(need("average"), [])
    check(v == 0, "average([]) returned %r, expected 0." % (v,))

def test_loop():
    "Adds up with a loop, not sum()"
    check("sum(" not in CODE, "Use a for loop to add up the numbers this time.")
''',
        "solution": "def average(numbers):\n    if not numbers:\n        return 0\n    total = 0\n    for n in numbers:\n        total += n\n    return total / len(numbers)\n",
        "hints": [
            "An empty list is falsy, so `if not numbers: return 0` handles that case.",
            "Running total in a loop, then `return total / len(numbers)`.",
        ],
    },
    {
        "id": "filtering",
        "title": "Building new lists",
        "kind": "code",
        "body": """
To make a new list from an old one, start with an empty list and `append` as you go:

```python
long_words = []
for w in ["a", "beam", "to", "column"]:
    if len(w) > 3:
        long_words.append(w)
# ['beam', 'column']
```

Python has a compact way to write exactly this, called a **list comprehension**:

```python
long_words = [w for w in words if len(w) > 3]
```

Read it as "w, for each w in words, if it's longer than 3". You can transform the items too:

```python
squares = [n * n for n in range(5)]   # [0, 1, 4, 9, 16]
```

Use whichever you find clearer. The loop version is never wrong.

## Your task

Write `over_limit(readings, limit)` that returns a **new** list of the readings that are strictly greater than `limit`, in their original order. Don't change the list you were given.
""",
        "starter": "def over_limit(readings, limit):\n    result = []\n    # loop over readings; append the ones above limit to result\n\n    return result\n",
        "tests": '''
def test_values():
    "Keeps only readings above the limit, in order"
    f = need("over_limit")
    v, _ = capture(f, [3, 9, 4, 12, 9, 15], 9)
    check(v == [12, 15], "over_limit([3, 9, 4, 12, 9, 15], 9) returned %r." % (v,))
    v, _ = capture(f, [1, 2], 5)
    check(v == [], "Nothing over the limit should give [], got %r." % (v,))

def test_no_change():
    "Doesn't change the original list"
    data = [5, 50, 6, 60]
    capture(need("over_limit"), data, 10)
    check(data == [5, 50, 6, 60], "The original list was changed to %r." % data)
''',
        "solution": "def over_limit(readings, limit):\n    return [r for r in readings if r > limit]\n",
        "hints": [
            "Make `result = []`, loop over `readings`, and `append` the ones where `r > limit`.",
            "One line: `return [r for r in readings if r > limit]`",
        ],
    },
    {
        "id": "sorting",
        "title": "Sorting",
        "kind": "code",
        "body": """
Two ways to sort:

```python
nums = [5, 2, 9]
print(sorted(nums))   # [2, 5, 9]   new list, nums unchanged
nums.sort()           # nums itself is now [2, 5, 9]
```

Both take `reverse=True` for largest first:

```python
sorted(nums, reverse=True)   # [9, 5, 2]
```

Combine sorting with slicing and you can grab the top few of anything.

## Your task

Write `top_three(scores)` that returns the three highest scores, highest first. If there are fewer than three scores, return all of them, highest first. Don't change the original list.
""",
        "starter": "def top_three(scores):\n    pass\n",
        "tests": '''
def test_values():
    "Returns the top three, highest first"
    f = need("top_three")
    for data, want in [([50, 90, 70, 85, 60], [90, 85, 70]), ([1, 1, 1, 1], [1, 1, 1]),
                       ([4, 9], [9, 4]), ([], [])]:
        v, _ = capture(f, list(data))
        check(v == want, "top_three(%r) returned %r, expected %r." % (data, v, want))

def test_no_change():
    "Doesn't change the original list"
    data = [3, 1, 2]
    capture(need("top_three"), data)
    check(data == [3, 1, 2], "The original list was changed to %r. Use sorted() instead of .sort()." % data)
''',
        "solution": "def top_three(scores):\n    return sorted(scores, reverse=True)[:3]\n",
        "hints": [
            "`sorted(..., reverse=True)` gives you a new list, biggest first.",
            "Slice off the first three with `[:3]`. Slicing past the end is fine, it just gives you what's there.",
        ],
    },
    {
        "id": "aliasing",
        "title": "Two names, one list",
        "kind": "quiz",
        "body": """
A variable doesn't hold a list. It points at one. So two variables can point at the **same** list:

```python
a = [1, 2]
b = a        # b points at the same list as a
```

To get a separate copy, use `a.copy()` or `a[:]` or `list(a)`.
""",
        "question": "What does this print?\n\n```python\na = [1, 2]\nb = a\nb.append(3)\nprint(a)\n```",
        "options": ["`[1, 2]`", "`[1, 2, 3]`", "`[3]`", "An error"],
        "answer": 1,
        "explain": "`a` and `b` are two names for one list, so appending through `b` changes what `a` sees as well. If `b` had been made with `b = a.copy()`, `a` would still be `[1, 2]`.",
    },
]
