import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Indexes and speed",
    "summary": "What an index is, reading EXPLAIN QUERY PLAN, creating indexes, and when they help or hurt.",
}

HELPERS = '''
def index_columns(table):
    """{index name: [columns]} for a table, including automatic ones."""
    out = {}
    for row in query("PRAGMA index_list(%s)" % table):
        name = row[1]
        out[name] = [r[2] for r in query("PRAGMA index_info('%s')" % name)]
    return out

def last_plan():
    if not COLUMNS or "detail" not in [c.lower() for c in COLUMNS]:
        return None
    i = [c.lower() for c in COLUMNS].index("detail")
    return " | ".join(str(r[i]) for r in ROWS)
'''

LESSONS = [
    {
        "id": "index-what",
        "title": "What an index is",
        "kind": "read",
        "body": """
Ask for `WHERE material_id = 4` and, with no help, the database reads **every row** of `deliveries` and checks each one. With 24 rows that's instant. With 20 million it isn't.

An **index** is like the index at the back of a book. Instead of reading every page to find "rebar", you look it up in a sorted list that tells you which pages to turn to. A database index is a sorted copy of one or more columns, with a pointer from each value back to its rows.

```sql
CREATE INDEX idx_deliveries_material ON deliveries(material_id);
```

After that, `WHERE material_id = 4` jumps straight to the matching rows.

## The trade-off

Indexes aren't free:

- Every `INSERT`, `UPDATE` and `DELETE` must update every index on that table too, so writes get slower.
- Each index takes disk space.

So you add indexes for the questions you actually ask often, on big tables, not on every column "just in case".

## You already have some

SQLite automatically indexes every `PRIMARY KEY` and every `UNIQUE` column, because it needs to check those quickly on every insert. That's why looking a row up by its `id` is always fast.
""",
    },
    {
        "id": "explain",
        "title": "EXPLAIN QUERY PLAN",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
You don't have to guess whether a query uses an index. Put `EXPLAIN QUERY PLAN` in front of it and SQLite describes its plan instead of running it:

```sql
EXPLAIN QUERY PLAN
SELECT * FROM materials WHERE id = 4;
-- detail: SEARCH materials USING INTEGER PRIMARY KEY (rowid=?)
```

Look at the `detail` column:

- **SCAN** table means "read every row". Fine for small tables, slow for big ones.
- **SEARCH** table **USING INDEX** means "jump straight to the right rows".

## Your task

Ask for the plan of this query, and see which kind it is:

```sql
SELECT name FROM suppliers WHERE city = 'Riyadh';
```
""",
        "starter": "-- put EXPLAIN QUERY PLAN in front of the query\nSELECT name FROM suppliers WHERE city = 'Riyadh';\n",
        "tests": HELPERS + '''
def test_plan():
    "Shows the plan for the suppliers query"
    plan = last_plan()
    check(plan is not None, "Put EXPLAIN QUERY PLAN in front of the SELECT, so the result shows a detail column.")
    check("SCAN" in plan.upper() and "SUPPLIERS" in plan.upper(), "The plan should be a SCAN of suppliers. It was: %s" % plan)
''',
        "solution": "EXPLAIN QUERY PLAN\nSELECT name FROM suppliers WHERE city = 'Riyadh';\n",
        "hints": [
            "Add the line `EXPLAIN QUERY PLAN` directly above the SELECT (no semicolon between them).",
        ],
    },
    {
        "id": "create-index",
        "title": "CREATE INDEX",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
```sql
CREATE INDEX idx_suppliers_city ON suppliers(city);
```

- The name is up to you. A common pattern is `idx_table_column`.
- `ON table(column)` says what to index.
- `DROP INDEX idx_suppliers_city;` removes it. The data isn't touched.

Run `EXPLAIN QUERY PLAN` after creating an index and you'll see the plan change from SCAN to SEARCH.

## Your task

1. Create an index called `idx_deliveries_material` on `deliveries(material_id)`.
2. Then show the plan for `SELECT * FROM deliveries WHERE material_id = 4;` to confirm it's used.
""",
        "starter": "-- 1. CREATE INDEX ...\n\n-- 2. EXPLAIN QUERY PLAN ...\n",
        "tests": HELPERS + '''
def test_index():
    "The index exists on material_id"
    idx = index_columns("deliveries")
    check("idx_deliveries_material" in idx, "I can't find an index called idx_deliveries_material on deliveries.")
    check(idx["idx_deliveries_material"] == ["material_id"], "The index should be on material_id, but it's on %r." % idx["idx_deliveries_material"])

def test_plan():
    "The plan uses it"
    plan = last_plan()
    check(plan is not None, "Finish with EXPLAIN QUERY PLAN for the query, so the plan is shown.")
    check("USING INDEX" in plan.upper() or "USING COVERING INDEX" in plan.upper(), "The plan doesn't use an index: %s" % plan)
''',
        "solution": "CREATE INDEX idx_deliveries_material ON deliveries(material_id);\n\nEXPLAIN QUERY PLAN\nSELECT * FROM deliveries WHERE material_id = 4;\n",
        "hints": [
            "`CREATE INDEX idx_deliveries_material ON deliveries(material_id);`",
            "Then `EXPLAIN QUERY PLAN` followed by the SELECT.",
        ],
    },
    {
        "id": "scan-quiz",
        "title": "Reading a plan",
        "kind": "quiz",
        "body": "One line of a query plan tells you a lot.",
        "question": "A slow report's plan says `SCAN deliveries`, and `deliveries` has 20 million rows. The query filters on `site`. What's the most likely fix?",
        "options": [
            "Add `LIMIT 100`",
            "Create an index on `deliveries(site)`",
            "Index every column of deliveries",
            "Rename the table",
        ],
        "answer": 1,
        "explain": "SCAN means every one of the 20 million rows is read to find the matching sites. An index on the column being filtered lets SQLite SEARCH instead. Indexing every column would slow down every write for little gain.",
    },
    {
        "id": "index-two",
        "title": "Indexes on two columns",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
An index can cover several columns, sorted by the first, then the second, like a phone book sorted by surname then first name:

```sql
CREATE INDEX idx_staff_site_role ON staff(site, role);
```

It helps queries that filter on the **first** column, or on the first and second together. It doesn't help a query that only filters on the second column, just as a phone book doesn't help you find everyone called "Sara".

So the order matters: put the column you always filter on first.

## Your task

Reports often ask for one site's deliveries over a date range:

```sql
SELECT * FROM deliveries
WHERE site = 'RYD-N' AND delivery_date BETWEEN '2026-10-01' AND '2026-10-10';
```

Create an index called `idx_deliveries_site_date` on `site` then `delivery_date`, and finish with the plan for the query above.
""",
        "starter": "",
        "tests": HELPERS + '''
def test_index():
    "Index on (site, delivery_date), in that order"
    idx = index_columns("deliveries")
    check("idx_deliveries_site_date" in idx, "I can't find an index called idx_deliveries_site_date.")
    check(idx["idx_deliveries_site_date"] == ["site", "delivery_date"],
          "The index columns are %r. They should be site first, then delivery_date." % idx["idx_deliveries_site_date"])

def test_plan():
    "The plan uses it"
    plan = last_plan()
    check(plan is not None and "IDX_DELIVERIES_SITE_DATE" in plan.upper(), "Finish with EXPLAIN QUERY PLAN for the query. Plan was: %s" % plan)
''',
        "solution": "CREATE INDEX idx_deliveries_site_date ON deliveries(site, delivery_date);\n\nEXPLAIN QUERY PLAN\nSELECT * FROM deliveries\nWHERE site = 'RYD-N' AND delivery_date BETWEEN '2026-10-01' AND '2026-10-10';\n",
        "hints": [
            "`CREATE INDEX idx_deliveries_site_date ON deliveries(site, delivery_date);`",
        ],
    },
    {
        "id": "index-when-quiz",
        "title": "When not to index",
        "kind": "quiz",
        "body": "Indexes speed up reads and slow down writes. Weigh it up.",
        "question": "Which of these is the **weakest** case for a new index?",
        "options": [
            "A big table, searched by customer id hundreds of times a minute",
            "A small lookup table of 12 rows",
            "A column used to join two large tables",
            "A big table that's filtered by date in every report",
        ],
        "answer": 1,
        "explain": "Twelve rows are read in no time with a plain scan, so an index adds upkeep for no real gain. The others all involve big tables and frequent lookups, which is exactly where indexes pay off.",
    },
]
