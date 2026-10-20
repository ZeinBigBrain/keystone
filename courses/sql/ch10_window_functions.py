import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Window functions",
    "summary": "Numbering, ranking and running totals without collapsing rows: OVER, PARTITION BY, ROW_NUMBER, RANK.",
}

LESSONS = [
    {
        "id": "window-intro",
        "title": "Aggregates that keep the rows",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`GROUP BY` squashes each group into one row. Sometimes you want the group's total **next to every row** instead: each delivery, plus its site's total, say.

A **window function** does that. Put `OVER (...)` after an aggregate:

```sql
SELECT id, site, quantity,
       SUM(quantity) OVER () AS grand_total
FROM deliveries;
```

`OVER ()` with empty brackets means "the window is the whole result", so every row shows the same grand total. Nothing is squashed: you still get all 24 rows.

## Your task

Show every material's `name` and `unit_price`, plus a column `avg_price` holding the average price of all materials on every row.
""",
        "starter": "SELECT name, unit_price\n       -- add AVG(unit_price) OVER () AS avg_price\nFROM materials;\n",
        "tests": '''
def test_rows():
    "Every material with the overall average beside it"
    check_rows("SELECT name, unit_price, AVG(unit_price) OVER () FROM materials", hint="AVG(unit_price) OVER () AS avg_price.")

def test_name():
    "Third column is avg_price"
    check_columns("name", "unit_price", "avg_price")
''',
        "solution": "SELECT name, unit_price,\n       AVG(unit_price) OVER () AS avg_price\nFROM materials;\n",
        "hints": [
            "Add a comma after `unit_price`, then `AVG(unit_price) OVER () AS avg_price`.",
        ],
    },
    {
        "id": "partition",
        "title": "PARTITION BY",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`PARTITION BY` inside the `OVER` splits the window into groups, like `GROUP BY` does, but still keeps every row:

```sql
SELECT id, site, quantity,
       SUM(quantity) OVER (PARTITION BY site) AS site_total
FROM deliveries;
```

Each delivery now shows the total for **its own** site. That makes "what share of the site's total was this delivery?" a one-line calculation.

## Your task

Show each member of staff's `name`, `site` and `years`, plus `site_avg`: the average years of experience **at their site**.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Each person with their site's average"
    check_rows("SELECT name, site, years, AVG(years) OVER (PARTITION BY site) FROM staff",
               hint="AVG(years) OVER (PARTITION BY site).")

def test_name():
    "Fourth column is site_avg"
    check_columns("name", "site", "years", "site_avg")
''',
        "solution": "SELECT name, site, years,\n       AVG(years) OVER (PARTITION BY site) AS site_avg\nFROM staff;\n",
        "hints": [
            "`AVG(years) OVER (PARTITION BY site) AS site_avg`",
        ],
    },
    {
        "id": "row-number",
        "title": "ROW_NUMBER and RANK",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Some window functions only make sense with an order. `ORDER BY` inside the `OVER` gives it one:

```sql
SELECT name, years,
       ROW_NUMBER() OVER (ORDER BY years DESC) AS position
FROM staff;
```

| Function | Gives |
|---|---|
| `ROW_NUMBER()` | 1, 2, 3 ... with no ties |
| `RANK()` | ties share a rank, then it skips: 1, 2, 2, 4 |
| `DENSE_RANK()` | ties share a rank, no gaps: 1, 2, 2, 3 |

Add `PARTITION BY` and the numbering restarts for each group.

## Your task

Rank staff by experience **within each site**: show `site`, `name`, `years`, and `site_rank` (1 for the most experienced at that site). Use `RANK()`.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Ranks restart at each site"
    check_rows("SELECT site, name, years, RANK() OVER (PARTITION BY site ORDER BY years DESC) FROM staff",
               hint="RANK() OVER (PARTITION BY site ORDER BY years DESC).")

def test_name():
    "Fourth column is site_rank"
    check_columns("site", "name", "years", "site_rank")
''',
        "solution": "SELECT site, name, years,\n       RANK() OVER (PARTITION BY site ORDER BY years DESC) AS site_rank\nFROM staff;\n",
        "hints": [
            "Inside the OVER: `PARTITION BY site ORDER BY years DESC`.",
        ],
    },
    {
        "id": "rank-quiz",
        "title": "RANK versus ROW_NUMBER",
        "kind": "quiz",
        "body": "Three scores: 90, 85, 85, 70.",
        "question": "Ordered from highest, what does `RANK()` give those four rows?",
        "options": ["1, 2, 3, 4", "1, 2, 2, 3", "1, 2, 2, 4", "1, 1, 2, 3"],
        "answer": 2,
        "explain": "The two 85s tie for 2nd, and the next rank skips to 4, because three rows come before it. `DENSE_RANK()` would give 1, 2, 2, 3, and `ROW_NUMBER()` 1, 2, 3, 4.",
    },
    {
        "id": "running-total",
        "title": "Running totals",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`SUM(...) OVER (ORDER BY ...)` adds up everything **from the first row to this one**, which is a running total:

```sql
SELECT delivery_date, quantity,
       SUM(quantity) OVER (ORDER BY delivery_date, id) AS running_qty
FROM deliveries;
```

It's the running-total loop from the Python course, done by the database. Add `PARTITION BY` for one running total per group.

Order by something that's unique (here, date then id), so rows on the same day still add up one at a time.

## Your task

For cement deliveries only (`material_id = 1`), show `delivery_date`, `quantity` and `cumulative`, the running total of quantity in date order (then id). Sort the result the same way.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Running total of cement"
    check_rows("""SELECT delivery_date, quantity, SUM(quantity) OVER (ORDER BY delivery_date, id)
                  FROM deliveries WHERE material_id = 1 ORDER BY delivery_date, id""", ordered=True,
               hint="WHERE material_id = 1, and SUM(quantity) OVER (ORDER BY delivery_date, id).")

def test_name():
    "Third column is cumulative"
    check_columns("delivery_date", "quantity", "cumulative")
''',
        "solution": "SELECT delivery_date, quantity,\n       SUM(quantity) OVER (ORDER BY delivery_date, id) AS cumulative\nFROM deliveries\nWHERE material_id = 1\nORDER BY delivery_date, id;\n",
        "hints": [
            "`SUM(quantity) OVER (ORDER BY delivery_date, id) AS cumulative`, with `WHERE material_id = 1`.",
        ],
    },
    {
        "id": "window-task",
        "title": "Chapter task: biggest delivery per site",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A classic: "the top one per group". Window functions can't go in a `WHERE` directly, because WHERE runs first. So number the rows in a CTE, then filter on the number.

```sql
WITH numbered AS (
    SELECT ..., ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...) AS rn
    FROM ...
)
SELECT ... FROM numbered WHERE rn = 1;
```

## Your task

For each site, show its single **largest** delivery: `site`, `id` and `quantity`. If two deliveries at a site tie, take the one with the lower id. Sort by site.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Largest delivery per site"
    check_rows("""WITH n AS (SELECT site, id, quantity, ROW_NUMBER() OVER (PARTITION BY site ORDER BY quantity DESC, id) AS rn FROM deliveries)
                  SELECT site, id, quantity FROM n WHERE rn = 1 ORDER BY site""", ordered=True,
               hint="Number each site's deliveries by quantity, biggest first, and keep rn = 1.")
''',
        "solution": "WITH numbered AS (\n    SELECT site, id, quantity,\n           ROW_NUMBER() OVER (PARTITION BY site ORDER BY quantity DESC, id) AS rn\n    FROM deliveries\n)\nSELECT site, id, quantity\nFROM numbered\nWHERE rn = 1\nORDER BY site;\n",
        "hints": [
            "`ROW_NUMBER() OVER (PARTITION BY site ORDER BY quantity DESC, id) AS rn` inside the CTE.",
            "Then `SELECT site, id, quantity FROM numbered WHERE rn = 1 ORDER BY site`.",
        ],
    },
]
