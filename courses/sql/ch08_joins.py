import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Joins",
    "summary": "Putting split-up data back together: INNER JOIN, aliases, LEFT JOIN, three tables, self joins, and spotting a bad join.",
}

LESSONS = [
    {
        "id": "join-why",
        "title": "Why joins exist",
        "kind": "read",
        "body": """
Last chapter split data into tables so each fact is stored once. The price: a delivery row says `material_id = 4`, and to show the word `rebar` you have to look in another table.

A **join** does that lookup for every row at once. Picture it:

```
deliveries                         materials
id | material_id | quantity        id | name
---+-------------+---------        ---+-------
 4 |      4      |   3.5    --->    4 | rebar
 5 |      1      |   30     --->    1 | cement
```

For each delivery, SQL finds the material row whose `id` matches the delivery's `material_id`, and glues the two rows side by side. Then you can `SELECT` columns from either half.

The matching rule goes after the word `ON`:

```sql
SELECT deliveries.id, materials.name, deliveries.quantity
FROM deliveries
JOIN materials ON deliveries.material_id = materials.id;
```

Read the last line as: "join on the rows where the delivery's `material_id` equals the material's `id`". Because both tables have columns called `id`, every column is written `table.column` so SQL knows which one you mean.

Almost every join you write links a **foreign key** (like `material_id`) to the **primary key** it points at (like `materials.id`).
""",
    },
    {
        "id": "first-join",
        "title": "Your first join",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Here's the example from the last page, ready to finish. Only the `ON` part is missing.

```sql
SELECT deliveries.id, materials.name, deliveries.quantity
FROM deliveries
JOIN materials ON deliveries.material_id = materials.id;
```

## Your task

Show each delivery's `id`, the **name of its supplier**, and its `quantity`. The supplier's name is in `suppliers.name`, and deliveries point at it with `supplier_id`.
""",
        "starter": "SELECT deliveries.id, suppliers.name, deliveries.quantity\nFROM deliveries\nJOIN suppliers ON -- which column matches which?\n",
        "tests": '''
def test_rows():
    "Every delivery with its supplier's name"
    check_rows("SELECT deliveries.id, suppliers.name, deliveries.quantity FROM deliveries JOIN suppliers ON deliveries.supplier_id = suppliers.id",
               hint="Match the delivery's supplier_id to the supplier's id.")
''',
        "solution": "SELECT deliveries.id, suppliers.name, deliveries.quantity\nFROM deliveries\nJOIN suppliers ON deliveries.supplier_id = suppliers.id;\n",
        "hints": [
            "The foreign key is `deliveries.supplier_id`. It points at `suppliers.id`.",
            "`JOIN suppliers ON deliveries.supplier_id = suppliers.id`",
        ],
    },
    {
        "id": "aliases",
        "title": "Short names for tables",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Writing `deliveries.` over and over gets old. Give each table a short **alias** after its name, then use that everywhere in the query:

```sql
SELECT d.id, m.name, d.quantity
FROM deliveries d
JOIN materials m ON d.material_id = m.id;
```

`d` and `m` only exist inside this one query. The alias is defined in `FROM` and `JOIN`, but you can use it in `SELECT` above them, because SQL reads the whole statement before running it.

## Your task

Show each delivery's `delivery_date`, material `name`, `quantity` and the material's `unit`, sorted by date and then delivery id. Use the aliases `d` and `m`.
""",
        "starter": "SELECT d.delivery_date, m.name, d.quantity, m.unit\nFROM deliveries d\n-- JOIN ...\n-- ORDER BY ...\n",
        "tests": '''
def test_rows():
    "Date, material, quantity and unit, sorted"
    check_rows("SELECT d.delivery_date, m.name, d.quantity, m.unit FROM deliveries d JOIN materials m ON d.material_id = m.id ORDER BY d.delivery_date, d.id",
               ordered=True)

def test_aliases():
    "Uses the aliases d and m"
    up = " " + SQL.upper() + " "
    check(" DELIVERIES D " in up and " MATERIALS M " in up, "Give the tables the aliases d and m: FROM deliveries d JOIN materials m.")
''',
        "solution": "SELECT d.delivery_date, m.name, d.quantity, m.unit\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id\nORDER BY d.delivery_date, d.id;\n",
        "hints": [
            "`JOIN materials m ON d.material_id = m.id`",
            "`ORDER BY d.delivery_date, d.id`",
        ],
    },
    {
        "id": "ambiguous-quiz",
        "title": "Which id?",
        "kind": "quiz",
        "body": "A very common error message when you start joining.",
        "question": "This fails with `ambiguous column name: id`. Why?\n\n```sql\nSELECT id, name\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id;\n```",
        "options": [
            "`id` is a reserved word",
            "Both tables have an `id` column, so SQL can't tell which you mean",
            "Aliases can't be used with JOIN",
            "The ON condition is the wrong way round",
        ],
        "answer": 1,
        "explain": "`deliveries` and `materials` both have an `id`. Say which: `d.id` or `m.id`. (`name` is fine here, because only `materials` has one.) Prefixing every column with its alias in a join is a good habit anyway.",
    },
    {
        "id": "join-where",
        "title": "Filtering a join",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Once two tables are joined, `WHERE` can test columns from **either** of them. That's how you ask questions like "deliveries of materials in a certain category", where the category lives in one table and the deliveries in another:

```sql
SELECT d.id, m.name, d.quantity
FROM deliveries d
JOIN materials m ON d.material_id = m.id
WHERE m.category = 'aggregate';
```

`WHERE` comes after all the `JOIN` lines.

## Your task

Show the `delivery_date`, `site` and `quantity` of every delivery of a material in the `finishes` category, sorted by date.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Finishes deliveries, by date"
    check_rows("SELECT d.delivery_date, d.site, d.quantity FROM deliveries d JOIN materials m ON d.material_id = m.id WHERE m.category = 'finishes' ORDER BY d.delivery_date",
               ordered=(0,), hint="Join materials so you can test m.category.")
''',
        "solution": "SELECT d.delivery_date, d.site, d.quantity\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id\nWHERE m.category = 'finishes'\nORDER BY d.delivery_date;\n",
        "hints": [
            "Same join as before, then `WHERE m.category = 'finishes'`, then `ORDER BY d.delivery_date`.",
        ],
    },
    {
        "id": "join-calc",
        "title": "Calculating across tables",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A calculation can mix columns from both tables. The quantity is in `deliveries` and the price is in `materials`, so the cost of each delivery needs the join:

```sql
SELECT d.id, d.quantity * m.unit_price AS cost
FROM deliveries d
JOIN materials m ON d.material_id = m.id;
```

## Your task

Show the **five most expensive** deliveries: their `id`, material `name`, and `cost` (quantity times unit price), most expensive first.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Top five deliveries by cost"
    check_rows("SELECT d.id, m.name, d.quantity * m.unit_price FROM deliveries d JOIN materials m ON d.material_id = m.id ORDER BY 3 DESC LIMIT 5",
               ordered=True, hint="ORDER BY cost DESC, then LIMIT 5.")

def test_name():
    "Third column is called cost"
    check_columns("id", "name", "cost")
''',
        "solution": "SELECT d.id, m.name, d.quantity * m.unit_price AS cost\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id\nORDER BY cost DESC\nLIMIT 5;\n",
        "hints": [
            "`d.quantity * m.unit_price AS cost`, then `ORDER BY cost DESC LIMIT 5`.",
        ],
    },
    {
        "id": "join-group",
        "title": "Joins with GROUP BY",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Joins and grouping combine naturally. Join first to get the columns you need, then group:

```sql
SELECT s.name, COUNT(*) AS deliveries
FROM deliveries d
JOIN suppliers s ON d.supplier_id = s.id
GROUP BY s.name;
```

## Your task

For each material **name**, show the total spent on it across all deliveries (quantity times unit price, summed), as `spend`. Biggest spend first.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Spend per material, biggest first"
    check_rows("SELECT m.name, SUM(d.quantity * m.unit_price) FROM deliveries d JOIN materials m ON d.material_id = m.id GROUP BY m.name ORDER BY 2 DESC",
               ordered=True, hint="SUM(d.quantity * m.unit_price), grouped by m.name.")

def test_name():
    "Columns name and spend"
    check_columns("name", "spend")
''',
        "solution": "SELECT m.name, SUM(d.quantity * m.unit_price) AS spend\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id\nGROUP BY m.name\nORDER BY spend DESC;\n",
        "hints": [
            "`SUM(d.quantity * m.unit_price) AS spend`",
            "`GROUP BY m.name` then `ORDER BY spend DESC`.",
        ],
    },
    {
        "id": "no-on-quiz",
        "title": "A join gone wrong",
        "kind": "quiz",
        "body": "Row counts are your best early warning that a join is wrong.",
        "question": "There are 24 deliveries and 9 materials. Someone forgets the matching rule:\n\n```sql\nSELECT d.id, m.name\nFROM deliveries d, materials m;\n```\n\nHow many rows come back?",
        "options": ["24", "9", "33", "216"],
        "answer": 3,
        "explain": "With no rule, every delivery is paired with every material: 24 x 9 = 216 rows, most of them nonsense. If a join returns far more rows than either table has, check the ON condition first.",
    },
    {
        "id": "left-join",
        "title": "LEFT JOIN",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A plain `JOIN` (also called `INNER JOIN`) only keeps rows that found a match. Glass has never been delivered, so it vanishes from every join with `deliveries`.

`LEFT JOIN` keeps **every row from the left table** (the one in `FROM`), matched or not. Where there's no match, the right table's columns come back as `NULL`:

```sql
SELECT s.name, COUNT(d.id) AS deliveries
FROM suppliers s
LEFT JOIN deliveries d ON d.supplier_id = s.id
GROUP BY s.name;
-- Coastal Glass Co shows 0
```

Notice `COUNT(d.id)`, not `COUNT(*)`. For an unmatched supplier there's still one row (with `d.id` as NULL), so `COUNT(*)` would say 1. `COUNT(d.id)` skips the NULL and correctly says 0.

## Your task

Show **every** material's `name` and how many deliveries it has had, as `deliveries`, including materials with none. Sort by name.
""",
        "starter": "SELECT m.name, COUNT(d.id) AS deliveries\nFROM materials m\nJOIN deliveries d ON d.material_id = m.id\nGROUP BY m.name\nORDER BY m.name;\n",
        "tests": '''
def test_rows():
    "Every material, glass included with 0"
    check_rows("SELECT m.name, COUNT(d.id) FROM materials m LEFT JOIN deliveries d ON d.material_id = m.id GROUP BY m.name ORDER BY m.name",
               ordered=True, hint="Glass should be there with 0. Is it a LEFT JOIN, and are you counting d.id?")
''',
        "solution": "SELECT m.name, COUNT(d.id) AS deliveries\nFROM materials m\nLEFT JOIN deliveries d ON d.material_id = m.id\nGROUP BY m.name\nORDER BY m.name;\n",
        "hints": [
            "Run the starter: glass is missing. Change `JOIN` to `LEFT JOIN`.",
        ],
    },
    {
        "id": "left-quiz",
        "title": "Finding what's missing",
        "kind": "quiz",
        "body": "LEFT JOIN plus `IS NULL` is the standard way to find things that have no match.",
        "question": "What does this return?\n\n```sql\nSELECT s.name\nFROM suppliers s\nLEFT JOIN deliveries d ON d.supplier_id = s.id\nWHERE d.id IS NULL;\n```",
        "options": [
            "Every supplier",
            "Suppliers that have made at least one delivery",
            "Suppliers that have never made a delivery",
            "Nothing, because ids are never NULL",
        ],
        "answer": 2,
        "explain": "The LEFT JOIN keeps every supplier. The ones with no deliveries get NULL in every `d.` column, so `WHERE d.id IS NULL` keeps exactly those. Here that's Coastal Glass Co.",
    },
    {
        "id": "three-tables",
        "title": "Joining three tables",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Add one `JOIN` line per extra table. Each has its own `ON`:

```sql
SELECT d.delivery_date, m.name AS material, si.name AS site_name
FROM deliveries d
JOIN materials m ON d.material_id = m.id
JOIN sites si ON d.site = si.code;
```

Each join is a separate lookup from `deliveries` out to one other table. When two columns would both be called `name`, rename them with `AS` so the result makes sense.

## Your task

For deliveries to site `JED-1`, show the `delivery_date`, the material name as `material`, and the supplier name as `supplier`. Sort by date.
""",
        "starter": "SELECT d.delivery_date, m.name AS material, s.name AS supplier\nFROM deliveries d\n-- one JOIN for materials, one for suppliers\n-- WHERE ...\n-- ORDER BY ...\n",
        "tests": '''
def test_rows():
    "JED-1 deliveries with material and supplier"
    check_rows("""SELECT d.delivery_date, m.name, s.name FROM deliveries d
                  JOIN materials m ON d.material_id = m.id
                  JOIN suppliers s ON d.supplier_id = s.id
                  WHERE d.site = 'JED-1' ORDER BY d.delivery_date""", ordered=(0,))

def test_names():
    "Columns delivery_date, material, supplier"
    check_columns("delivery_date", "material", "supplier")
''',
        "solution": "SELECT d.delivery_date, m.name AS material, s.name AS supplier\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id\nJOIN suppliers s ON d.supplier_id = s.id\nWHERE d.site = 'JED-1'\nORDER BY d.delivery_date;\n",
        "hints": [
            "`JOIN materials m ON d.material_id = m.id` and `JOIN suppliers s ON d.supplier_id = s.id`.",
            "Then `WHERE d.site = 'JED-1' ORDER BY d.delivery_date`.",
        ],
    },
    {
        "id": "self-join",
        "title": "Joining a table to itself",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
In `staff`, `manager_id` points at another row of the **same** table. To show each person next to their manager's name, join `staff` to itself, using two different aliases so SQL can tell the two copies apart:

```sql
SELECT e.name AS employee, b.name AS boss
FROM staff e
JOIN staff b ON e.manager_id = b.id;
```

Think of `e` as "the employee's row" and `b` as "the boss's row". The `ON` says: the employee's `manager_id` is the boss's `id`.

The three top managers have `manager_id` NULL, so an inner join drops them. Use `LEFT JOIN` to keep them, with an empty boss.

## Your task

Show every member of staff as `employee` with their manager's name as `manager`, **including** the people with no manager. Sort by employee name.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Everyone, with their manager (or NULL)"
    check_rows("SELECT e.name, b.name FROM staff e LEFT JOIN staff b ON e.manager_id = b.id ORDER BY e.name",
               ordered=True, hint="All 10 staff should appear. Use LEFT JOIN to keep the top managers.")

def test_names():
    "Columns employee and manager"
    check_columns("employee", "manager")
''',
        "solution": "SELECT e.name AS employee, b.name AS manager\nFROM staff e\nLEFT JOIN staff b ON e.manager_id = b.id\nORDER BY e.name;\n",
        "hints": [
            "Same as the example but with `LEFT JOIN`, and `b.name AS manager`.",
            "`ORDER BY e.name` at the end.",
        ],
    },
    {
        "id": "bad-join",
        "title": "Checking a join",
        "kind": "read",
        "body": """
A wrong join rarely gives an error. It just gives a confident, wrong answer. Three quick checks catch most of them.

## 1. Predict the row count first

Before running, say how many rows you expect.

- Joining each delivery to its material should give **one row per delivery**: 24. Each delivery has exactly one material.
- If you get more, something is matching several times: usually a wrong or missing `ON`.
- If you get fewer, rows are being dropped: an inner join where you needed a `LEFT JOIN`, or a `WHERE` on the right-hand table that throws away the NULL rows.

## 2. Check the ON joins a key to its key

`ON d.material_id = m.id` is right. `ON d.id = m.id` runs fine and is nonsense: it pairs delivery 4 with material 4 because they happen to share a number.

## 3. Spot-check one row by hand

Pick one row of the result and look it up yourself in the original tables. Thirty seconds, and it catches the joins that look plausible.

## A sneaky one: WHERE after a LEFT JOIN

```sql
SELECT m.name, d.id
FROM materials m
LEFT JOIN deliveries d ON d.material_id = m.id
WHERE d.site = 'RYD-N';
```

Glass has no deliveries, so its `d.site` is NULL, and the WHERE throws it away. The LEFT JOIN might as well be a plain JOIN. If you want to keep unmatched rows while filtering the right-hand table, move the test into the `ON`: `LEFT JOIN deliveries d ON d.material_id = m.id AND d.site = 'RYD-N'`.
""",
    },
    {
        "id": "join-task",
        "title": "Chapter task: supplier spend in Riyadh",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Four tables, one question.

## Your task

For deliveries to sites in the city of `Riyadh` only, show each supplier's `name` as `supplier` and their total spend as `spend` (quantity times unit price, summed). Only include suppliers whose spend is **over 10,000**. Biggest spend first.

You'll need `deliveries`, `materials` (for the price), `suppliers` (for the name) and `sites` (for the city).
""",
        "starter": "",
        "tests": '''
def test_rows():
    "Supplier spend for Riyadh sites over 10,000"
    check_rows("""SELECT s.name, SUM(d.quantity * m.unit_price) FROM deliveries d
                  JOIN materials m ON d.material_id = m.id
                  JOIN suppliers s ON d.supplier_id = s.id
                  JOIN sites si ON d.site = si.code
                  WHERE si.city = 'Riyadh'
                  GROUP BY s.name HAVING SUM(d.quantity * m.unit_price) > 10000
                  ORDER BY 2 DESC""", ordered=True,
               hint="WHERE on the city, GROUP BY the supplier name, HAVING on the spend.")

def test_names():
    "Columns supplier and spend"
    check_columns("supplier", "spend")
''',
        "solution": "SELECT s.name AS supplier, SUM(d.quantity * m.unit_price) AS spend\nFROM deliveries d\nJOIN materials m ON d.material_id = m.id\nJOIN suppliers s ON d.supplier_id = s.id\nJOIN sites si ON d.site = si.code\nWHERE si.city = 'Riyadh'\nGROUP BY s.name\nHAVING SUM(d.quantity * m.unit_price) > 10000\nORDER BY spend DESC;\n",
        "hints": [
            "Three JOIN lines out of `deliveries`: to materials, suppliers and sites (`d.site = si.code`).",
            "Then `WHERE si.city = 'Riyadh'`, `GROUP BY s.name`, `HAVING SUM(...) > 10000`, `ORDER BY spend DESC`.",
        ],
    },
]
