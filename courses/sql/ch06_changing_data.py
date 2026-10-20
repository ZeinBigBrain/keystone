import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Changing data",
    "summary": "Adding rows with INSERT, changing them with UPDATE, removing them with DELETE, and transactions.",
}

LESSONS = [
    {
        "id": "insert",
        "title": "INSERT",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`INSERT` adds a row. Name the columns you're filling, then give the values in the same order:

```sql
INSERT INTO sites (code, name, city)
VALUES ('DMM-1', 'Gulf Yard', 'Dammam');
```

You can leave out a column whose value is filled in for you. The `id` column in our tables is an `INTEGER PRIMARY KEY`, and SQLite gives every new row the next free number automatically.

An `INSERT` doesn't return any rows, so **Run** just reports `(1 row changed)`. To see the result, add a `SELECT` after it in the same editor. Each run starts from a fresh database, so you can run it as often as you like.

```sql
INSERT INTO sites (code, name, city) VALUES ('DMM-1', 'Gulf Yard', 'Dammam');
SELECT * FROM sites;
```

## Your task

Add a supplier called `Eastern Fixings`, based in `Dammam`, with a rating of `4`. Let SQLite choose the id.
""",
        "starter": "-- INSERT INTO suppliers (name, city, rating) VALUES (...);\n\nSELECT * FROM suppliers;\n",
        "tests": '''
def test_row():
    "Eastern Fixings is in the table"
    rows = query("SELECT city, rating FROM suppliers WHERE name = 'Eastern Fixings'")
    check(len(rows) == 1, "I found %d supplier(s) called 'Eastern Fixings'. Expected exactly 1. Check the spelling and capitals." % len(rows))
    check(rows[0] == ("Dammam", 4), "Eastern Fixings has city and rating %r, expected ('Dammam', 4)." % (rows[0],))

def test_count():
    "Nothing else changed"
    n = query("SELECT COUNT(*) FROM suppliers")[0][0]
    check(n == 7, "There should be 7 suppliers now, but there are %d." % n)
''',
        "solution": "INSERT INTO suppliers (name, city, rating)\nVALUES ('Eastern Fixings', 'Dammam', 4);\n\nSELECT * FROM suppliers;\n",
        "hints": [
            "Three columns, three values, in the same order. Text in single quotes, the number without.",
            "`INSERT INTO suppliers (name, city, rating) VALUES ('Eastern Fixings', 'Dammam', 4);`",
        ],
    },
    {
        "id": "insert-many",
        "title": "Several rows at once",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
One `INSERT` can add several rows. Put a comma between each bracketed set of values:

```sql
INSERT INTO sites (code, name, city)
VALUES ('DMM-1', 'Gulf Yard', 'Dammam'),
       ('MED-1', 'Garden Court', 'Madinah');
```

> **Common slip:** a different number of values from columns. Three columns means every bracket needs exactly three values.

## Your task

Add two materials in one statement:

| name | category | unit | unit_price |
|---|---|---|---|
| mortar | binder | bag | 14.0 |
| plasterboard | finishes | m2 | 27.5 |
""",
        "starter": "-- add mortar and plasterboard in one INSERT\n\nSELECT * FROM materials;\n",
        "tests": '''
def test_rows():
    "Both new materials are there"
    rows = query("SELECT name, category, unit, unit_price FROM materials WHERE name IN ('mortar', 'plasterboard') ORDER BY name")
    want = [("mortar", "binder", "bag", 14.0), ("plasterboard", "finishes", "m2", 27.5)]
    check(rows == want, "Found %r\\nexpected %r" % (rows, want))
    check(query("SELECT COUNT(*) FROM materials")[0][0] == 11, "There should be 11 materials now.")

def test_one_statement():
    "One INSERT statement"
    check(SQL.upper().count("INSERT") == 1, "Add both rows with a single INSERT.")
''',
        "solution": "INSERT INTO materials (name, category, unit, unit_price)\nVALUES ('mortar', 'binder', 'bag', 14.0),\n       ('plasterboard', 'finishes', 'm2', 27.5);\n\nSELECT * FROM materials;\n",
        "hints": [
            "Columns: `(name, category, unit, unit_price)`. Then two bracketed sets of four values after `VALUES`, with a comma between them.",
        ],
    },
    {
        "id": "insert-quiz",
        "title": "Leaving out the column list",
        "kind": "quiz",
        "body": """
You *can* write an INSERT without naming the columns:

```sql
INSERT INTO sites VALUES ('DMM-1', 'Gulf Yard', 'Dammam');
```

Then the values must match every column of the table, in the table's order.
""",
        "question": "Why is it better to name the columns anyway?",
        "options": [
            "It runs faster",
            "If someone adds or reorders columns later, the INSERT still puts each value in the right place (or fails clearly)",
            "SQLite requires it for text values",
            "It stops duplicate rows",
        ],
        "answer": 1,
        "explain": "Without a column list, the INSERT silently depends on the table's current column order. Add a column later and every such INSERT breaks, or worse, puts values in the wrong columns. Naming the columns makes the statement say exactly what it means.",
    },
    {
        "id": "update",
        "title": "UPDATE",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`UPDATE` changes values in existing rows. `SET` says what to change, `WHERE` says which rows:

```sql
UPDATE suppliers
SET rating = 5
WHERE name = 'Najd Timber';
```

To change two columns, separate them with commas: `SET city = 'Jubail', rating = 3`.

> **The most expensive slip in SQL:** forgetting the `WHERE`. Then **every row** gets updated. A safe habit: write and run `SELECT * FROM suppliers WHERE name = 'Najd Timber';` first, check it returns exactly the rows you mean, then turn it into the UPDATE.

## Your task

The price of paint has gone up. Set paint's `unit_price` to `24.0`, without touching any other material.
""",
        "starter": "-- 1. check which rows your WHERE picks:\nSELECT * FROM materials WHERE name = 'paint';\n\n-- 2. then write the UPDATE\n",
        "tests": '''
def test_paint():
    "Paint costs 24.0"
    p = query("SELECT unit_price FROM materials WHERE name = 'paint'")[0][0]
    check(p == 24.0, "Paint's price is %r, expected 24.0." % p)

def test_others():
    "Every other material is unchanged"
    now = query("SELECT name, unit_price FROM materials WHERE name <> 'paint' ORDER BY id")
    _, before = fresh("SELECT name, unit_price FROM materials WHERE name <> 'paint' ORDER BY id")
    check(now == before, "Other materials changed too. Did the UPDATE have a WHERE?")
''',
        "solution": "SELECT * FROM materials WHERE name = 'paint';\n\nUPDATE materials\nSET unit_price = 24.0\nWHERE name = 'paint';\n",
        "hints": [
            "`UPDATE materials SET unit_price = 24.0 WHERE name = 'paint';`",
        ],
    },
    {
        "id": "update-quiz",
        "title": "UPDATE without WHERE",
        "kind": "quiz",
        "body": "One question to make the warning stick.",
        "question": "What does this do?\n\n```sql\nUPDATE staff SET site = 'JED-1';\n```",
        "options": [
            "Nothing, it's missing a WHERE so SQL refuses",
            "Moves the first member of staff to JED-1",
            "Moves every member of staff to JED-1",
            "Adds a new row with site JED-1",
        ],
        "answer": 2,
        "explain": "With no WHERE, the UPDATE applies to every row. SQL doesn't ask if you're sure. In a real database the only way back is a backup, or a transaction you haven't committed yet (later in this chapter).",
    },
    {
        "id": "update-calc",
        "title": "Updating with a calculation",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
The new value can be worked out from the old one, row by row:

```sql
UPDATE staff
SET years = years + 1
WHERE site = 'RYD-S';     -- everyone at RYD-S gets one more year
```

## Your task

Aggregate prices are going up by 10%. Multiply the `unit_price` of every material in the `aggregate` category by `1.10`.
""",
        "starter": "-- check first:\nSELECT name, unit_price FROM materials WHERE category = 'aggregate';\n\n-- then the UPDATE\n",
        "tests": '''
def test_prices():
    "Aggregates are 10% dearer, everything else unchanged"
    now = query("SELECT name, ROUND(unit_price, 6) FROM materials ORDER BY id")
    _, want = fresh("SELECT name, ROUND(CASE WHEN category = 'aggregate' THEN unit_price * 1.10 ELSE unit_price END, 6) FROM materials ORDER BY id")
    check(now == want, "Prices are now %r\\nexpected %r" % (now, want))
''',
        "solution": "SELECT name, unit_price FROM materials WHERE category = 'aggregate';\n\nUPDATE materials\nSET unit_price = unit_price * 1.10\nWHERE category = 'aggregate';\n",
        "hints": [
            "`SET unit_price = unit_price * 1.10` with `WHERE category = 'aggregate'`.",
        ],
    },
    {
        "id": "delete",
        "title": "DELETE",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`DELETE` removes whole rows. Same shape, same warning:

```sql
DELETE FROM deliveries
WHERE id = 7;
```

`DELETE FROM deliveries;` with no WHERE empties the whole table.

Our tables have **foreign keys**: a delivery points at a material by its id. So SQLite won't let you delete a material that deliveries still point at. You'd get `FOREIGN KEY constraint failed`, which is the database protecting you from orphaned rows.

## Your task

Delete every delivery dated **before** 3 October 2026.
""",
        "starter": "-- check first:\nSELECT * FROM deliveries WHERE delivery_date < '2026-10-03';\n\n-- then the DELETE\n",
        "tests": '''
def test_gone():
    "No deliveries before the 3rd"
    n = query("SELECT COUNT(*) FROM deliveries WHERE delivery_date < '2026-10-03'")[0][0]
    check(n == 0, "%d delivery(s) before 3 October are still there." % n)

def test_kept():
    "Everything from the 3rd onwards is kept"
    n = query("SELECT COUNT(*) FROM deliveries")[0][0]
    _, want = fresh("SELECT COUNT(*) FROM deliveries WHERE delivery_date >= '2026-10-03'")
    check(n == want[0][0], "There are %d deliveries left, expected %d. Deliveries on the 3rd itself should stay." % (n, want[0][0]))
''',
        "solution": "SELECT * FROM deliveries WHERE delivery_date < '2026-10-03';\n\nDELETE FROM deliveries\nWHERE delivery_date < '2026-10-03';\n",
        "hints": [
            "`DELETE FROM deliveries WHERE delivery_date < '2026-10-03';`",
        ],
    },
    {
        "id": "transactions",
        "title": "Transactions",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Some changes only make sense together. Recording a new material **and** its first delivery, say: if the second statement fails, you don't want the first one left behind on its own.

A **transaction** groups statements so they happen all together or not at all:

```sql
BEGIN;
UPDATE staff SET site = 'RYD-S' WHERE name = 'Karim';
UPDATE staff SET manager_id = 6 WHERE name = 'Karim';
COMMIT;
```

- `BEGIN` starts the transaction.
- `COMMIT` makes everything since `BEGIN` permanent.
- `ROLLBACK` instead of `COMMIT` throws it all away, as if none of it happened.

Until you commit, nobody else using the database sees your changes.

## Your task

In one transaction:

1. add a material `mesh` (category `steel`, unit `sheet`, unit_price `85.0`) with id `10`,
2. add delivery `25`: dated `2026-10-20`, site `RYD-N`, material `10`, supplier `2`, quantity `40`,
3. commit.
""",
        "starter": "BEGIN;\n\n-- 1. INSERT the material (give it id 10)\n\n-- 2. INSERT the delivery (id 25)\n\n-- 3. COMMIT\n",
        "tests": '''
def test_rows():
    "The material and delivery are both there"
    m = query("SELECT name, category, unit, unit_price FROM materials WHERE id = 10")
    check(m == [("mesh", "steel", "sheet", 85.0)], "Material 10 is %r." % (m,))
    d = query("SELECT delivery_date, site, material_id, supplier_id, quantity FROM deliveries WHERE id = 25")
    check(d == [("2026-10-20", "RYD-N", 10, 2, 40)], "Delivery 25 is %r." % (d,))

def test_transaction():
    "Wrapped in BEGIN and COMMIT"
    up = SQL.upper()
    check("BEGIN" in up and "COMMIT" in up, "Start with BEGIN; and finish with COMMIT;.")
    check(not db.in_transaction, "The transaction is still open. Finish with COMMIT;.")
''',
        "solution": "BEGIN;\n\nINSERT INTO materials (id, name, category, unit, unit_price)\nVALUES (10, 'mesh', 'steel', 'sheet', 85.0);\n\nINSERT INTO deliveries (id, delivery_date, site, material_id, supplier_id, quantity)\nVALUES (25, '2026-10-20', 'RYD-N', 10, 2, 40);\n\nCOMMIT;\n",
        "hints": [
            "Name the id column in each INSERT so you can give it a value: `INSERT INTO materials (id, name, category, unit, unit_price) VALUES (10, 'mesh', ...)`.",
            "The delivery has six columns: id, delivery_date, site, material_id, supplier_id, quantity.",
        ],
    },
    {
        "id": "rollback-quiz",
        "title": "ROLLBACK",
        "kind": "quiz",
        "body": "Trace it statement by statement.",
        "question": "There are 24 deliveries. What does the last line show?\n\n```sql\nBEGIN;\nDELETE FROM deliveries;\nROLLBACK;\nSELECT COUNT(*) FROM deliveries;\n```",
        "options": ["`0`", "`24`", "An error", "`1`"],
        "answer": 1,
        "explain": "The DELETE did empty the table, but only inside the transaction. ROLLBACK undid everything since BEGIN, so all 24 rows are back. (Had it been COMMIT, they'd be gone for good.)",
    },
    {
        "id": "change-task",
        "title": "Chapter task: tidying the records",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Three fixes that came in from the site office. Do all three in one transaction.

## Your task

1. `Red Sea Materials` has now been rated: set its rating to `4`.
2. Delivery `21` was entered twice over: halve its quantity.
3. Remove every delivery with a quantity **under 3** (they were test entries).

Then commit.
""",
        "starter": "",
        "tests": '''
def test_rating():
    "Red Sea Materials is rated 4"
    r = query("SELECT rating FROM suppliers WHERE name = 'Red Sea Materials'")
    check(r == [(4,)], "Red Sea Materials' rating is %r." % (r,))
    _, before = fresh("SELECT name, rating FROM suppliers WHERE name <> 'Red Sea Materials' ORDER BY id")
    check(query("SELECT name, rating FROM suppliers WHERE name <> 'Red Sea Materials' ORDER BY id") == before,
          "Other suppliers changed too.")

def test_halved():
    "Delivery 21 is halved"
    q = query("SELECT quantity FROM deliveries WHERE id = 21")
    check(q == [(45.0,)] or q == [(45,)], "Delivery 21 has quantity %r, expected 45." % (q,))

def test_small_gone():
    "Small deliveries removed, the rest kept"
    check(query("SELECT COUNT(*) FROM deliveries WHERE quantity < 3")[0][0] == 0, "Some deliveries under 3 are still there.")
    _, want = fresh("SELECT COUNT(*) FROM deliveries WHERE quantity >= 3")
    n = query("SELECT COUNT(*) FROM deliveries")[0][0]
    check(n == want[0][0], "%d deliveries left, expected %d." % (n, want[0][0]))

def test_committed():
    "Done in a committed transaction"
    check("BEGIN" in SQL.upper() and "COMMIT" in SQL.upper() and not db.in_transaction,
          "Wrap the three changes in BEGIN; ... COMMIT;.")
''',
        "solution": "BEGIN;\n\nUPDATE suppliers SET rating = 4 WHERE name = 'Red Sea Materials';\n\nUPDATE deliveries SET quantity = quantity / 2 WHERE id = 21;\n\nDELETE FROM deliveries WHERE quantity < 3;\n\nCOMMIT;\n",
        "hints": [
            "Two UPDATEs and a DELETE between `BEGIN;` and `COMMIT;`. Each one needs its own WHERE.",
            "Halving: `SET quantity = quantity / 2 WHERE id = 21`.",
        ],
    },
]
