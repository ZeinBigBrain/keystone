import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "What a database is",
    "summary": "Tables, rows and columns, the practice database, and your first queries.",
}

LESSONS = [
    {
        "id": "sql-welcome",
        "title": "Tables, rows and columns",
        "kind": "read",
        "body": """
A **database** stores data in **tables**. A table looks a lot like a spreadsheet tab:

| id | name | unit | unit_price |
|---|---|---|---|
| 1 | cement | bag | 18.5 |
| 2 | sand | t | 45.0 |
| 3 | gravel | t | 52.0 |

- Each **row** is one thing: one material, one delivery, one person.
- Each **column** is one fact about it, and every value in a column has the same type.
- Most tables have an **id** column, a number that identifies each row and never repeats.

## Why not just use a spreadsheet?

For a few hundred rows that one person edits, a spreadsheet is fine. Databases earn their keep when:

- the data is big (millions of rows don't slow it down much),
- several people or programs read and write at the same time,
- you need rules enforced, like "every delivery must point at a real site",
- you want to ask questions of the data quickly and repeatably.

## SQL

You talk to a database in **SQL** (people say "sequel" or "S-Q-L"). Instead of clicking around, you write a sentence describing what you want, and the database works out how to get it:

```sql
SELECT name, unit_price FROM materials WHERE unit_price > 40;
```

This track uses **SQLite**, a database that comes built into Python. Each database is a single file, and there's nothing to install.

## How SQL exercises work

The editor in SQL lessons takes SQL, not Python. **Run** sends your SQL to a fresh copy of the practice database and shows the rows that come back as a table. **Submit** checks your result. Nothing you do can damage anything: every run starts from a clean copy.
""",
    },
    {
        "id": "sql-first-query",
        "title": "Your first query",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
The simplest question you can ask a database is "show me everything in this table":

```sql
SELECT * FROM sites;
```

Read it as: **select** every column (`*` means "all of them") **from** the `sites` table. The semicolon marks the end of the statement.

Run that and you get every row of `sites`, with every column.

## Your task

Show every row and every column of the `materials` table.
""",
        "starter": "-- show everything in the materials table\n",
        "tests": '''
def test_rows():
    "Returns every material, with every column"
    check_rows("SELECT * FROM materials", hint="Use SELECT * FROM materials.")

def test_table():
    "Reads from materials"
    check("FROM MATERIALS" in SQL.upper(), "Select from the materials table.")
''',
        "solution": "SELECT * FROM materials;\n",
        "hints": [
            "Same shape as the example, with a different table name.",
            "`SELECT * FROM materials;`",
        ],
    },
    {
        "id": "sql-tables",
        "title": "The practice database",
        "kind": "read",
        "body": """
Most of this track uses one practice database: a small construction company with three sites. Come back to this page whenever you need to check a column name.

## sites

| column | holds |
|---|---|
| `code` | short code like `'RYD-N'`, the id for this table |
| `name` | e.g. `'North Plaza'` |
| `city` | `'Riyadh'` or `'Jeddah'` |

## materials

| column | holds |
|---|---|
| `id` | 1 to 9 |
| `name` | `'cement'`, `'sand'`, `'rebar'` ... |
| `category` | `'binder'`, `'aggregate'`, `'steel'`, `'masonry'`, `'formwork'`, `'finishes'` |
| `unit` | what it's sold by: `'bag'`, `'t'`, `'m2'` ... |
| `unit_price` | price per unit in SAR (one material has no price yet) |

## suppliers

| column | holds |
|---|---|
| `id` | 1 to 6 |
| `name` | company name |
| `city` | where they're based |
| `rating` | 1 to 5, or empty for new suppliers |

## deliveries

| column | holds |
|---|---|
| `id` | 1 to 24 |
| `delivery_date` | text like `'2026-10-05'` |
| `site` | which site, matching `sites.code` |
| `material_id` | which material, matching `materials.id` |
| `supplier_id` | which supplier, matching `suppliers.id` |
| `quantity` | how many units arrived |

## staff

| column | holds |
|---|---|
| `id` | 1 to 10 |
| `name`, `role` | e.g. `'Karim'`, `'site engineer'` |
| `site` | where they work |
| `years` | years of experience |
| `manager_id` | the `id` of their manager in this same table, or empty for the top managers |

Notice that `deliveries` doesn't repeat the material's name or the supplier's city. It just stores their ids and points at the other tables. You'll see why that's a good idea, and how to put the pieces back together, later in the track.
""",
    },
    {
        "id": "sql-which-table",
        "title": "Which table?",
        "kind": "quiz",
        "body": "Use the page you just read.",
        "question": "You want to know how many bags of cement arrived at North Plaza on 7 October. Which table holds the quantity?",
        "options": ["`materials`", "`sites`", "`deliveries`", "`suppliers`"],
        "answer": 2,
        "explain": "Each delivery row has a date, a site, a material and a quantity, so the number you want lives in `deliveries`. You'd need `materials` too, to know that material 1 is cement, but the quantity itself is in `deliveries`.",
    },
    {
        "id": "sql-another-table",
        "title": "Case and semicolons",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A few things SQL doesn't mind about, and one it does:

- **Keywords don't care about case.** `SELECT`, `select` and `Select` all work. Most people write keywords in capitals so they stand out from table and column names.
- **Spacing and line breaks don't matter.** Long queries are usually split over several lines.
- **The semicolon** ends a statement. With one statement it's optional here, but with several it's how SQL knows where one stops and the next starts. Get in the habit of always adding it.
- **Spelling of table and column names does matter.** `FROM supplier` (no s) gives `no such table: supplier`.

```sql
select *
from sites;
```

## Your task

Show everything in the `suppliers` table. Spread it over two lines, the way the example does.
""",
        "starter": "-- show everything in the suppliers table, over two lines\n",
        "tests": '''
def test_rows():
    "Returns every supplier"
    check_rows("SELECT * FROM suppliers", hint="Select everything from suppliers.")

def test_two_lines():
    "Written over more than one line"
    lines = [l for l in RAW_CODE.splitlines() if l.strip() and not l.strip().startswith("--")]
    check(len(lines) >= 2, "Put FROM on its own line, like the example.")
''',
        "solution": "SELECT *\nFROM suppliers;\n",
        "hints": [
            "Line one: `SELECT *`. Line two: `FROM suppliers;`",
        ],
    },
    {
        "id": "sql-star-quiz",
        "title": "Reading a query",
        "kind": "quiz",
        "body": "One last check before you start choosing columns.",
        "question": "What does `select * from STAFF;` do?",
        "options": [
            "Fails, because keywords must be capitals",
            "Fails, because the table name is in capitals",
            "Shows every column of every row in the staff table",
            "Shows only the first column of staff",
        ],
        "answer": 2,
        "explain": "Keywords can be any case, and SQLite also ignores case in table names, so this is just `SELECT * FROM staff`. The `*` means all columns. (Values inside quotes are different: `'Riyadh'` and `'riyadh'` are not the same text.)",
    },
]
