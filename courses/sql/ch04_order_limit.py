import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Sorting and limiting",
    "summary": "ORDER BY, sorting on several columns, LIMIT and OFFSET, and the order clauses go in.",
}

LESSONS = [
    {
        "id": "order-by",
        "title": "ORDER BY",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Rows come back in whatever order the database finds convenient. If the order matters, ask for it with `ORDER BY`, which goes at the end:

```sql
SELECT name, years
FROM staff
ORDER BY years;
```

That sorts smallest first (**ascending**). Text sorts alphabetically, and dates stored as `'YYYY-MM-DD'` sort in date order.

## Your task

Show the `name` and `unit_price` of every material, cheapest first.
""",
        "starter": "SELECT name, unit_price\nFROM materials\n-- sort by price here\n",
        "tests": '''
def test_rows():
    "Cheapest first"
    check_rows("SELECT name, unit_price FROM materials ORDER BY unit_price", ordered=True)
''',
        "solution": "SELECT name, unit_price\nFROM materials\nORDER BY unit_price;\n",
        "hints": [
            "`ORDER BY unit_price` as the last line.",
        ],
    },
    {
        "id": "desc",
        "title": "Biggest first",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Add `DESC` (descending) after the column to flip the order. `ASC` means ascending, which is the default, so you rarely need to write it.

```sql
SELECT name, years
FROM staff
ORDER BY years DESC;    -- most experienced first
```

You'll have noticed glass came first last time. In SQLite, `NULL` counts as smaller than any number, so it sorts first going up and last going down.

## Your task

Show the `id`, `delivery_date` and `quantity` of every delivery, **largest quantity first**.
""",
        "starter": "-- every delivery, largest quantity first\n",
        "tests": '''
def test_rows():
    "Largest quantity first"
    check_rows("SELECT id, delivery_date, quantity FROM deliveries ORDER BY quantity DESC", ordered=(2,))
''',
        "solution": "SELECT id, delivery_date, quantity\nFROM deliveries\nORDER BY quantity DESC;\n",
        "hints": [
            "`ORDER BY quantity DESC`",
        ],
    },
    {
        "id": "order-two",
        "title": "Sorting on two columns",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
List several columns after `ORDER BY`. SQL sorts by the first one, and only uses the second to break ties:

```sql
SELECT name, city, rating
FROM suppliers
ORDER BY city, name;
```

Each column gets its own direction. `ORDER BY city, rating DESC` sorts cities A to Z, and within each city puts the best rating first.

## Your task

Show the `site`, `name` and `years` of all staff, sorted by site (A to Z), and within each site by years of experience, **most first**.
""",
        "starter": "-- staff by site, then most experienced first\n",
        "tests": '''
def test_rows():
    "By site, then years descending"
    check_rows("SELECT site, name, years FROM staff ORDER BY site, years DESC", ordered=True,
               hint="Two columns after ORDER BY, and DESC only on the second.")
''',
        "solution": "SELECT site, name, years\nFROM staff\nORDER BY site, years DESC;\n",
        "hints": [
            "`ORDER BY site, years DESC`. The `DESC` only applies to `years`.",
        ],
    },
    {
        "id": "limit",
        "title": "LIMIT",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`LIMIT n` keeps only the first `n` rows of the result. Combined with `ORDER BY` it answers "top 3" and "bottom 5" questions:

```sql
SELECT name, years
FROM staff
ORDER BY years DESC
LIMIT 3;          -- the three most experienced
```

Without an `ORDER BY`, "the first 3 rows" means whichever three the database happens to return, which isn't a useful answer to anything.

## Your task

Show the `name` and `unit_price` of the **three most expensive** materials, most expensive first.
""",
        "starter": "-- the three most expensive materials\n",
        "tests": '''
def test_rows():
    "The top three by price"
    check_rows("SELECT name, unit_price FROM materials ORDER BY unit_price DESC LIMIT 3", ordered=True,
               hint="Sort by price, biggest first, then LIMIT 3.")
''',
        "solution": "SELECT name, unit_price\nFROM materials\nORDER BY unit_price DESC\nLIMIT 3;\n",
        "hints": [
            "`ORDER BY unit_price DESC` then `LIMIT 3` on the line after.",
        ],
    },
    {
        "id": "clause-order",
        "title": "The order of the parts",
        "kind": "quiz",
        "body": """
Every part of a SELECT has a fixed place. You don't need all of them, but the ones you use must come in this order:

```sql
SELECT ...
FROM ...
WHERE ...
ORDER BY ...
LIMIT ...;
```

(`GROUP BY` and `HAVING` slot in after `WHERE` in the next chapter.)
""",
        "question": "Which of these runs without an error?",
        "options": [
            "`SELECT name FROM staff ORDER BY years WHERE site = 'RYD-N';`",
            "`SELECT name FROM staff LIMIT 2 ORDER BY years;`",
            "`SELECT name FROM staff WHERE site = 'RYD-N' ORDER BY years LIMIT 2;`",
            "`SELECT name WHERE site = 'RYD-N' FROM staff;`",
        ],
        "answer": 2,
        "explain": "Only the third keeps the order SELECT, FROM, WHERE, ORDER BY, LIMIT. The others put a clause in the wrong place, and SQLite reports a syntax error near the word that's out of place.",
    },
    {
        "id": "offset",
        "title": "Paging with OFFSET",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`OFFSET n` skips the first `n` rows before `LIMIT` starts counting. That's how apps show results a page at a time:

```sql
-- page 1: rows 1 to 10
... ORDER BY id LIMIT 10 OFFSET 0;
-- page 2: rows 11 to 20
... ORDER BY id LIMIT 10 OFFSET 10;
```

For page `p` with `n` rows per page, the offset is `(p - 1) * n`.

Paging only makes sense with an `ORDER BY` that gives every row a definite position. Sorting by date alone isn't enough when two deliveries share a date, so add `id` as a tie-breaker.

## Your task

Show **page 2** of the deliveries, **5 per page**, sorted by `delivery_date` and then `id`. Show the `id`, `delivery_date` and `site`.
""",
        "starter": "SELECT id, delivery_date, site\nFROM deliveries\nORDER BY delivery_date, id\n-- LIMIT ... OFFSET ...\n",
        "tests": '''
def test_rows():
    "Rows 6 to 10"
    check_rows("SELECT id, delivery_date, site FROM deliveries ORDER BY delivery_date, id LIMIT 5 OFFSET 5", ordered=True,
               hint="Page 2 with 5 per page skips 5 rows.")
''',
        "solution": "SELECT id, delivery_date, site\nFROM deliveries\nORDER BY delivery_date, id\nLIMIT 5 OFFSET 5;\n",
        "hints": [
            "Page 2 means skip one page of 5: `OFFSET 5`.",
            "`LIMIT 5 OFFSET 5`",
        ],
    },
    {
        "id": "order-task",
        "title": "Chapter task: the biggest cement deliveries",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Everything from the last two chapters in one query.

## Your task

Cement is material id `1`. Show the `delivery_date`, `site` and `quantity` of the **three largest** cement deliveries, largest first. If two had the same quantity, the earlier date should come first.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Top three cement deliveries"
    check_rows("SELECT delivery_date, site, quantity FROM deliveries WHERE material_id = 1 ORDER BY quantity DESC, delivery_date LIMIT 3",
               ordered=True, hint="Filter to material 1 first, then sort and limit.")
''',
        "solution": "SELECT delivery_date, site, quantity\nFROM deliveries\nWHERE material_id = 1\nORDER BY quantity DESC, delivery_date\nLIMIT 3;\n",
        "hints": [
            "The parts in order: SELECT, FROM, WHERE (material 1), ORDER BY, LIMIT.",
            "`ORDER BY quantity DESC, delivery_date` then `LIMIT 3`.",
        ],
    },
]
