CHAPTER = {
    "title": "Grouping and summarising",
    "summary": "groupby, several summaries at once, pivot tables, merging tables, and summary statistics.",
}

T = 40

DELIVERIES_CSV = """date,site,material,qty
2026-10-01,RYD-N,cement,40
2026-10-01,RYD-N,sand,12
2026-10-02,RYD-S,cement,25
2026-10-02,RYD-N,rebar,3.5
2026-10-03,JED-1,cement,30
2026-10-03,RYD-N,gravel,18
2026-10-05,RYD-S,sand,20
2026-10-05,JED-1,rebar,2
2026-10-07,RYD-N,cement,35
2026-10-07,JED-1,sand,15
2026-10-08,RYD-S,rebar,5
2026-10-13,JED-1,cement,20
2026-10-17,RYD-S,cement,45
2026-10-18,RYD-N,gravel,22
"""

PRICES_CSV = """material,unit,unit_price
cement,bag,18.5
sand,t,45.0
gravel,t,52.0
rebar,t,2950.0
bricks,pallet,640.0
"""

READ = 'import pandas as pd\n\ndf = pd.read_csv("deliveries.csv")\n'

LESSONS = [
    {
        "id": "groupby",
        "title": "groupby",
        "kind": "code",
        "timeout": T,
        "files": {"deliveries.csv": DELIVERIES_CSV},
        "body": """
"Total per site", "average per month", "count per material": these are all **group, then summarise**. In pandas:

```python
df.groupby("material")["qty"].sum()
# material
# cement    195.0
# gravel     40.0
# ...
```

Read it as: split the rows into groups by `material`, take the `qty` column of each group, and add it up. If you did the SQL track, it's `GROUP BY` again.

The result is a Series with the group names as its index. Add `.reset_index()` to turn it back into an ordinary two-column table, which is easier to save or merge:

```python
totals = df.groupby("material")["qty"].sum().reset_index()
```

## Your task

From `deliveries.csv`, store `per_site`: the number of deliveries to each site, as a table with columns `site` and `qty` (use `.count()` on the `qty` column, then `.reset_index()`).
""",
        "starter": READ + "\n# per_site = ...\n",
        "tests": '''
import pandas as pd

def test_values():
    "Deliveries counted per site"
    p = need("per_site")
    check(isinstance(p, pd.DataFrame), "per_site should be a DataFrame. Add .reset_index() at the end.")
    check(list(p.columns) == ["site", "qty"], "Columns are %r, expected site and qty." % list(p.columns))
    check(dict(zip(p["site"], p["qty"])) == {"JED-1": 4, "RYD-N": 6, "RYD-S": 4}, "Counts are %r." % dict(zip(p["site"], p["qty"])))
''',
        "solution": READ + "\nper_site = df.groupby(\"site\")[\"qty\"].count().reset_index()\nprint(per_site)\n",
        "hints": [
            "`df.groupby(\"site\")[\"qty\"].count()` then `.reset_index()`.",
        ],
    },
    {
        "id": "agg",
        "title": "Several summaries at once",
        "kind": "code",
        "timeout": T,
        "files": {"deliveries.csv": DELIVERIES_CSV},
        "body": """
`.agg()` makes several summary columns in one go. Each new column is `name=(source column, function)`:

```python
summary = df.groupby("site").agg(
    deliveries=("qty", "count"),
    total=("qty", "sum"),
    biggest=("qty", "max"),
).reset_index()
```

The function names are text: `"sum"`, `"mean"`, `"count"`, `"min"`, `"max"`, `"median"`, `"std"`, `"first"`, `"last"`.

## Your task

Make `by_material`: one row per material with columns `material`, `deliveries` (how many), `total_qty` (sum of qty) and `avg_qty` (mean of qty).
""",
        "starter": READ + "\n# by_material = df.groupby(\"material\").agg(...).reset_index()\n",
        "tests": '''
import pandas as pd
import numpy as np

def test_values():
    "Count, total and average per material"
    b = need("by_material")
    check(list(b.columns) == ["material", "deliveries", "total_qty", "avg_qty"], "Columns are %r." % list(b.columns))
    b = b.set_index("material")
    check(b.loc["cement", "deliveries"] == 6 and b.loc["cement", "total_qty"] == 195, "cement should have 6 deliveries totalling 195.")
    check(np.isclose(b.loc["rebar", "avg_qty"], 3.5), "rebar's average should be 3.5.")
''',
        "solution": READ + "\nby_material = df.groupby(\"material\").agg(\n    deliveries=(\"qty\", \"count\"),\n    total_qty=(\"qty\", \"sum\"),\n    avg_qty=(\"qty\", \"mean\"),\n).reset_index()\nprint(by_material)\n",
        "hints": [
            "Three items inside `.agg(...)`: `deliveries=(\"qty\", \"count\")`, `total_qty=(\"qty\", \"sum\")`, `avg_qty=(\"qty\", \"mean\")`.",
        ],
    },
    {
        "id": "groupby-quiz",
        "title": "Where did the column go?",
        "kind": "quiz",
        "body": "A common puzzle after the first groupby.",
        "question": "After `t = df.groupby(\"site\")[\"qty\"].sum()`, why does `t[\"site\"]` fail?",
        "options": [
            "groupby deletes the site column",
            "`site` became the index (the row labels), not a column. `.reset_index()` turns it back into a column",
            "`t` is a list",
            "Sums can't have text columns",
        ],
        "answer": 1,
        "explain": "groupby puts the group names into the index. `t.index` holds the sites and `t[\"RYD-N\"]` would work. To have `site` as an ordinary column again, call `.reset_index()`.",
    },
    {
        "id": "pivot",
        "title": "Pivot tables",
        "kind": "code",
        "timeout": T,
        "files": {"deliveries.csv": DELIVERIES_CSV},
        "body": """
A **pivot table** groups by two things at once and lays the result out as a grid, like Excel's PivotTable:

```python
grid = df.pivot_table(
    index="site",          # one row per site
    columns="material",    # one column per material
    values="qty",          # what to summarise
    aggfunc="sum",         # how
    fill_value=0,          # 0 instead of NaN where nothing was delivered
)
```

Add `margins=True` for row and column totals.

## Your task

Make `grid`: total quantity with **one row per material** and **one column per site**, with `0` where there were no deliveries.
""",
        "starter": READ + "\n# grid = df.pivot_table(...)\n",
        "tests": '''
def test_grid():
    "Materials down the side, sites across the top"
    g = need("grid")
    check(list(g.index) == ["cement", "gravel", "rebar", "sand"], "The rows should be the materials. Use index=\\"material\\".")
    check(list(g.columns) == ["JED-1", "RYD-N", "RYD-S"], "The columns should be the sites. Use columns=\\"site\\".")
    check(g.loc["cement", "RYD-S"] == 70 and g.loc["gravel", "JED-1"] == 0, "Values look wrong. Use aggfunc=\\"sum\\" and fill_value=0.")
''',
        "solution": READ + "\ngrid = df.pivot_table(index=\"material\", columns=\"site\", values=\"qty\", aggfunc=\"sum\", fill_value=0)\nprint(grid)\n",
        "hints": [
            "Same as the example with `index` and `columns` swapped round.",
            "`df.pivot_table(index=\"material\", columns=\"site\", values=\"qty\", aggfunc=\"sum\", fill_value=0)`",
        ],
    },
    {
        "id": "merge",
        "title": "Merging tables",
        "kind": "code",
        "timeout": T,
        "files": {"deliveries.csv": DELIVERIES_CSV, "prices.csv": PRICES_CSV},
        "body": """
`pd.merge` lines two tables up on a shared column, the SQL `JOIN` in pandas:

```python
both = pd.merge(deliveries, prices, on="material", how="left")
```

- `on` names the column the two tables share.
- `how="left"` keeps every row of the first table, even if it has no match (the new columns get `NaN`). `how="inner"` keeps only rows that matched in both.

If the columns have different names in each table, use `left_on="material_id", right_on="id"` instead of `on`.

> **Check the row count after every merge.** A left merge should give exactly as many rows as the left table. More means the right table had repeated keys, and some rows got doubled.

## Your task

Merge `deliveries.csv` with `prices.csv` so every delivery has its unit price. Add a `cost` column (qty times unit_price). Then store `spend`: total cost per **site**, as a table with columns `site` and `cost`.
""",
        "starter": "import pandas as pd\n\ndeliveries = pd.read_csv(\"deliveries.csv\")\nprices = pd.read_csv(\"prices.csv\")\n\n# both = pd.merge(...)\n# both[\"cost\"] = ...\n# spend = ...\n",
        "tests": '''
import numpy as np

def test_merge():
    "Every delivery kept, with a cost"
    b = need("both")
    check(len(b) == 14, "both has %d rows. A left merge should keep all 14 deliveries." % len(b))
    check("cost" in b.columns and np.allclose(b["cost"], b["qty"] * b["unit_price"]), "Add cost = qty * unit_price.")

def test_spend():
    "Spend per site"
    s = need("spend")
    check(list(s.columns) == ["site", "cost"], "spend should have columns site and cost. Use .reset_index().")
    d = dict(zip(s["site"], s["cost"]))
    check(np.isclose(d["RYD-N"], 14332.5) and np.isclose(d["RYD-S"], 16945.0) and np.isclose(d["JED-1"], 7500.0), "Spend per site is %r." % d)
''',
        "solution": "import pandas as pd\n\ndeliveries = pd.read_csv(\"deliveries.csv\")\nprices = pd.read_csv(\"prices.csv\")\n\nboth = pd.merge(deliveries, prices, on=\"material\", how=\"left\")\nboth[\"cost\"] = both[\"qty\"] * both[\"unit_price\"]\nspend = both.groupby(\"site\")[\"cost\"].sum().reset_index()\nprint(spend)\n",
        "hints": [
            "`both = pd.merge(deliveries, prices, on=\"material\", how=\"left\")`",
            "`spend = both.groupby(\"site\")[\"cost\"].sum().reset_index()`",
        ],
    },
    {
        "id": "merge-quiz",
        "title": "Left or inner?",
        "kind": "quiz",
        "body": "Think about which rows survive.",
        "question": "Prices exist for cement, sand and gravel only. Deliveries include rebar. What does `pd.merge(deliveries, prices, on=\"material\", how=\"inner\")` do to the rebar deliveries?",
        "options": [
            "Keeps them with a price of 0",
            "Keeps them with a price of NaN",
            "Drops them, because they have no match",
            "Raises an error",
        ],
        "answer": 2,
        "explain": "An inner merge only keeps rows that matched in both tables, so rebar deliveries vanish, and their cost silently disappears from every total. `how=\"left\"` would keep them with `NaN` prices, which you'd then spot.",
    },
    {
        "id": "describe",
        "title": "Summary statistics",
        "kind": "code",
        "timeout": T,
        "body": """
`describe()` gives a quick statistical picture of a column:

```python
df["strength"].describe()
# count, mean, std, min, 25%, 50% (median), 75%, max
```

Each number is also available on its own: `.mean()`, `.std()`, `.median()`, `.min()`, `.max()`, and `.quantile(0.95)` for any percentile.

For concrete, the **characteristic strength** is often estimated as the mean minus 1.64 standard deviations: the value roughly 95% of results should beat.

## Your task

Write `strength_stats(values)` that takes a list of cube strengths and returns a dictionary with keys `mean`, `std`, `min` and `characteristic` (mean minus 1.64 times std), each rounded to 2 decimal places. Use a pandas Series.
""",
        "starter": "import pandas as pd\n\n\ndef strength_stats(values):\n    s = pd.Series(values)\n    pass\n\n\nprint(strength_stats([41.2, 39.5, 43.0, 38.8, 42.1, 40.6]))\n",
        "tests": '''
import pandas as pd

def test_stats():
    "Right statistics"
    vals = [41.2, 39.5, 43.0, 38.8, 42.1, 40.6]
    v, _ = capture(need("strength_stats"), vals)
    s = pd.Series(vals)
    want = {"mean": round(s.mean(), 2), "std": round(s.std(), 2), "min": round(s.min(), 2),
            "characteristic": round(s.mean() - 1.64 * s.std(), 2)}
    check(isinstance(v, dict), "Return a dictionary.")
    check(set(v) == set(want), "The keys should be mean, std, min and characteristic. Got %r." % list(v))
    for k in want:
        check(abs(v[k] - want[k]) < 0.006, "%s is %r, expected %r." % (k, v[k], want[k]))
''',
        "solution": "import pandas as pd\n\n\ndef strength_stats(values):\n    s = pd.Series(values)\n    mean, std = s.mean(), s.std()\n    return {\n        \"mean\": round(mean, 2),\n        \"std\": round(std, 2),\n        \"min\": round(s.min(), 2),\n        \"characteristic\": round(mean - 1.64 * std, 2),\n    }\n\n\nprint(strength_stats([41.2, 39.5, 43.0, 38.8, 42.1, 40.6]))\n",
        "hints": [
            "`s.mean()`, `s.std()` and `s.min()`.",
            "Build the dict with `round(..., 2)` on each value.",
        ],
    },
    {
        "id": "group-task",
        "title": "Chapter task: a monthly cost report",
        "kind": "code",
        "timeout": T,
        "files": {"deliveries.csv": DELIVERIES_CSV, "prices.csv": PRICES_CSV},
        "body": """
A report the commercial team would actually ask for.

## Your task

Write `cost_report(deliveries_path, prices_path)` that returns a DataFrame with one row per **site**, and columns:

- `site`
- `deliveries`: how many deliveries
- `cost`: total cost (quantity times unit price)
- `top_material`: the material with the highest total cost at that site

Sort by `cost`, biggest first. Reset the index so it runs 0, 1, 2.

`top_material` is the tricky part. One way: group by site **and** material to get the cost of each pair, sort that by cost (biggest first), then keep the first row for each site with `drop_duplicates(subset=["site"])`.
""",
        "starter": "import pandas as pd\n\n\ndef cost_report(deliveries_path, prices_path):\n    d = pd.read_csv(deliveries_path)\n    p = pd.read_csv(prices_path)\n    # 1. merge and add cost\n    # 2. per site: deliveries and cost\n    # 3. top material per site\n    # 4. put them together, sort, reset the index\n    pass\n\n\nprint(cost_report(\"deliveries.csv\", \"prices.csv\"))\n",
        "tests": '''
import pandas as pd
import numpy as np

def test_report():
    "One row per site, sorted by cost"
    v, _ = capture(need("cost_report"), "deliveries.csv", "prices.csv")
    check(isinstance(v, pd.DataFrame), "Return a DataFrame.")
    check(list(v.columns) == ["site", "deliveries", "cost", "top_material"], "Columns are %r." % list(v.columns))
    check(v["site"].tolist() == ["RYD-S", "RYD-N", "JED-1"], "Sites in order: %r. Sort by cost, biggest first." % v["site"].tolist())
    check(v["deliveries"].tolist() == [4, 6, 4], "Delivery counts: %r." % v["deliveries"].tolist())
    check(np.allclose(v["cost"], [16945.0, 14332.5, 7500.0]), "Costs: %r." % v["cost"].tolist())
    check(v["top_material"].tolist() == ["rebar", "rebar", "rebar"], "Top materials: %r." % v["top_material"].tolist())
    check(list(v.index) == [0, 1, 2], "Reset the index with .reset_index(drop=True).")
''',
        "solution": "import pandas as pd\n\n\ndef cost_report(deliveries_path, prices_path):\n    d = pd.read_csv(deliveries_path)\n    p = pd.read_csv(prices_path)\n    both = pd.merge(d, p, on=\"material\", how=\"left\")\n    both[\"cost\"] = both[\"qty\"] * both[\"unit_price\"]\n\n    per_site = both.groupby(\"site\").agg(\n        deliveries=(\"qty\", \"count\"),\n        cost=(\"cost\", \"sum\"),\n    ).reset_index()\n\n    pairs = both.groupby([\"site\", \"material\"])[\"cost\"].sum().reset_index()\n    top = pairs.sort_values(\"cost\", ascending=False).drop_duplicates(subset=[\"site\"])\n    top = top[[\"site\", \"material\"]].rename(columns={\"material\": \"top_material\"})\n\n    report = pd.merge(per_site, top, on=\"site\")\n    return report.sort_values(\"cost\", ascending=False).reset_index(drop=True)\n\n\nprint(cost_report(\"deliveries.csv\", \"prices.csv\"))\n",
        "hints": [
            "Steps 1 and 2 are the merge lesson plus the agg lesson.",
            "Step 3: `pairs = both.groupby([\"site\", \"material\"])[\"cost\"].sum().reset_index()`, then `pairs.sort_values(\"cost\", ascending=False).drop_duplicates(subset=[\"site\"])`.",
            "Step 4: rename `material` to `top_material` with `.rename(columns={...})`, merge onto the per-site table on `site`, sort by cost and `.reset_index(drop=True)`.",
        ],
    },
]
