CHAPTER = {
    "title": "pandas basics",
    "summary": "DataFrames and Series, selecting columns, calculated columns, filtering, loc and iloc, and sorting.",
}

T = 30

BEAMS = '''import pandas as pd

beams = pd.DataFrame({
    "name": ["B1", "B2", "B3", "B4", "B5"],
    "span_m": [4.5, 6.0, 7.2, 3.8, 5.5],
    "load_kn_m": [12.0, 8.5, 15.0, 20.0, 11.0],
})
'''

LESSONS = [
    {
        "id": "pandas-what",
        "title": "Tables in Python",
        "kind": "read",
        "body": """
**pandas** gives Python a table type, the **DataFrame**. If you've done the SQL track, think of it as a table you can hold in a variable. If not, think of a spreadsheet tab that you work on with code instead of clicks.

```
  name  span_m  load_kn_m
0   B1     4.5       12.0
1   B2     6.0        8.5
2   B3     7.2       15.0
```

- Each **column** has a name and holds one kind of value. A single column on its own is a **Series**.
- The numbers down the left are the **index**: a label for each row. By default it's 0, 1, 2 ..., but it can be anything, like the beam names.

Under the hood every column is a NumPy array, so everything from the last two chapters (maths on whole columns, masks, `.max()`, `.mean()`) works the same way.

Why not just use Excel? For a one-off look, Excel is fine. pandas pays off when the job repeats: next month's data drops in, you rerun the script, and every step happens the same way, with nothing missed and nothing pasted into the wrong cell.
""",
    },
    {
        "id": "dataframe",
        "title": "Making a DataFrame",
        "kind": "code",
        "timeout": T,
        "body": """
The quickest way to make one by hand is a dictionary: each key is a column name, each value is a list of that column's values.

```python
import pandas as pd

columns = pd.DataFrame({
    "ref": ["C1", "C2", "C3"],
    "height_m": [3.2, 3.2, 4.0],
})
print(columns)
print(columns.shape)     # (3, 2): rows, columns
```

All the lists must be the same length, one value per row.

Most of the time your data will come from a CSV or Excel file instead (that's the next chapter), but building small ones by hand is the best way to learn.

## Your task

Make a DataFrame called `beams` with three columns:

| name | span_m | load_kn_m |
|---|---|---|
| B1 | 4.5 | 12.0 |
| B2 | 6.0 | 8.5 |
| B3 | 7.2 | 15.0 |

Then print it.
""",
        "starter": "import pandas as pd\n\n# beams = pd.DataFrame({...})\n",
        "tests": '''
import pandas as pd

def test_frame():
    "beams has the right columns and values"
    b = need("beams")
    check(isinstance(b, pd.DataFrame), "beams should be a DataFrame made with pd.DataFrame({...}).")
    check(list(b.columns) == ["name", "span_m", "load_kn_m"], "Columns are %r, expected name, span_m, load_kn_m in that order." % list(b.columns))
    check(b["name"].tolist() == ["B1", "B2", "B3"] and b["span_m"].tolist() == [4.5, 6.0, 7.2] and b["load_kn_m"].tolist() == [12.0, 8.5, 15.0],
          "Some values don't match the table.")
''',
        "solution": BEAMS.replace('"B1", "B2", "B3", "B4", "B5"', '"B1", "B2", "B3"').replace("4.5, 6.0, 7.2, 3.8, 5.5", "4.5, 6.0, 7.2").replace("12.0, 8.5, 15.0, 20.0, 11.0", "12.0, 8.5, 15.0") + "print(beams)\n",
        "hints": [
            "Three keys: `\"name\"`, `\"span_m\"` and `\"load_kn_m\"`, each with a list of three values.",
        ],
    },
    {
        "id": "select-columns",
        "title": "Selecting columns",
        "kind": "code",
        "timeout": T,
        "body": """
Square brackets with a column name give you that column as a **Series**. Square brackets with a **list** of names give you a smaller DataFrame:

```python
beams["span_m"]                 # one column: a Series
beams[["name", "span_m"]]       # two columns: a DataFrame (note the double brackets)
beams["span_m"].max()           # 7.2
beams["span_m"].tolist()        # [4.5, 6.0, 7.2, 3.8, 5.5], a plain list
```

The double brackets aren't special syntax: the outer pair is "select", and the inner pair is an ordinary Python list of names.

## Your task

From the `beams` table in the starter, store:

- `spans`: the `span_m` column (a Series)
- `longest`: the longest span
- `summary`: a DataFrame with just the `name` and `load_kn_m` columns, in that order
""",
        "starter": BEAMS + "\n# spans = ...\n# longest = ...\n# summary = ...\n",
        "tests": '''
import pandas as pd

def test_values():
    "spans, longest and summary"
    s = need("spans")
    check(isinstance(s, pd.Series) and s.tolist() == [4.5, 6.0, 7.2, 3.8, 5.5], "spans should be the span_m column: beams[\\"span_m\\"].")
    check(need("longest") == 7.2, "longest should be 7.2, got %r." % ns.get("longest"))
    sm = need("summary")
    check(isinstance(sm, pd.DataFrame) and list(sm.columns) == ["name", "load_kn_m"],
          "summary should be a DataFrame with columns name and load_kn_m. Use double brackets: beams[[\\"name\\", \\"load_kn_m\\"]].")
''',
        "solution": BEAMS + "\nspans = beams[\"span_m\"]\nlongest = spans.max()\nsummary = beams[[\"name\", \"load_kn_m\"]]\nprint(summary)\n",
        "hints": [
            "`spans = beams[\"span_m\"]` and `longest = spans.max()`.",
            "`summary = beams[[\"name\", \"load_kn_m\"]]`",
        ],
    },
    {
        "id": "brackets-quiz",
        "title": "One bracket or two?",
        "kind": "quiz",
        "body": "Quick check on the last lesson.",
        "question": "What does `beams[\"name\", \"span_m\"]` (single brackets, two names) do?",
        "options": [
            "Returns the two columns",
            "Returns the first matching column",
            "Raises a `KeyError`, because it looks for one column called (\"name\", \"span_m\")",
            "Returns the first two rows",
        ],
        "answer": 2,
        "explain": "With single brackets, the two names become a tuple, and pandas looks for one column with that tuple as its name. There isn't one, so you get a `KeyError`. To select several columns, pass a list: `beams[[\"name\", \"span_m\"]]`.",
    },
    {
        "id": "new-column",
        "title": "Calculated columns",
        "kind": "code",
        "timeout": T,
        "body": """
Assign to a new column name and pandas adds it. The calculation runs down the whole column, row by row, like NumPy:

```python
beams["load_kn"] = beams["load_kn_m"] * beams["span_m"]     # total load on each beam
beams["heavy"] = beams["load_kn"] > 80                      # a True/False column
```

There's no loop: each row's answer uses that row's values.

## Your task

Add a column `moment_knm` to `beams` holding the maximum bending moment of each beam: `w L^2 / 8`, where `w` is `load_kn_m` and `L` is `span_m`. Then print `beams`.
""",
        "starter": BEAMS + "\n# beams[\"moment_knm\"] = ...\n\nprint(beams)\n",
        "tests": '''
import numpy as np

def test_column():
    "moment_knm is w L^2 / 8"
    b = need("beams")
    check("moment_knm" in b.columns, "Add a column called moment_knm.")
    want = b["load_kn_m"] * b["span_m"] ** 2 / 8
    check(np.allclose(b["moment_knm"], want), "moment_knm is %r, expected %r." % (b["moment_knm"].tolist(), want.tolist()))
    check("for " not in CODE, "No loop needed: calculate the whole column at once.")
''',
        "solution": BEAMS + "\nbeams[\"moment_knm\"] = beams[\"load_kn_m\"] * beams[\"span_m\"] ** 2 / 8\n\nprint(beams)\n",
        "hints": [
            "`beams[\"moment_knm\"] = beams[\"load_kn_m\"] * beams[\"span_m\"] ** 2 / 8`",
        ],
    },
    {
        "id": "filter-rows",
        "title": "Filtering rows",
        "kind": "code",
        "timeout": T,
        "body": """
Filtering works like NumPy masks. A comparison on a column gives a True/False Series, and putting that inside `[ ]` keeps the True rows:

```python
long_ones = beams[beams["span_m"] > 5]
```

Two conditions: `&` for and, `|` for or, and **brackets round each condition**:

```python
picked = beams[(beams["span_m"] > 5) & (beams["load_kn_m"] < 12)]
```

It's the SQL `WHERE` again, written differently.

> **Common slips:**
> - `and` instead of `&` gives `ValueError: The truth value of a Series is ambiguous`.
> - Leaving out the brackets: `beams["span_m"] > 5 & beams["load_kn_m"] < 12` runs the `&` first and fails with a confusing error.

## Your task

Store `critical`: the beams with a span **over 5 m** and a load of **at least 11 kN/m**.
""",
        "starter": BEAMS + "\n# critical = beams[(...) & (...)]\n",
        "tests": '''
def test_rows():
    "Only the long, heavily loaded beams"
    c = need("critical")
    check(c["name"].tolist() == ["B3", "B5"], "critical holds %r, expected B3 and B5." % c["name"].tolist())
''',
        "solution": BEAMS + "\ncritical = beams[(beams[\"span_m\"] > 5) & (beams[\"load_kn_m\"] >= 11)]\nprint(critical)\n",
        "hints": [
            "Two conditions in brackets, joined with `&`: `(beams[\"span_m\"] > 5) & (beams[\"load_kn_m\"] >= 11)`.",
        ],
    },
    {
        "id": "and-quiz",
        "title": "Reading the error",
        "kind": "quiz",
        "body": "You'll see this error message a lot in your first weeks of pandas.",
        "question": "`beams[(beams[\"span_m\"] > 5) and (beams[\"load_kn_m\"] > 10)]` fails with \"The truth value of a Series is ambiguous\". What's the fix?",
        "options": [
            "Remove the brackets",
            "Replace `and` with `&`",
            "Use `==` instead of `>`",
            "Add `.tolist()` to each column",
        ],
        "answer": 1,
        "explain": "Python's `and` wants a single True or False, but each side is a whole column of them, so pandas can't say which you mean. `&` combines the two columns row by row, which is what you want.",
    },
    {
        "id": "loc-iloc",
        "title": "loc and iloc",
        "kind": "code",
        "timeout": T,
        "body": """
To pick out particular rows (and columns), there are two tools:

- `.iloc[...]` picks by **position**: 0, 1, 2 ...
- `.loc[...]` picks by **label**: the index value and column name.

Labels get more useful once you make a meaningful column the index:

```python
b = beams.set_index("name")      # the beam names become the row labels
b.loc["B3"]                      # the whole row for B3
b.loc["B3", "span_m"]            # 7.2: row B3, column span_m
b.iloc[0]                        # the first row, whatever it's called
b.loc[b["span_m"] > 5, "load_kn_m"]   # a mask for rows, a name for the column
```

Like NumPy, it's always `[rows, columns]`, separated by a comma.

## Your task

With `b = beams.set_index("name")` (already in the starter), store:

- `b4_load`: the `load_kn_m` of beam `B4`, using `.loc`
- `last_row`: the last row, using `.iloc`
- `long_loads`: the `load_kn_m` of beams with a span over 5 m, using `.loc` with a mask
""",
        "starter": BEAMS + "\nb = beams.set_index(\"name\")\n\n# b4_load = ...\n# last_row = ...\n# long_loads = ...\n",
        "tests": '''
import pandas as pd

def test_values():
    "Picks the right values"
    check(need("b4_load") == 20.0, "b4_load should be 20.0, got %r. Use b.loc[\\"B4\\", \\"load_kn_m\\"]." % ns.get("b4_load"))
    lr = need("last_row")
    check(isinstance(lr, pd.Series) and lr.name == "B5", "last_row should be the B5 row. Use b.iloc[-1].")
    ll = need("long_loads")
    check(isinstance(ll, pd.Series) and ll.to_dict() == {"B2": 8.5, "B3": 15.0, "B5": 11.0},
          "long_loads is %r. Use b.loc[b[\\"span_m\\"] > 5, \\"load_kn_m\\"]." % (ll.to_dict() if hasattr(ll, "to_dict") else ll,))
''',
        "solution": BEAMS + "\nb = beams.set_index(\"name\")\n\nb4_load = b.loc[\"B4\", \"load_kn_m\"]\nlast_row = b.iloc[-1]\nlong_loads = b.loc[b[\"span_m\"] > 5, \"load_kn_m\"]\nprint(b4_load, long_loads, sep=\"\\n\")\n",
        "hints": [
            "`b.loc[\"B4\", \"load_kn_m\"]` and `b.iloc[-1]`.",
            "`b.loc[b[\"span_m\"] > 5, \"load_kn_m\"]`",
        ],
    },
    {
        "id": "sorting",
        "title": "Sorting",
        "kind": "code",
        "timeout": T,
        "body": """
`sort_values` sorts by a column. It returns a new, sorted DataFrame and leaves the original alone:

```python
beams.sort_values("span_m")                        # shortest first
beams.sort_values("span_m", ascending=False)       # longest first
beams.sort_values(["load_kn_m", "span_m"])         # by load, ties by span
beams.nlargest(3, "span_m")                        # shortcut: top 3
```

> **Common slip:** `beams.sort_values("span_m")` on its own line does nothing useful. The sorted table is returned and thrown away. Keep it: `beams = beams.sort_values(...)`, or store it under a new name.

## Your task

Add a `load_kn` column (`load_kn_m * span_m`), then store `top3`: a plain **list** of the names of the three beams with the biggest `load_kn`, biggest first.
""",
        "starter": BEAMS + "\n# 1. beams[\"load_kn\"] = ...\n# 2. sort, take the top three rows, take their names, make a list\n",
        "tests": '''
def test_top3():
    "Top three names by total load"
    t = need("top3")
    check(isinstance(t, list), "top3 should be a plain list. Add .tolist() at the end.")
    check(t == ["B3", "B4", "B5"], "top3 is %r, expected ['B3', 'B4', 'B5']." % (t,))
''',
        "solution": BEAMS + "\nbeams[\"load_kn\"] = beams[\"load_kn_m\"] * beams[\"span_m\"]\ntop3 = beams.sort_values(\"load_kn\", ascending=False).head(3)[\"name\"].tolist()\nprint(top3)\n",
        "hints": [
            "`beams.sort_values(\"load_kn\", ascending=False)` sorts biggest first, and `.head(3)` keeps the first three rows.",
            "Then `[\"name\"].tolist()`. You can chain it all on one line.",
        ],
    },
    {
        "id": "pandas-task",
        "title": "Chapter task: a beam schedule",
        "kind": "code",
        "timeout": T,
        "body": """
The whole chapter in one function.

## Your task

Write `beam_schedule(names, spans_m, loads_kn_m, min_moment)` that:

1. builds a DataFrame with columns `name`, `span_m` and `load_kn_m` from the three lists,
2. adds `moment_knm` (`w L^2 / 8`),
3. keeps only beams whose moment is **at least** `min_moment`,
4. sorts them by moment, **biggest first**,
5. returns the result.
""",
        "starter": "import pandas as pd\n\n\ndef beam_schedule(names, spans_m, loads_kn_m, min_moment):\n    pass\n\n\nprint(beam_schedule([\"B1\", \"B2\", \"B3\"], [4.5, 6.0, 7.2], [12.0, 8.5, 15.0], 35))\n",
        "tests": '''
import pandas as pd
import numpy as np

def test_schedule():
    "Filtered and sorted schedule"
    f = need("beam_schedule")
    v, _ = capture(f, ["B1", "B2", "B3", "B4", "B5"], [4.5, 6.0, 7.2, 3.8, 5.5], [12.0, 8.5, 15.0, 20.0, 11.0], 35)
    check(isinstance(v, pd.DataFrame), "Return the DataFrame.")
    check(list(v.columns) == ["name", "span_m", "load_kn_m", "moment_knm"], "Columns are %r." % list(v.columns))
    names = v["name"].tolist()
    m = v["moment_knm"].tolist()
    check(names == ["B3", "B5", "B2", "B4"], "Rows are %r with moments %r. Expected B3, B5, B2, B4: moment of at least 35, biggest first." % (names, [round(x, 2) for x in m]))
''',
        "solution": "import pandas as pd\n\n\ndef beam_schedule(names, spans_m, loads_kn_m, min_moment):\n    df = pd.DataFrame({\"name\": names, \"span_m\": spans_m, \"load_kn_m\": loads_kn_m})\n    df[\"moment_knm\"] = df[\"load_kn_m\"] * df[\"span_m\"] ** 2 / 8\n    df = df[df[\"moment_knm\"] >= min_moment]\n    return df.sort_values(\"moment_knm\", ascending=False)\n\n\nprint(beam_schedule([\"B1\", \"B2\", \"B3\"], [4.5, 6.0, 7.2], [12.0, 8.5, 15.0], 35))\n",
        "hints": [
            "Build it with `pd.DataFrame({\"name\": names, ...})`, then add the column as before.",
            "Filter with `df = df[df[\"moment_knm\"] >= min_moment]`, then `return df.sort_values(\"moment_knm\", ascending=False)`.",
        ],
    },
]
