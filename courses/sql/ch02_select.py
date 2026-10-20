import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Reading data with SELECT",
    "summary": "Choosing columns, renaming them, calculating new ones, and removing repeats.",
}

LESSONS = [
    {
        "id": "columns",
        "title": "Choosing columns",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`*` gives you every column. Usually you only want a few, so you list them instead, separated by commas:

```sql
SELECT name, city
FROM suppliers;
```

The columns come back in the order you list them, which doesn't have to match the table.

> **Common slips:** a comma after the last column (`SELECT name, city, FROM ...`) gives a syntax error near `FROM`. A missing comma between two columns is sneakier, as the next quiz shows.

## Your task

Show just the `name` and `unit_price` of every material, in that order.
""",
        "starter": "-- name and unit_price of every material\n",
        "tests": '''
def test_rows():
    "Returns name and unit_price for every material"
    check_rows("SELECT name, unit_price FROM materials")

def test_order():
    "Columns in the right order"
    check([c.lower() for c in COLUMNS] == ["name", "unit_price"], "List name first, then unit_price.")
''',
        "solution": "SELECT name, unit_price\nFROM materials;\n",
        "hints": [
            "Same shape as the example: `SELECT` two columns `FROM` a table.",
            "`SELECT name, unit_price FROM materials;`",
        ],
    },
    {
        "id": "missing-comma",
        "title": "The missing comma",
        "kind": "quiz",
        "body": "This one surprises everybody the first time.",
        "question": "What does this return?\n\n```sql\nSELECT name unit_price\nFROM materials;\n```",
        "options": [
            "A syntax error",
            "Two columns, name and unit_price",
            "One column of names, with the heading `unit_price`",
            "One column of prices",
        ],
        "answer": 2,
        "explain": "Without the comma, SQL reads `unit_price` as a new *heading* for the `name` column (you'll meet this properly as `AS` next lesson). So you get the material names under a column called `unit_price`, with no error to warn you. If a result looks odd, check the commas.",
    },
    {
        "id": "as",
        "title": "Renaming with AS",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`AS` gives a column a different heading in the result. The table itself doesn't change.

```sql
SELECT name AS supplier, rating AS stars
FROM suppliers;
```

The result has columns called `supplier` and `stars`. This matters more once you start calculating columns, because a calculated column has no sensible name of its own.

Keep the new names simple: lowercase, with underscores instead of spaces.

## Your task

Show every material's `name` with the heading `material`, and its `unit_price` with the heading `price_sar`.
""",
        "starter": "-- name as material, unit_price as price_sar\n",
        "tests": '''
def test_rows():
    "Right values"
    check_rows("SELECT name, unit_price FROM materials")

def test_names():
    "Headings are material and price_sar"
    check_columns("material", "price_sar")
''',
        "solution": "SELECT name AS material, unit_price AS price_sar\nFROM materials;\n",
        "hints": [
            "Put `AS new_name` straight after each column.",
            "`SELECT name AS material, unit_price AS price_sar FROM materials;`",
        ],
    },
    {
        "id": "calculated",
        "title": "Calculated columns",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A column in `SELECT` can be a calculation. The usual arithmetic works: `+`, `-`, `*`, `/`.

```sql
SELECT name, unit_price, unit_price * 10 AS price_for_10
FROM materials;
```

Each row gets its own answer, worked out from that row's values. Name the result with `AS`, otherwise its heading is the whole expression.

> **Two things to know:**
> - Any sum involving an empty value (`NULL`) gives `NULL`. Glass has no price yet, so its `price_for_10` is `NULL` too. More on `NULL` in the next chapter.
> - Dividing two whole numbers gives a whole number in SQLite: `7 / 2` is `3`. Write `7 / 2.0` if you want `3.5`.

## Your task

Prices in the table don't include VAT. Show each material's `name` and its price including 15% VAT (`unit_price * 1.15`), named `price_with_vat`.
""",
        "starter": "-- name, and unit_price * 1.15 as price_with_vat\n",
        "tests": '''
def test_rows():
    "Right prices with VAT"
    check_rows("SELECT name, unit_price * 1.15 FROM materials", hint="Multiply unit_price by 1.15.")

def test_name():
    "The calculated column is named price_with_vat"
    check_columns("name", "price_with_vat")
''',
        "solution": "SELECT name, unit_price * 1.15 AS price_with_vat\nFROM materials;\n",
        "hints": [
            "The second column is `unit_price * 1.15`, followed by `AS price_with_vat`.",
            "`SELECT name, unit_price * 1.15 AS price_with_vat FROM materials;`",
        ],
    },
    {
        "id": "round",
        "title": "Rounding",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
SQL has functions, used just like Python's: a name, then values in brackets. `ROUND(value, places)` rounds to a number of decimal places:

```sql
SELECT name, ROUND(unit_price / 3, 1) AS third
FROM materials;
```

You can wrap a whole calculation in a function. SQL works out the inside first, then rounds it.

## Your task

Same as last time, but round the VAT price to 2 decimal places. Keep the heading `price_with_vat`.
""",
        "starter": "SELECT name, unit_price * 1.15 AS price_with_vat\nFROM materials;\n",
        "tests": '''
def test_rows():
    "Prices rounded to 2 places"
    check_rows("SELECT name, ROUND(unit_price * 1.15, 2) FROM materials", hint="Wrap the calculation in ROUND(..., 2).")
    check("ROUND(" in SQL.upper(), "Use ROUND(..., 2).")

def test_name():
    "Still named price_with_vat"
    check_columns("name", "price_with_vat")
''',
        "solution": "SELECT name, ROUND(unit_price * 1.15, 2) AS price_with_vat\nFROM materials;\n",
        "hints": [
            "`ROUND(unit_price * 1.15, 2)` in place of the plain calculation.",
        ],
    },
    {
        "id": "concat",
        "title": "Joining text together",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`||` sticks pieces of text together (it's SQL's version of `+` on Python strings). Text you type yourself goes in **single** quotes:

```sql
SELECT name || ' (' || city || ')' AS label
FROM suppliers;
-- Al Noor Building Supplies (Riyadh)
```

> **Common slip:** using double quotes for text. In SQL, double quotes are for names of columns and tables. Single quotes are for text values. Stick to single quotes for text and you'll never be bitten.

## Your task

Make one column called `label` that reads like `cement per bag` for each material: the name, the words ` per `, then the unit.
""",
        "starter": "-- name || ' per ' || unit, as label\n",
        "tests": '''
def test_rows():
    "Labels like 'cement per bag'"
    check_rows("SELECT name || ' per ' || unit FROM materials", hint="Mind the spaces inside ' per '.")

def test_name():
    "Named label"
    check_columns("label")
''',
        "solution": "SELECT name || ' per ' || unit AS label\nFROM materials;\n",
        "hints": [
            "Three pieces joined with `||`: `name`, `' per '` and `unit`.",
            "`SELECT name || ' per ' || unit AS label FROM materials;`",
        ],
    },
    {
        "id": "distinct",
        "title": "DISTINCT",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`SELECT DISTINCT` removes repeated rows from the result:

```sql
SELECT city FROM suppliers;            -- Riyadh appears three times
SELECT DISTINCT city FROM suppliers;   -- each city once
```

It's the quick way to answer "which different values are there?".

## Your task

List each material **category** once.
""",
        "starter": "-- each category once\n",
        "tests": '''
def test_rows():
    "Each category once"
    check_rows("SELECT DISTINCT category FROM materials", hint="Without DISTINCT you get one row per material.")
''',
        "solution": "SELECT DISTINCT category\nFROM materials;\n",
        "hints": [
            "`DISTINCT` goes straight after `SELECT`.",
        ],
    },
    {
        "id": "distinct-quiz",
        "title": "DISTINCT on two columns",
        "kind": "quiz",
        "body": "DISTINCT looks at whole rows, not single columns.",
        "question": "What does this return?\n\n```sql\nSELECT DISTINCT site, material_id\nFROM deliveries;\n```",
        "options": [
            "Each site once",
            "Each material once",
            "Each different site-and-material pair once",
            "An error: DISTINCT only takes one column",
        ],
        "answer": 2,
        "explain": "DISTINCT removes rows that are identical in *every* listed column. `('RYD-N', 1)` and `('RYD-S', 1)` differ, so both stay. You get one row per combination of site and material that has ever been delivered.",
    },
]
