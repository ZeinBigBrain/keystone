import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Subqueries and CTEs",
    "summary": "Queries inside queries: in WHERE, with IN, in FROM, and the tidier WITH form.",
}

LESSONS = [
    {
        "id": "subquery-where",
        "title": "A query inside a query",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Some questions need an answer before they can be asked. "Which materials cost more than average?" needs the average first.

You could run two queries and copy the number across. A **subquery** does it in one: a complete `SELECT` in brackets, used where a value would go.

```sql
SELECT name, years
FROM staff
WHERE years > (SELECT AVG(years) FROM staff);
```

SQL runs the inner query first (the average, 9.2), then uses that number in the outer one. The inner query must return a **single value** to be used with `>` like this.

A good way to build one: write and run the inner query on its own first, check its answer, then wrap it in brackets and drop it in.

## Your task

Show the `name` and `unit_price` of every material that costs **more than the average** unit price.
""",
        "starter": "-- step 1: run this on its own and look at the answer\nSELECT AVG(unit_price) FROM materials;\n\n-- step 2: use it in brackets inside the real query\n",
        "tests": '''
def test_rows():
    "Materials above the average price"
    check_rows("SELECT name, unit_price FROM materials WHERE unit_price > (SELECT AVG(unit_price) FROM materials)",
               hint="Put the AVG query in brackets after the >.")

def test_subquery():
    "Uses a subquery, not a typed number"
    up = SQL.upper()
    check("(SELECT" in up.replace("( SELECT", "(SELECT"), "Put the average query in brackets inside the WHERE.")
''',
        "solution": "SELECT name, unit_price\nFROM materials\nWHERE unit_price > (SELECT AVG(unit_price) FROM materials);\n",
        "hints": [
            "`WHERE unit_price > (SELECT AVG(unit_price) FROM materials)`",
        ],
    },
    {
        "id": "subquery-in",
        "title": "Subqueries with IN",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
When the inner query returns a **list** of values (one column, many rows), use it with `IN`:

```sql
SELECT name
FROM materials
WHERE id IN (SELECT material_id FROM deliveries WHERE site = 'JED-1');
```

Inner query: the material ids delivered to JED-1. Outer query: the names of those materials. This often reads more naturally than a join when you only want columns from one table.

`NOT IN` works the same way, for "never" questions. One catch: if the inner list contains a `NULL`, `NOT IN` returns nothing at all. Add `WHERE column IS NOT NULL` to the inner query when that's possible.

## Your task

Show the `name` and `city` of every supplier that has delivered to site `JED-1`.
""",
        "starter": "-- step 1: which supplier ids delivered to JED-1?\nSELECT supplier_id FROM deliveries WHERE site = 'JED-1';\n\n-- step 2: the suppliers whose id is IN that list\n",
        "tests": '''
def test_rows():
    "Suppliers who delivered to JED-1"
    check_rows("SELECT name, city FROM suppliers WHERE id IN (SELECT supplier_id FROM deliveries WHERE site = 'JED-1')",
               hint="Each supplier should appear once.")
''',
        "solution": "SELECT name, city\nFROM suppliers\nWHERE id IN (SELECT supplier_id FROM deliveries WHERE site = 'JED-1');\n",
        "hints": [
            "`WHERE id IN (SELECT supplier_id FROM deliveries WHERE site = 'JED-1')`",
        ],
    },
    {
        "id": "subquery-quiz",
        "title": "One value or many?",
        "kind": "quiz",
        "body": "Whether a subquery returns one value or a list decides how you can use it.",
        "question": "Which WHERE is correct for \"deliveries of the most expensive material\"?",
        "options": [
            "`WHERE material_id = (SELECT id FROM materials ORDER BY unit_price DESC LIMIT 1)`",
            "`WHERE material_id = (SELECT id, MAX(unit_price) FROM materials)`",
            "`WHERE material_id IN MAX(unit_price)`",
            "`WHERE MAX(material_id)`",
        ],
        "answer": 0,
        "explain": "The first returns exactly one value, the id of the priciest material, so `=` works. The second returns two columns, which can't be compared to one value. The last two aren't valid SQL.",
    },
    {
        "id": "subquery-from",
        "title": "Subqueries in FROM",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A subquery can also stand in for a **table**. Put it in `FROM`, give it an alias, and query its result like any other table.

This is how you aggregate twice: first per group, then across the groups.

```sql
SELECT MAX(n) AS busiest
FROM (
    SELECT site, COUNT(*) AS n
    FROM deliveries
    GROUP BY site
) AS per_site;
```

The inner query makes a little table of deliveries per site. The outer query finds the biggest number in it.

## Your task

What's the **average number of deliveries per site**? Count deliveries per site in a subquery, then average those counts. Return one column called `avg_per_site`.
""",
        "starter": "SELECT AVG(n) AS avg_per_site\nFROM (\n    -- deliveries per site, with the count called n\n) AS per_site;\n",
        "tests": '''
def test_rows():
    "The average of the per-site counts"
    check_rows("SELECT AVG(n) FROM (SELECT site, COUNT(*) AS n FROM deliveries GROUP BY site)",
               hint="The inner query is a GROUP BY site with COUNT(*) AS n.")

def test_name():
    "Named avg_per_site"
    check_columns("avg_per_site")
''',
        "solution": "SELECT AVG(n) AS avg_per_site\nFROM (\n    SELECT site, COUNT(*) AS n\n    FROM deliveries\n    GROUP BY site\n) AS per_site;\n",
        "hints": [
            "Inside the brackets: `SELECT site, COUNT(*) AS n FROM deliveries GROUP BY site`.",
        ],
    },
    {
        "id": "cte",
        "title": "WITH: naming a step",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Subqueries in `FROM` get hard to read once they nest. A **CTE** (common table expression) pulls the inner query out to the top and gives it a name:

```sql
WITH per_site AS (
    SELECT site, COUNT(*) AS n
    FROM deliveries
    GROUP BY site
)
SELECT MAX(n) AS busiest
FROM per_site;
```

It does exactly what the last example did, but reads top to bottom: first work out `per_site`, then use it.

You can define several, separated by commas, and later ones can use earlier ones:

```sql
WITH a AS (...),
     b AS (SELECT ... FROM a)
SELECT ... FROM b;
```

## Your task

Using a CTE called `spend_per_site` that works out each site's total spend (quantity times unit price, as `spend`), return the `site` and `spend` of sites whose spend is **above the average** site spend.
""",
        "starter": "WITH spend_per_site AS (\n    SELECT d.site, SUM(d.quantity * m.unit_price) AS spend\n    FROM deliveries d\n    JOIN materials m ON d.material_id = m.id\n    GROUP BY d.site\n)\n-- now select from spend_per_site\n",
        "tests": '''
def test_rows():
    "Sites spending more than the average site"
    check_rows("""WITH s AS (SELECT d.site, SUM(d.quantity * m.unit_price) AS spend FROM deliveries d
                  JOIN materials m ON d.material_id = m.id GROUP BY d.site)
                  SELECT site, spend FROM s WHERE spend > (SELECT AVG(spend) FROM s)""",
               hint="Compare spend with (SELECT AVG(spend) FROM spend_per_site).")

def test_with():
    "Uses WITH spend_per_site"
    check("WITH SPEND_PER_SITE" in SQL.upper(), "Start with WITH spend_per_site AS (...).")
''',
        "solution": "WITH spend_per_site AS (\n    SELECT d.site, SUM(d.quantity * m.unit_price) AS spend\n    FROM deliveries d\n    JOIN materials m ON d.material_id = m.id\n    GROUP BY d.site\n)\nSELECT site, spend\nFROM spend_per_site\nWHERE spend > (SELECT AVG(spend) FROM spend_per_site);\n",
        "hints": [
            "The CTE is done for you. Underneath it: `SELECT site, spend FROM spend_per_site WHERE spend > (...)`.",
            "The brackets hold another subquery on the CTE: `(SELECT AVG(spend) FROM spend_per_site)`.",
        ],
    },
    {
        "id": "cte-task",
        "title": "Chapter task: above-average deliveries",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A question that needs a value per group before it can be asked.

## Your task

For each **material**, find the deliveries whose quantity is **bigger than that material's own average** delivery. Show the material `name`, the delivery `id` and its `quantity`, sorted by name then id.

A plan: a CTE called `avg_qty` with each `material_id` and its average quantity (`avg_q`). Then join deliveries to it (and to materials, for the name) and compare.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Deliveries above their material's average"
    check_rows("""WITH a AS (SELECT material_id, AVG(quantity) AS avg_q FROM deliveries GROUP BY material_id)
                  SELECT m.name, d.id, d.quantity FROM deliveries d
                  JOIN a ON d.material_id = a.material_id
                  JOIN materials m ON d.material_id = m.id
                  WHERE d.quantity > a.avg_q ORDER BY m.name, d.id""", ordered=True,
               hint="Join each delivery to its own material's average, then keep quantity > avg_q.")
''',
        "solution": "WITH avg_qty AS (\n    SELECT material_id, AVG(quantity) AS avg_q\n    FROM deliveries\n    GROUP BY material_id\n)\nSELECT m.name, d.id, d.quantity\nFROM deliveries d\nJOIN avg_qty a ON d.material_id = a.material_id\nJOIN materials m ON d.material_id = m.id\nWHERE d.quantity > a.avg_q\nORDER BY m.name, d.id;\n",
        "hints": [
            "The CTE: `SELECT material_id, AVG(quantity) AS avg_q FROM deliveries GROUP BY material_id`.",
            "Then join it like a table: `JOIN avg_qty a ON d.material_id = a.material_id`, and `WHERE d.quantity > a.avg_q`.",
        ],
    },
]
