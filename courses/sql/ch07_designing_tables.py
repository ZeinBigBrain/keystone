import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Designing tables",
    "summary": "CREATE TABLE, column types, primary keys, constraints, foreign keys, splitting data across tables, and ALTER TABLE.",
}

# Shared helpers for the checks in this chapter
HELPERS = '''
import sqlite3

def columns(table):
    return [(r[1], (r[2] or "").upper()) for r in query("PRAGMA table_info(%s)" % table)]

def table_exists(table):
    return bool(query("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % table))

def rejected(sql):
    """True if the database refuses this statement (a constraint stops it)."""
    try:
        db.execute("SAVEPOINT t")
        db.execute(sql)
    except sqlite3.IntegrityError:
        db.execute("ROLLBACK TO t")
        db.execute("RELEASE t")
        return True
    db.execute("ROLLBACK TO t")
    db.execute("RELEASE t")
    return False
'''

LESSONS = [
    {
        "id": "types",
        "title": "Column types",
        "kind": "read",
        "body": """
Up to now you've used tables someone else designed. This chapter is about designing your own.

Every column gets a **type**. SQLite keeps it simple:

| Type | Holds | Python equivalent |
|---|---|---|
| `INTEGER` | whole numbers | `int` |
| `REAL` | decimals | `float` |
| `TEXT` | text | `str` |
| `BLOB` | raw bytes, like an image | `bytes` |

A few conventions fill the gaps:

- **Dates** are stored as `TEXT` in the form `'2026-10-17'`. That form sorts correctly, and SQLite's date functions understand it.
- **True or false** is stored as `INTEGER`, `1` or `0`.
- **Money** is often stored as `INTEGER` in the smallest unit (halalas, cents) to avoid float rounding, or as `REAL` when exact pennies don't matter.

SQLite is unusually relaxed: it will actually let you put text in an `INTEGER` column. Other databases won't, and you shouldn't rely on it. Declare the type you mean and stick to it.

## Naming

Table names are usually plural nouns (`deliveries`, `staff`), column names are lowercase with underscores (`unit_price`), and the id column is just `id`. A column that points at another table's id is named after it: `material_id`, `supplier_id`.
""",
    },
    {
        "id": "create-table",
        "title": "CREATE TABLE",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`CREATE TABLE` gives the table a name, then lists its columns in brackets, each with a type, separated by commas:

```sql
CREATE TABLE visitors (
    id INTEGER PRIMARY KEY,
    name TEXT,
    company TEXT,
    visit_date TEXT
);
```

(`PRIMARY KEY` is explained in the next lesson. For now: every table gets an `id INTEGER PRIMARY KEY` column first.)

> **Common slips:** a comma after the last column (syntax error near `)`), and forgetting the closing bracket (`incomplete input`).

## Your task

Create a table called `inspections` with four columns:

| column | type |
|---|---|
| `id` | `INTEGER PRIMARY KEY` |
| `site` | `TEXT` |
| `inspected_on` | `TEXT` |
| `passed` | `INTEGER` |
""",
        "starter": "CREATE TABLE inspections (\n    id INTEGER PRIMARY KEY\n    -- add the other three columns\n);\n",
        "tests": HELPERS + '''
def test_exists():
    "The inspections table exists"
    check(table_exists("inspections"), "I can't find a table called inspections.")

def test_columns():
    "It has the four columns with the right types"
    want = [("id", "INTEGER"), ("site", "TEXT"), ("inspected_on", "TEXT"), ("passed", "INTEGER")]
    got = columns("inspections")
    check(got == want, "Columns are %r\\nexpected %r" % (got, want))
''',
        "solution": "CREATE TABLE inspections (\n    id INTEGER PRIMARY KEY,\n    site TEXT,\n    inspected_on TEXT,\n    passed INTEGER\n);\n",
        "hints": [
            "Put a comma after `id INTEGER PRIMARY KEY`, then one line per column: name, space, type.",
            "No comma after the last column, `passed INTEGER`.",
        ],
    },
    {
        "id": "primary-key",
        "title": "Primary keys",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A **primary key** is the column that identifies each row. No two rows can share a value, and it can't be empty. Everything else in the database refers to a row by its key: a delivery says "material 4", not "the steel thing that costs 2950".

In SQLite, a column declared `INTEGER PRIMARY KEY` has a bonus: leave it out when you insert, and it fills itself in with the next number.

```sql
CREATE TABLE visitors (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO visitors (name) VALUES ('Ali'), ('Mona');
SELECT * FROM visitors;
-- 1 | Ali
-- 2 | Mona
```

Sometimes a natural value works as the key instead. `sites` uses its short `code` (`'RYD-N'`) as a `TEXT PRIMARY KEY`.

## Your task

1. Create a table `plant` with columns `id INTEGER PRIMARY KEY`, `name TEXT` and `day_rate REAL`.
2. Insert an `excavator` at `1200` a day and a `crane` at `3500`, **without** giving ids.
3. Select everything from `plant` to see the ids SQLite chose.
""",
        "starter": "-- 1. CREATE TABLE plant (...);\n\n-- 2. INSERT the two machines, leaving out id\n\n-- 3. SELECT * FROM plant;\n",
        "tests": HELPERS + '''
def test_table():
    "plant has the right columns"
    check(table_exists("plant"), "Create a table called plant.")
    want = [("id", "INTEGER"), ("name", "TEXT"), ("day_rate", "REAL")]
    check(columns("plant") == want, "Columns are %r, expected %r." % (columns("plant"), want))

def test_rows():
    "Both machines got automatic ids"
    rows = query("SELECT id, name, day_rate FROM plant ORDER BY id")
    check(rows == [(1, "excavator", 1200.0), (2, "crane", 3500.0)], "plant holds %r." % (rows,))
''',
        "solution": "CREATE TABLE plant (\n    id INTEGER PRIMARY KEY,\n    name TEXT,\n    day_rate REAL\n);\n\nINSERT INTO plant (name, day_rate)\nVALUES ('excavator', 1200), ('crane', 3500);\n\nSELECT * FROM plant;\n",
        "hints": [
            "The INSERT names only the two columns you're filling: `INSERT INTO plant (name, day_rate) VALUES ...`.",
        ],
    },
    {
        "id": "constraints",
        "title": "NOT NULL, UNIQUE, DEFAULT, CHECK",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
**Constraints** are rules the database enforces on every insert and update. Bad data gets refused at the door instead of turning up in a report months later.

| Constraint | Means |
|---|---|
| `NOT NULL` | a value must be given |
| `UNIQUE` | no two rows can have the same value |
| `DEFAULT x` | if no value is given, use `x` |
| `CHECK (test)` | the row is refused unless the test is true |

They go after the column's type, and you can combine them:

```sql
CREATE TABLE visitors (
    id INTEGER PRIMARY KEY,
    badge_no TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    escorted INTEGER NOT NULL DEFAULT 1,
    hours REAL CHECK (hours > 0)
);
```

## Your task

Create a table `permits`:

| column | rules |
|---|---|
| `id` | `INTEGER PRIMARY KEY` |
| `ref` | text, must be given, no two permits with the same ref |
| `status` | text, must be given, defaults to `'open'` |
| `valid_days` | integer, must be more than 0 |

The checks will try inserting good and bad rows to see what your table lets through.
""",
        "starter": "CREATE TABLE permits (\n    id INTEGER PRIMARY KEY,\n    ref TEXT,\n    status TEXT,\n    valid_days INTEGER\n);\n-- add the rules to the columns above\n",
        "tests": HELPERS + '''
def test_good_row():
    "A normal permit goes in, and status defaults to open"
    check(table_exists("permits"), "Create a table called permits.")
    db.execute("INSERT INTO permits (ref, valid_days) VALUES ('PTW-001', 7)")
    rows = query("SELECT ref, status, valid_days FROM permits WHERE ref = 'PTW-001'")
    check(rows == [("PTW-001", "open", 7)], "After inserting ref 'PTW-001' with 7 days, the row is %r. Is status defaulting to 'open'?" % (rows,))

def test_ref_rules():
    "ref must be given and unique"
    db.execute("INSERT INTO permits (ref, valid_days) VALUES ('PTW-100', 3)")
    check(rejected("INSERT INTO permits (ref, valid_days) VALUES ('PTW-100', 5)"), "A second permit with ref 'PTW-100' was allowed. ref needs UNIQUE.")
    check(rejected("INSERT INTO permits (valid_days) VALUES (5)"), "A permit with no ref was allowed. ref needs NOT NULL.")

def test_status_rule():
    "status can't be set to NULL"
    check(rejected("INSERT INTO permits (ref, status, valid_days) VALUES ('PTW-200', NULL, 5)"), "status was allowed to be NULL. It needs NOT NULL as well as the DEFAULT.")

def test_days_rule():
    "valid_days must be more than 0"
    check(rejected("INSERT INTO permits (ref, valid_days) VALUES ('PTW-300', 0)"), "valid_days of 0 was allowed. Add CHECK (valid_days > 0).")
''',
        "solution": "CREATE TABLE permits (\n    id INTEGER PRIMARY KEY,\n    ref TEXT NOT NULL UNIQUE,\n    status TEXT NOT NULL DEFAULT 'open',\n    valid_days INTEGER CHECK (valid_days > 0)\n);\n",
        "hints": [
            "`ref TEXT NOT NULL UNIQUE` and `status TEXT NOT NULL DEFAULT 'open'`.",
            "`valid_days INTEGER CHECK (valid_days > 0)`",
        ],
    },
    {
        "id": "constraint-quiz",
        "title": "Which rule?",
        "kind": "quiz",
        "body": "Match the rule to the problem.",
        "question": "Two staff members were accidentally given the same badge number. Which constraint on `badge_no` would have stopped it?",
        "options": ["`NOT NULL`", "`DEFAULT`", "`UNIQUE`", "`CHECK (badge_no > 0)`"],
        "answer": 2,
        "explain": "`UNIQUE` refuses a value that's already in that column. `NOT NULL` only stops empty values, and `DEFAULT` only fills in missing ones.",
    },
    {
        "id": "foreign-keys",
        "title": "Foreign keys",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A **foreign key** is a column that points at another table's primary key. `REFERENCES` makes the database check it: a value is only allowed if that row really exists.

```sql
CREATE TABLE site_visits (
    id INTEGER PRIMARY KEY,
    site TEXT NOT NULL REFERENCES sites(code),
    visit_date TEXT NOT NULL
);
INSERT INTO site_visits (site, visit_date) VALUES ('RYD-N', '2026-10-20');  -- fine
INSERT INTO site_visits (site, visit_date) VALUES ('XYZ', '2026-10-20');    -- refused
```

Read `REFERENCES sites(code)` as "must match a `code` in `sites`". It also works the other way: a site can't be deleted while visits still point at it.

> SQLite only enforces foreign keys after `PRAGMA foreign_keys = ON;`. Keystone turns that on for you. In your own programs, run it each time you connect.

## Your task

Create the `inspections` table again, with rules this time:

| column | rules |
|---|---|
| `id` | `INTEGER PRIMARY KEY` |
| `site` | text, must be given, must be a real site code |
| `inspected_on` | text, must be given |
| `passed` | integer, must be given, and must be `0` or `1` |

For the last one, `CHECK (passed IN (0, 1))` does it.
""",
        "starter": "CREATE TABLE inspections (\n    id INTEGER PRIMARY KEY,\n    site TEXT,\n    inspected_on TEXT,\n    passed INTEGER\n);\n",
        "tests": HELPERS + '''
def test_good():
    "A proper inspection goes in"
    check(table_exists("inspections"), "Create a table called inspections.")
    db.execute("INSERT INTO inspections (site, inspected_on, passed) VALUES ('RYD-N', '2026-10-20', 1)")
    check(query("SELECT COUNT(*) FROM inspections")[0][0] == 1, "A valid inspection should be accepted.")

def test_site_must_exist():
    "site must be a real site"
    check(rejected("INSERT INTO inspections (site, inspected_on, passed) VALUES ('XYZ', '2026-10-20', 1)"),
          "An inspection at site 'XYZ' was allowed. Add REFERENCES sites(code).")
    check(rejected("INSERT INTO inspections (inspected_on, passed) VALUES ('2026-10-20', 1)"), "site must be NOT NULL.")

def test_other_rules():
    "inspected_on is required, passed is 0 or 1"
    check(rejected("INSERT INTO inspections (site, passed) VALUES ('RYD-N', 1)"), "inspected_on must be NOT NULL.")
    check(rejected("INSERT INTO inspections (site, inspected_on, passed) VALUES ('RYD-N', '2026-10-20', 2)"), "passed = 2 was allowed. Add CHECK (passed IN (0, 1)).")
    check(rejected("INSERT INTO inspections (site, inspected_on) VALUES ('RYD-N', '2026-10-20')"), "passed must be NOT NULL.")
''',
        "solution": "CREATE TABLE inspections (\n    id INTEGER PRIMARY KEY,\n    site TEXT NOT NULL REFERENCES sites(code),\n    inspected_on TEXT NOT NULL,\n    passed INTEGER NOT NULL CHECK (passed IN (0, 1))\n);\n",
        "hints": [
            "`site TEXT NOT NULL REFERENCES sites(code)`",
            "`passed INTEGER NOT NULL CHECK (passed IN (0, 1))`",
        ],
    },
    {
        "id": "normalisation",
        "title": "Splitting data across tables",
        "kind": "read",
        "body": """
Why does `deliveries` store `supplier_id = 3` instead of the supplier's name and city? Picture the alternative, one wide table like a spreadsheet:

| delivery_date | material | supplier | supplier_city | quantity |
|---|---|---|---|---|
| 2026-10-01 | sand | Desert Aggregates | Riyadh | 12 |
| 2026-10-03 | gravel | Desert Aggregates | Riyadh | 18 |
| 2026-10-05 | sand | Desert Aggregates | Riyadh | 20 |

Problems show up fast:

- **Repetition.** "Desert Aggregates, Riyadh" is stored on every one of its deliveries.
- **Updates go wrong.** If the supplier moves, you have to change every row. Miss one and the data now disagrees with itself.
- **Typos create ghosts.** One row says "Desert Agregates" and suddenly reports show two suppliers.
- **You can't record things on their own.** A new supplier with no deliveries yet has nowhere to live.

The fix is **normalisation**: store each fact once, in the table it belongs to, and link tables by id.

- Supplier facts (name, city, rating) live in `suppliers`, once each.
- Each delivery stores only `supplier_id`, a pointer to that row.

Moving a supplier is now a one-row `UPDATE`. A supplier with no deliveries is just a row in `suppliers`.

## A rule of thumb

If you find yourself typing the same group of values on many rows, those values probably belong in their own table, with an id that the rows point at.

The cost is that answers now need data from several tables at once. That's what **joins** are for, and they're the next chapter.
""",
    },
    {
        "id": "normalise-quiz",
        "title": "Spot the design problem",
        "kind": "quiz",
        "body": "Apply the rule of thumb.",
        "question": "A `staff` table has columns `name`, `site_code`, `site_name` and `site_city`. What's the better design?",
        "options": [
            "Keep it, it's easier to read",
            "Keep `site_code`, and move `site_name` and `site_city` into a `sites` table keyed by code",
            "Delete `site_code` and keep the name and city",
            "Make one table per site",
        ],
        "answer": 1,
        "explain": "Site name and city are facts about the *site*, repeated on every staff row. Store them once in `sites`, and let each staff row point at its site by code. That's exactly how the practice database does it.",
    },
    {
        "id": "alter",
        "title": "ALTER TABLE",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Tables can change after they're made. The two changes you'll use most:

```sql
ALTER TABLE suppliers ADD COLUMN phone TEXT;          -- existing rows get NULL
ALTER TABLE suppliers RENAME COLUMN phone TO tel;
```

A new column can have a `DEFAULT`, which existing rows then get instead of `NULL`.

To remove a whole table: `DROP TABLE plant;`. Add `IF EXISTS` so it doesn't fail when the table isn't there: `DROP TABLE IF EXISTS plant;`. There's no undo, so be sure.

## Your task

1. Add a column `min_stock` to `materials`: an `INTEGER` with a default of `0`.
2. Set cement's `min_stock` to `50`.
""",
        "starter": "-- 1. ALTER TABLE ... ADD COLUMN ...\n\n-- 2. UPDATE cement's min_stock\n\nSELECT name, min_stock FROM materials;\n",
        "tests": HELPERS + '''
def test_column():
    "materials has min_stock INTEGER"
    check(("min_stock", "INTEGER") in [(n, t.split()[0] if t else t) for n, t in columns("materials")],
          "Add a column called min_stock of type INTEGER to materials.")

def test_values():
    "cement is 50, everything else 0"
    rows = query("SELECT name, min_stock FROM materials ORDER BY id")
    for name, v in rows:
        want = 50 if name == "cement" else 0
        check(v == want, "%s has min_stock %r, expected %r." % (name, v, want))
''',
        "solution": "ALTER TABLE materials ADD COLUMN min_stock INTEGER DEFAULT 0;\n\nUPDATE materials SET min_stock = 50 WHERE name = 'cement';\n\nSELECT name, min_stock FROM materials;\n",
        "hints": [
            "`ALTER TABLE materials ADD COLUMN min_stock INTEGER DEFAULT 0;`",
            "Then an UPDATE with `WHERE name = 'cement'`.",
        ],
    },
    {
        "id": "design-task",
        "title": "Chapter task: a tool loan register",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Design a table from a description, the way you would at work.

## Your task

The store wants to track which tools are lent to which staff. Create a table `tool_loans` where:

- each loan has an automatic `id`,
- `tool` (text) must be given,
- `staff_id` (integer) must be given and must be a real staff member's id,
- `loaned_on` (text date) must be given,
- `returned_on` (text date) is empty until the tool comes back,
- a loan can't be returned **before** it was lent: `returned_on` must be `NULL` or on or after `loaned_on`.

Then record two loans: a `laser level` lent to staff `2` on `2026-10-10` and returned on `2026-10-12`, and a `drill` lent to staff `4` on `2026-10-15`, not yet returned.
""",
        "starter": "",
        "tests": HELPERS + '''
def test_rows():
    "Both loans are recorded"
    check(table_exists("tool_loans"), "Create a table called tool_loans.")
    rows = query("SELECT tool, staff_id, loaned_on, returned_on FROM tool_loans ORDER BY loaned_on")
    want = [("laser level", 2, "2026-10-10", "2026-10-12"), ("drill", 4, "2026-10-15", None)]
    check(rows == want, "tool_loans holds %r\\nexpected %r" % (rows, want))

def test_required():
    "tool, staff_id and loaned_on are required"
    check(rejected("INSERT INTO tool_loans (staff_id, loaned_on) VALUES (2, '2026-10-20')"), "tool must be NOT NULL.")
    check(rejected("INSERT INTO tool_loans (tool, loaned_on) VALUES ('saw', '2026-10-20')"), "staff_id must be NOT NULL.")
    check(rejected("INSERT INTO tool_loans (tool, staff_id) VALUES ('saw', 2)"), "loaned_on must be NOT NULL.")

def test_staff_exists():
    "staff_id must point at real staff"
    check(rejected("INSERT INTO tool_loans (tool, staff_id, loaned_on) VALUES ('saw', 99, '2026-10-20')"),
          "A loan to staff 99 (who doesn't exist) was allowed. Add REFERENCES staff(id).")

def test_dates():
    "Can't be returned before it was lent"
    check(rejected("INSERT INTO tool_loans (tool, staff_id, loaned_on, returned_on) VALUES ('saw', 2, '2026-10-20', '2026-10-19')"),
          "A return date before the loan date was allowed. Add a CHECK comparing the two.")
    check(not rejected("INSERT INTO tool_loans (tool, staff_id, loaned_on, returned_on) VALUES ('saw', 2, '2026-10-20', '2026-10-20')"),
          "Returning a tool on the same day it was lent should be allowed.")
''',
        "solution": "CREATE TABLE tool_loans (\n    id INTEGER PRIMARY KEY,\n    tool TEXT NOT NULL,\n    staff_id INTEGER NOT NULL REFERENCES staff(id),\n    loaned_on TEXT NOT NULL,\n    returned_on TEXT,\n    CHECK (returned_on IS NULL OR returned_on >= loaned_on)\n);\n\nINSERT INTO tool_loans (tool, staff_id, loaned_on, returned_on)\nVALUES ('laser level', 2, '2026-10-10', '2026-10-12'),\n       ('drill', 4, '2026-10-15', NULL);\n",
        "hints": [
            "A CHECK that compares two columns goes on its own line at the end, after the last column: `CHECK (returned_on IS NULL OR returned_on >= loaned_on)`.",
            "`staff_id INTEGER NOT NULL REFERENCES staff(id)`",
        ],
    },
]
