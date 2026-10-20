CHAPTER = {
    "title": "NumPy arrays",
    "summary": "Arrays instead of lists: creating them, shape and type, indexing, maths on whole arrays, and masks.",
}

T = 30

LESSONS = [
    {
        "id": "arrays",
        "title": "Lists versus arrays",
        "kind": "code",
        "timeout": T,
        "body": """
A NumPy **array** looks like a list, but maths on it works on **every element at once**:

```python
import numpy as np

loads = np.array([12.5, 8.0, 20.0])
print(loads * 1.5)      # [18.75 12.   30.  ]   every load factored
print(loads + 2)        # [14.5 10.  22. ]
```

With a list you'd need a loop for that. With an array it's one line, and for big arrays it's also hundreds of times faster, because the loop runs inside NumPy's compiled code.

`np.array(some_list)` turns a list into an array.

## Your task

The starter has a list of spans in metres. Make an array from it called `spans_m`, then make `spans_mm` by converting every span to millimetres (times 1000). Print `spans_mm`.
""",
        "starter": "import numpy as np\n\nspans = [4.5, 6.0, 7.2, 3.8]\n\n# spans_m = an array made from spans\n\n# spans_mm = spans_m converted to mm\n\n",
        "tests": '''
import numpy as np

def test_arrays():
    "spans_m and spans_mm are arrays with the right values"
    a = need("spans_m")
    check(isinstance(a, np.ndarray), "spans_m should be a NumPy array. Use np.array(spans).")
    b = need("spans_mm")
    check(isinstance(b, np.ndarray), "spans_mm should be an array too. Multiply the array, not the list.")
    check(np.allclose(b, [4500, 6000, 7200, 3800]), "spans_mm is %r, expected [4500, 6000, 7200, 3800]." % (b,))

def test_no_loop():
    "No loop needed"
    check("for " not in CODE, "Multiply the whole array at once instead of looping.")
''',
        "solution": "import numpy as np\n\nspans = [4.5, 6.0, 7.2, 3.8]\n\nspans_m = np.array(spans)\nspans_mm = spans_m * 1000\nprint(spans_mm)\n",
        "hints": [
            "`spans_m = np.array(spans)`",
            "`spans_mm = spans_m * 1000`",
        ],
    },
    {
        "id": "list-quiz",
        "title": "Same maths, different answer",
        "kind": "quiz",
        "body": "Lists and arrays look alike, which is exactly why this catches people.",
        "question": "What do these two lines print?\n\n```python\nprint([1, 2] * 2)\nprint(np.array([1, 2]) * 2)\n```",
        "options": [
            "`[2, 4]` and `[2 4]`",
            "`[1, 2, 1, 2]` and `[2 4]`",
            "`[1, 2, 1, 2]` twice",
            "An error for the list",
        ],
        "answer": 1,
        "explain": "`*` on a list repeats it, so you get `[1, 2, 1, 2]`. On an array it multiplies each element, giving `[2 4]`. (Arrays print without commas, which is a quick way to tell them apart.)",
    },
    {
        "id": "shape",
        "title": "Shape and type",
        "kind": "code",
        "timeout": T,
        "body": """
Arrays can have more than one dimension. A list of lists becomes a 2D array, like a table:

```python
loads = np.array([
    [120, 135, 118, 140],    # floor 1, four columns
    [ 95, 110,  98, 105],    # floor 2
    [ 60,  72,  65,  70],    # floor 3
])
print(loads.shape)   # (3, 4): 3 rows, 4 columns
print(loads.size)    # 12 values in total
print(loads.ndim)    # 2 dimensions
print(loads.dtype)   # int64: every value is a whole number
```

Every value in an array has the **same type** (the `dtype`). Mix whole numbers and decimals and they all become floats.

`.shape` is a tuple, so you can unpack it: `rows, cols = loads.shape`.

## Your task

For the `readings` array in the starter, store:

- `rows` and `cols`: its number of rows and columns (unpack `.shape`)
- `total`: how many values it holds
""",
        "starter": "import numpy as np\n\nreadings = np.array([\n    [0.12, 0.15, 0.11],\n    [0.31, 0.29, 0.33],\n    [0.52, 0.48, 0.50],\n    [0.70, 0.74, 0.69],\n    [0.91, 0.88, 0.93],\n])\n\n# rows, cols = ...\n# total = ...\n",
        "tests": '''
def test_shape():
    "rows, cols and total are right"
    check(need("rows") == 5 and need("cols") == 3, "rows and cols should be 5 and 3. Got %r and %r." % (ns.get("rows"), ns.get("cols")))
    check(need("total") == 15, "total should be 15 (5 x 3). Got %r." % ns.get("total"))
    check("shape" in CODE and ("size" in CODE or "rows * cols" in CODE.replace(" ", "").replace("rows*cols", "rows * cols")), "Get the numbers from the array's shape and size rather than counting by hand.")
''',
        "solution": "import numpy as np\n\nreadings = np.array([\n    [0.12, 0.15, 0.11],\n    [0.31, 0.29, 0.33],\n    [0.52, 0.48, 0.50],\n    [0.70, 0.74, 0.69],\n    [0.91, 0.88, 0.93],\n])\n\nrows, cols = readings.shape\ntotal = readings.size\nprint(rows, cols, total)\n",
        "hints": [
            "`rows, cols = readings.shape`",
            "`total = readings.size`",
        ],
    },
    {
        "id": "index-1d",
        "title": "Indexing and slicing",
        "kind": "code",
        "timeout": T,
        "body": """
A 1D array indexes and slices exactly like a list:

```python
r = np.array([3.1, 3.4, 3.9, 4.6, 5.2, 5.1])
r[0]      # 3.1   first
r[-1]     # 5.1   last
r[2:5]    # [3.9 4.6 5.2]   index 2 up to (not including) 5
r[::2]    # [3.1 3.9 5.2]   every second value
```

## Your task

The starter has hourly settlement readings. Store:

- `first` and `last`: the first and last readings
- `middle`: the readings from index 3 up to and including index 6, as an array
""",
        "starter": "import numpy as np\n\nsettlement = np.array([0.0, 0.4, 0.9, 1.3, 1.6, 1.8, 2.1, 2.2, 2.3])\n\n# first = ...\n# last = ...\n# middle = ...\n",
        "tests": '''
import numpy as np

def test_ends():
    "first and last"
    check(need("first") == 0.0 and need("last") == 2.3, "first and last should be 0.0 and 2.3, got %r and %r." % (ns.get("first"), ns.get("last")))
    check("[-1]" in CODE.replace(" ", ""), "Use a negative index for the last value.")

def test_middle():
    "middle is indexes 3 to 6"
    m = need("middle")
    check(isinstance(m, np.ndarray) and np.allclose(m, [1.3, 1.6, 1.8, 2.1]),
          "middle is %r, expected [1.3 1.6 1.8 2.1]. The stop index isn't included, so to include 6 you stop at 7." % (m,))
''',
        "solution": "import numpy as np\n\nsettlement = np.array([0.0, 0.4, 0.9, 1.3, 1.6, 1.8, 2.1, 2.2, 2.3])\n\nfirst = settlement[0]\nlast = settlement[-1]\nmiddle = settlement[3:7]\nprint(first, last, middle)\n",
        "hints": [
            "`settlement[0]` and `settlement[-1]`.",
            "Up to and including index 6 means the slice stops at 7: `settlement[3:7]`.",
        ],
    },
    {
        "id": "index-2d",
        "title": "Rows and columns",
        "kind": "code",
        "timeout": T,
        "body": """
A 2D array takes **two** indexes in one pair of brackets: row first, then column.

```python
loads = np.array([
    [120, 135, 118, 140],
    [ 95, 110,  98, 105],
    [ 60,  72,  65,  70],
])
loads[1, 2]    # 98: row 1, column 2
loads[0]       # [120 135 118 140]: the whole first row
loads[:, 3]    # [140 105  70]: every row, column 3
```

`:` on its own means "all of them". So `loads[:, 3]` reads "all rows, column 3", which is one column of the table.

> **Common slip:** `loads[1][2]` also works, but `loads[:][3]` does **not** give column 3. `loads[:]` is the whole array, and `[3]` then asks for row 3. Always use the comma form.

## Your task

Using the `loads` array from the starter (rows are floors, columns are column lines A to D), store:

- `b_floor2`: the load in column B (index 1) on floor 2 (index 1)
- `floor3`: the whole of floor 3 (index 2)
- `line_d`: column D (index 3) on every floor
""",
        "starter": "import numpy as np\n\nloads = np.array([\n    [120, 135, 118, 140],\n    [ 95, 110,  98, 105],\n    [ 60,  72,  65,  70],\n])\n\n# b_floor2 = ...\n# floor3 = ...\n# line_d = ...\n",
        "tests": '''
import numpy as np

def test_values():
    "Picks out the right parts"
    check(need("b_floor2") == 110, "b_floor2 should be 110 (row 1, column 1). Got %r." % ns.get("b_floor2"))
    check(np.array_equal(need("floor3"), [60, 72, 65, 70]), "floor3 should be row 2: [60 72 65 70]. Got %r." % (ns.get("floor3"),))
    check(np.array_equal(need("line_d"), [140, 105, 70]), "line_d should be column 3 of every row: [140 105 70]. Got %r. Use loads[:, 3]." % (ns.get("line_d"),))
''',
        "solution": "import numpy as np\n\nloads = np.array([\n    [120, 135, 118, 140],\n    [ 95, 110,  98, 105],\n    [ 60,  72,  65,  70],\n])\n\nb_floor2 = loads[1, 1]\nfloor3 = loads[2]\nline_d = loads[:, 3]\nprint(b_floor2, floor3, line_d)\n",
        "hints": [
            "`loads[1, 1]`, `loads[2]` and `loads[:, 3]`.",
        ],
    },
    {
        "id": "vector-maths",
        "title": "Maths on whole arrays",
        "kind": "code",
        "timeout": T,
        "body": """
When two arrays are the same shape, maths between them works **element by element**: first with first, second with second.

```python
force_kn = np.array([250, 410, 180])
area_mm2 = np.array([2500, 3200, 1600])
stress = force_kn * 1000 / area_mm2     # N/mm2 for each member
# [100.  128.125 112.5]
```

NumPy also has maths functions that work on whole arrays: `np.sqrt`, `np.sin`, `np.abs`, `np.round(x, 2)` and more. And summary methods:

```python
stress.max()     # 128.125
stress.mean()    # 113.54...
stress.argmax()  # 1: the index of the biggest one
```

## Your task

Work out the second moment of area of four rectangular sections: `b * h**3 / 12`. Store it in `I_mm4` (one value per section). Then store `stiffest`, the **index** of the section with the biggest `I_mm4`.
""",
        "starter": "import numpy as np\n\nb_mm = np.array([200, 250, 300, 200])\nh_mm = np.array([400, 450, 400, 500])\n\n# I_mm4 = ...\n# stiffest = ...\n",
        "tests": '''
import numpy as np

def test_I():
    "Second moments of area"
    I = need("I_mm4")
    b, h = np.array([200, 250, 300, 200]), np.array([400, 450, 400, 500])
    check(isinstance(I, np.ndarray) and np.allclose(I, b * h ** 3 / 12), "I_mm4 is %r. It should be b * h**3 / 12 for each section." % (I,))

def test_stiffest():
    "stiffest is the index of the biggest"
    check(need("stiffest") == 3, "stiffest should be 3. Got %r. .argmax() gives the index." % ns.get("stiffest"))
    check("for " not in CODE, "No loop needed: work on the whole arrays.")
''',
        "solution": "import numpy as np\n\nb_mm = np.array([200, 250, 300, 200])\nh_mm = np.array([400, 450, 400, 500])\n\nI_mm4 = b_mm * h_mm ** 3 / 12\nstiffest = I_mm4.argmax()\nprint(I_mm4, stiffest)\n",
        "hints": [
            "`I_mm4 = b_mm * h_mm ** 3 / 12`",
            "`stiffest = I_mm4.argmax()`",
        ],
    },
    {
        "id": "axis-quiz",
        "title": "Which way is axis=0?",
        "kind": "quiz",
        "body": """
On a 2D array, `.sum()`, `.mean()`, `.max()` and friends take an `axis`:

- no axis: one answer for the whole array
- `axis=0`: work **down** the rows, giving one answer per column
- `axis=1`: work **across** the columns, giving one answer per row

A way to remember it: the axis you name is the one that disappears.
""",
        "question": "`loads` has shape `(3, 4)`: 3 floors, 4 columns. What shape is `loads.sum(axis=0)`?",
        "options": ["`(3,)`, one total per floor", "`(4,)`, one total per column", "A single number", "`(3, 4)`, unchanged"],
        "answer": 1,
        "explain": "`axis=0` adds down the rows, so the 3 floors collapse into one total for each of the 4 columns. To get one total per floor, use `axis=1`.",
    },
    {
        "id": "axis",
        "title": "Totals along an axis",
        "kind": "code",
        "timeout": T,
        "body": """
```python
loads = np.array([
    [120, 135, 118, 140],
    [ 95, 110,  98, 105],
    [ 60,  72,  65,  70],
])
loads.sum(axis=0)   # [275 317 281 315]  one per column
loads.sum(axis=1)   # [513 408 267]      one per floor
loads.sum()         # 1188               everything
```

## Your task

Using the same `loads` array, store:

- `column_totals`: the total load on each column line, summed over all floors
- `floor_max`: the biggest column load on each floor
""",
        "starter": "import numpy as np\n\nloads = np.array([\n    [120, 135, 118, 140],\n    [ 95, 110,  98, 105],\n    [ 60,  72,  65,  70],\n])\n\n# column_totals = ...\n# floor_max = ...\n",
        "tests": '''
import numpy as np

def test_values():
    "Right totals and maxima"
    ct, fm = need("column_totals"), need("floor_max")
    check(np.array_equal(ct, [275, 317, 281, 315]), "column_totals is %r. One total per column means axis=0." % (ct,))
    check(np.array_equal(fm, [140, 110, 72]), "floor_max is %r. One answer per floor means axis=1." % (fm,))
''',
        "solution": "import numpy as np\n\nloads = np.array([\n    [120, 135, 118, 140],\n    [ 95, 110,  98, 105],\n    [ 60,  72,  65,  70],\n])\n\ncolumn_totals = loads.sum(axis=0)\nfloor_max = loads.max(axis=1)\nprint(column_totals, floor_max)\n",
        "hints": [
            "`loads.sum(axis=0)` and `loads.max(axis=1)`.",
        ],
    },
    {
        "id": "masks",
        "title": "Boolean masks",
        "kind": "code",
        "timeout": T,
        "body": """
Compare an array with a number and you get an array of `True` and `False`, one per element. That's a **mask**:

```python
stress = np.array([180, 260, 240, 310, 150])
over = stress > 250
print(over)             # [False  True False  True False]
```

Put a mask inside the square brackets and you get only the elements where it's `True`:

```python
print(stress[over])     # [260 310]
print(over.sum())       # 2: True counts as 1, so this counts them
```

Combine masks with `&` (and) and `|` (or), with each comparison in brackets:

```python
middling = stress[(stress > 160) & (stress < 300)]
```

> **Common slip:** `and` / `or` don't work on arrays (you get "truth value of an array is ambiguous"). Use `&` and `|`, and always bracket each side.

## Your task

The steel's design strength is 275 N/mm2. From the `stress` array, store:

- `failing`: an array of only the stresses **above** 275
- `n_failing`: how many there are
""",
        "starter": "import numpy as np\n\nstress = np.array([182, 291, 240, 310, 150, 275, 268, 302])\n\n# failing = ...\n# n_failing = ...\n",
        "tests": '''
import numpy as np

def test_values():
    "Only the stresses over 275, and the count"
    f = need("failing")
    check(isinstance(f, np.ndarray) and np.array_equal(f, [291, 310, 302]), "failing is %r, expected [291 310 302]. 275 itself isn't above 275." % (f,))
    check(need("n_failing") == 3, "n_failing should be 3, got %r." % ns.get("n_failing"))
    check("for " not in CODE, "Use a mask rather than a loop.")
''',
        "solution": "import numpy as np\n\nstress = np.array([182, 291, 240, 310, 150, 275, 268, 302])\n\nfailing = stress[stress > 275]\nn_failing = (stress > 275).sum()\nprint(failing, n_failing)\n",
        "hints": [
            "`failing = stress[stress > 275]`",
            "`n_failing = (stress > 275).sum()`, or `len(failing)`.",
        ],
    },
    {
        "id": "numpy-task",
        "title": "Chapter task: utilisation check",
        "kind": "code",
        "timeout": T,
        "body": """
This chapter's tools together, inside a function.

**Utilisation** is demand divided by capacity. Over 1.0 means the member fails.

```python
def summary(values, limit):
    over = values > limit
    return values.max(), over.sum()
```

## Your task

Write `check_members(demand, capacity)`. Both arguments are arrays of the same length. Return a tuple of three things:

1. the array of utilisations (demand / capacity), rounded to 3 decimal places with `np.round`
2. how many members fail (utilisation over 1.0)
3. the **index** of the worst member (highest utilisation)
""",
        "starter": "import numpy as np\n\n\ndef check_members(demand, capacity):\n    pass\n\n\nd = np.array([120.0, 340.0, 95.0, 410.0])\nc = np.array([150.0, 320.0, 200.0, 400.0])\nprint(check_members(d, c))\n",
        "tests": '''
import numpy as np

def test_values():
    "Utilisations, fail count and worst index"
    f = need("check_members")
    d = np.array([120.0, 340.0, 95.0, 410.0]); c = np.array([150.0, 320.0, 200.0, 400.0])
    v, _ = capture(f, d, c)
    check(isinstance(v, tuple) and len(v) == 3, "Return three things as a tuple: return util, n_fail, worst. Got %r." % (v,))
    util, n, worst = v
    check(np.allclose(util, np.round(d / c, 3)), "Utilisations are %r, expected %r." % (util, np.round(d / c, 3)))
    check(n == 2, "2 members fail, you returned %r." % (n,))
    check(worst == 1, "The worst member is index 1 (340 / 320). You returned %r." % (worst,))

def test_other():
    "Works on other data"
    d = np.array([10.0, 20.0, 30.0]); c = np.array([100.0, 100.0, 100.0])
    util, n, worst = need("check_members")(d, c)
    check(n == 0 and worst == 2, "For utilisations 0.1, 0.2, 0.3 expected 0 failures and worst index 2, got %r and %r." % (n, worst))
''',
        "solution": "import numpy as np\n\n\ndef check_members(demand, capacity):\n    util = np.round(demand / capacity, 3)\n    n_fail = (util > 1.0).sum()\n    worst = util.argmax()\n    return util, n_fail, worst\n\n\nd = np.array([120.0, 340.0, 95.0, 410.0])\nc = np.array([150.0, 320.0, 200.0, 400.0])\nprint(check_members(d, c))\n",
        "hints": [
            "`util = np.round(demand / capacity, 3)`",
            "`(util > 1.0).sum()` counts failures and `util.argmax()` finds the worst. `return util, n_fail, worst`.",
        ],
    },
]
