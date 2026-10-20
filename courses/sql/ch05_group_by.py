import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Aggregates and GROUP BY",
    "summary": "COUNT, SUM, AVG, MIN and MAX, then the same answers per group, and HAVING.",
}

LESSONS = [
    {
        "id": "count",
        "title": "Counting rows",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
So far every query has returned rows from the table. **Aggregate** functions do something different: they squash many rows into one answer.

```sql
SELECT COUNT(*) AS supplier_count
FROM suppliers;
-- one row, one column: 6
```

`COUNT(*)` counts rows. Add a `WHERE` and it counts only the rows that pass:

```sql
SELECT COUNT(*) AS riyadh_suppliers
FROM suppliers
WHERE city = 'Riyadh';
```

## Your task

How many deliveries went to site `JED-1`? Return one row with one column called `jed_deliveries`.
""",
        "starter": "-- count the deliveries to JED-1\n",
        "tests": '''
def test_rows():
    "One number: the JED-1 delivery count"
    check_rows("SELECT COUNT(*) FROM deliveries WHERE site = 'JED-1'", hint="COUNT(*) with a WHERE for the site.")

def test_name():
    "Named jed_deliveries"
    check_columns("jed_deliveries")
''',
        "solution": "SELECT COUNT(*) AS jed_deliveries\nFROM deliveries\nWHERE site = 'JED-1';\n",
        "hints": [
            "Same shape as the second example, on the deliveries table.",
            "`SELECT COUNT(*) AS jed_deliveries FROM deliveries WHERE site = 'JED-1';`",
        ],
    },
    {
        "id": "aggregates",
        "title": "SUM, AVG, MIN, MAX",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
The other everyday aggregates work on a column of numbers:

| Function | Gives |
|---|---|
| `SUM(col)` | the total |
| `AVG(col)` | the mean |
| `MIN(col)` | the smallest |
| `MAX(col)` | the largest |

You can use several at once. You still get one row:

```sql
SELECT MIN(years) AS least, MAX(years) AS most, AVG(years) AS average
FROM staff
WHERE site = 'RYD-N';
```

## Your task

For cement deliveries only (`material_id = 1`), return one row with four columns: `total`, `average`, `smallest` and `largest`, all worked out from `quantity`.
""",
        "starter": "SELECT SUM(quantity) AS total\nFROM deliveries\nWHERE material_id = 1;\n-- add average, smallest and largest\n",
        "tests": '''
def test_rows():
    "Total, average, smallest and largest cement delivery"
    check_rows("SELECT SUM(quantity), AVG(quantity), MIN(quantity), MAX(quantity) FROM deliveries WHERE material_id = 1")

def test_names():
    "Columns named total, average, smallest, largest"
    check_columns("total", "average", "smallest", "largest")
''',
        "solution": "SELECT SUM(quantity) AS total,\n       AVG(quantity) AS average,\n       MIN(quantity) AS smallest,\n       MAX(quantity) AS largest\nFROM deliveries\nWHERE material_id = 1;\n",
        "hints": [
            "Add three more columns to the SELECT, separated by commas, each with its own AS.",
            "`AVG(quantity) AS average, MIN(quantity) AS smallest, MAX(quantity) AS largest`",
        ],
    },
    {
        "id": "count-null",
        "title": "COUNT and NULL",
        "kind": "quiz",
        "body": """
`COUNT(*)` counts rows. `COUNT(column)` counts only the rows where that column **isn't NULL**. The other aggregates skip NULLs too: `AVG(rating)` averages only the suppliers that have a rating.
""",
        "question": "There are 9 materials and glass has no price. What does this return?\n\n```sql\nSELECT COUNT(*), COUNT(unit_price) FROM materials;\n```",
        "options": ["`9, 9`", "`9, 8`", "`8, 8`", "`8, 9`"],
        "answer": 1,
        "explain": "`COUNT(*)` counts all 9 rows. `COUNT(unit_price)` skips the row where unit_price is NULL, giving 8.",
    },
    {
        "id": "group-by",
        "title": "GROUP BY",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`COUNT(*)` with a `WHERE` answers one question: how many for this site? `GROUP BY` answers it for **every** site at once.

```sql
SELECT supplier_id, COUNT(*) AS deliveries
FROM deliveries
GROUP BY supplier_id;
```

Picture it in two steps:

1. `GROUP BY supplier_id` sorts the rows into piles, one pile per supplier.
2. The aggregate (`COUNT(*)`) runs once per pile, giving one result row per supplier.

The rule that keeps you out of trouble: **every column in the SELECT must either be in the GROUP BY, or be inside an aggregate.** Here `supplier_id` is the grouping column and `COUNT(*)` is the aggregate, so it's fine.

## Your task

Show each `site` and how many deliveries it received, in a column called `deliveries`.
""",
        "starter": "SELECT site, COUNT(*) AS deliveries\nFROM deliveries\n-- group by the site here\n",
        "tests": '''
def test_rows():
    "One row per site with its count"
    check_rows("SELECT site, COUNT(*) FROM deliveries GROUP BY site", hint="Without GROUP BY you get a single row.")

def test_name():
    "Columns are site and deliveries"
    check_columns("site", "deliveries")
''',
        "solution": "SELECT site, COUNT(*) AS deliveries\nFROM deliveries\nGROUP BY site;\n",
        "hints": [
            "Run the starter first: one row, which isn't right. Then add `GROUP BY site` as the last line.",
        ],
    },
    {
        "id": "group-sum",
        "title": "Totals per group",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Any aggregate works per group, and you can sort the grouped result with `ORDER BY` as usual. `ORDER BY` comes after `GROUP BY`.

```sql
SELECT site, SUM(quantity) AS total_qty
FROM deliveries
GROUP BY site
ORDER BY total_qty DESC;
```

You can sort by a column's `AS` name, as the last line does.

## Your task

For each `material_id`, show the total quantity delivered (call it `total_qty`). Sort by `material_id`.
""",
        "starter": "-- total quantity per material_id, sorted by material_id\n",
        "tests": '''
def test_rows():
    "Totals per material, in material order"
    check_rows("SELECT material_id, SUM(quantity) FROM deliveries GROUP BY material_id ORDER BY material_id", ordered=True)

def test_name():
    "Columns material_id and total_qty"
    check_columns("material_id", "total_qty")
''',
        "solution": "SELECT material_id, SUM(quantity) AS total_qty\nFROM deliveries\nGROUP BY material_id\nORDER BY material_id;\n",
        "hints": [
            "Same shape as the example, grouping by `material_id` instead of `site`.",
            "`GROUP BY material_id` then `ORDER BY material_id`.",
        ],
    },
    {
        "id": "bare-column",
        "title": "The grouping rule",
        "kind": "quiz",
        "body": "Many databases refuse a query that breaks the grouping rule. SQLite runs it anyway, which is worse, because the answer is quietly meaningless.",
        "question": "What's wrong with this?\n\n```sql\nSELECT site, delivery_date, COUNT(*)\nFROM deliveries\nGROUP BY site;\n```",
        "options": [
            "Nothing, it's fine",
            "`delivery_date` isn't grouped or aggregated, so each site just shows one of its dates, picked arbitrarily",
            "COUNT(*) can't be used with GROUP BY",
            "GROUP BY must come before FROM",
        ],
        "answer": 1,
        "explain": "Each site has many deliveries on many dates, but the result has one row per site. Which date should go in it? SQL can't know, so SQLite just picks one. Either add `delivery_date` to the GROUP BY, or wrap it in an aggregate like `MAX(delivery_date)`.",
    },
    {
        "id": "group-two",
        "title": "Grouping by two columns",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Group by two columns and you get one row per **combination**:

```sql
SELECT city, rating, COUNT(*) AS suppliers
FROM suppliers
GROUP BY city, rating;
```

## Your task

For each combination of `site` and `material_id`, show how many deliveries there were (as `deliveries`). Sort by site, then material_id.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "One row per site and material"
    check_rows("SELECT site, material_id, COUNT(*) FROM deliveries GROUP BY site, material_id ORDER BY site, material_id",
               ordered=True, hint="Both columns go in the GROUP BY.")

def test_name():
    "Third column is deliveries"
    check_columns("site", "material_id", "deliveries")
''',
        "solution": "SELECT site, material_id, COUNT(*) AS deliveries\nFROM deliveries\nGROUP BY site, material_id\nORDER BY site, material_id;\n",
        "hints": [
            "`GROUP BY site, material_id` and `ORDER BY site, material_id`.",
        ],
    },
    {
        "id": "having",
        "title": "HAVING",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`WHERE` filters rows **before** they're grouped. To filter the **groups** by their totals, use `HAVING`, which comes after `GROUP BY`:

```sql
SELECT site, COUNT(*) AS deliveries
FROM deliveries
GROUP BY site
HAVING COUNT(*) > 7;      -- only sites with more than 7 deliveries
```

The full order is now: `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`.

> **Common slip:** `WHERE COUNT(*) > 7`. WHERE runs before the groups exist, so there's nothing to count yet. SQLite says `misuse of aggregate`.

## Your task

Show each `material_id` and its total delivered quantity (as `total_qty`), but only for materials whose total is **more than 50**.
""",
        "starter": "SELECT material_id, SUM(quantity) AS total_qty\nFROM deliveries\nGROUP BY material_id\n-- keep only groups with a total over 50\n",
        "tests": '''
def test_rows():
    "Only materials with more than 50 in total"
    check_rows("SELECT material_id, SUM(quantity) FROM deliveries GROUP BY material_id HAVING SUM(quantity) > 50",
               hint="Use HAVING SUM(quantity) > 50 after the GROUP BY.")

def test_having():
    "Uses HAVING"
    check("HAVING" in SQL.upper(), "Filter the groups with HAVING.")
''',
        "solution": "SELECT material_id, SUM(quantity) AS total_qty\nFROM deliveries\nGROUP BY material_id\nHAVING SUM(quantity) > 50;\n",
        "hints": [
            "Add `HAVING SUM(quantity) > 50` after the `GROUP BY` line.",
        ],
    },
    {
        "id": "where-having",
        "title": "WHERE or HAVING?",
        "kind": "quiz",
        "body": "A quick test of which filter goes where.",
        "question": "You want the number of deliveries per site, counting only deliveries over 10 units, and showing only sites where that count is at least 5. Which is right?",
        "options": [
            "`WHERE quantity > 10 ... HAVING COUNT(*) >= 5`",
            "`HAVING quantity > 10 ... WHERE COUNT(*) >= 5`",
            "`WHERE quantity > 10 AND COUNT(*) >= 5`",
            "`HAVING quantity > 10 AND COUNT(*) >= 5`",
        ],
        "answer": 0,
        "explain": "`quantity > 10` is about single rows, so it's a WHERE: it decides which rows go into the piles. `COUNT(*) >= 5` is about whole groups, so it's a HAVING: it decides which piles make it into the result.",
    },
    {
        "id": "group-task",
        "title": "Chapter task: early October summary",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A summary report built from every piece in this chapter.

## Your task

For deliveries from 1 to 10 October 2026 (both included), show per `site`:

- `deliveries`: how many there were
- `total_qty`: their total quantity

Only include sites with **at least 3** deliveries in that period. Sort with the most deliveries first, and break ties by site name A to Z.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "The right summary rows, in the right order"
    check_rows("""SELECT site, COUNT(*), SUM(quantity) FROM deliveries
                  WHERE delivery_date BETWEEN '2026-10-01' AND '2026-10-10'
                  GROUP BY site HAVING COUNT(*) >= 3
                  ORDER BY COUNT(*) DESC, site""", ordered=True,
               hint="WHERE for the dates, GROUP BY site, HAVING for the count, then ORDER BY.")

def test_names():
    "Columns site, deliveries, total_qty"
    check_columns("site", "deliveries", "total_qty")
''',
        "solution": "SELECT site, COUNT(*) AS deliveries, SUM(quantity) AS total_qty\nFROM deliveries\nWHERE delivery_date BETWEEN '2026-10-01' AND '2026-10-10'\nGROUP BY site\nHAVING COUNT(*) >= 3\nORDER BY deliveries DESC, site;\n",
        "hints": [
            "Clause order: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY.",
            "`HAVING COUNT(*) >= 3` and `ORDER BY deliveries DESC, site`.",
        ],
    },
]
