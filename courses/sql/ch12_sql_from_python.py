import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "SQL from Python",
    "summary": "The sqlite3 module: connecting, fetching rows, parameters (and SQL injection), saving changes, and a small tracker app.",
}

FILES = {"site.sql": SITE}

# Each check builds its own fresh copy of the practice database
HELPERS = '''
import sqlite3

def site_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    with open("site.sql", encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn
'''

STARTER_HEAD = 'import sqlite3\n\nconn = sqlite3.connect(":memory:")\nwith open("site.sql", encoding="utf-8") as f:\n    conn.executescript(f.read())   # builds the practice database\n\n\n'

LESSONS = [
    {
        "id": "py-connect",
        "title": "Connecting and querying",
        "kind": "code",
        "files": FILES,
        "body": """
Back to Python. The `sqlite3` module that comes with Python lets a program run SQL:

```python
import sqlite3

conn = sqlite3.connect("site.db")     # opens the file, creating it if needed
cur = conn.execute("SELECT COUNT(*) FROM staff")
row = cur.fetchone()                  # one row, as a tuple: (10,)
print(row[0])                         # 10
```

- `sqlite3.connect(path)` opens a database file. `":memory:"` makes a temporary one in memory instead, which is what these exercises use.
- `conn.execute(sql)` runs one statement and gives back a **cursor**, which holds the results.
- `cur.fetchone()` gets the next row as a **tuple**, even when there's only one column. That's why you need `row[0]` to get the number out.

The starter code builds the practice database for you, from the same tables you've been using.

> **Common slip:** returning `row` instead of `row[0]`. The check will say you returned `(6,)`, a tuple, instead of `6`.

## Your task

Write `count_suppliers(conn)` that returns the number of suppliers as an `int`.
""",
        "starter": STARTER_HEAD + "def count_suppliers(conn):\n    # run SELECT COUNT(*) FROM suppliers, fetch one row, return its first value\n    pass\n\n\nprint(count_suppliers(conn))   # should print 6\n",
        "tests": HELPERS + '''
def test_count():
    "Returns the number of suppliers"
    c = site_db()
    v, _ = capture(need("count_suppliers"), c)
    check(v == 6 and isinstance(v, int), "count_suppliers returned %r, expected 6 (an int, not a tuple)." % (v,))
    c.execute("INSERT INTO suppliers (name) VALUES ('New One')")
    v, _ = capture(need("count_suppliers"), c)
    check(v == 7, "After adding a supplier, count_suppliers returned %r, expected 7. Query the database each time." % (v,))
''',
        "solution": STARTER_HEAD + "def count_suppliers(conn):\n    row = conn.execute(\"SELECT COUNT(*) FROM suppliers\").fetchone()\n    return row[0]\n\n\nprint(count_suppliers(conn))\n",
        "hints": [
            "`row = conn.execute(\"SELECT COUNT(*) FROM suppliers\").fetchone()`",
            "Then `return row[0]`.",
        ],
    },
    {
        "id": "py-fetchall",
        "title": "Looping over rows",
        "kind": "code",
        "files": FILES,
        "body": """
`fetchall()` gets every row at once, as a **list of tuples**. Loop over it like any list:

```python
rows = conn.execute("SELECT name, years FROM staff ORDER BY name").fetchall()
for name, years in rows:
    print(name, years)
```

The `for name, years in rows` line unpacks each tuple into two variables, the same way you unpacked tuples in the Python course.

Do the sorting and filtering in SQL where you can. The database is good at it, and the Python stays short.

## Your task

Write `material_names(conn)` that returns a plain **list of names** (strings, not tuples) of every material, in alphabetical order.
""",
        "starter": STARTER_HEAD + "def material_names(conn):\n    rows = conn.execute(\"SELECT name FROM materials ORDER BY name\").fetchall()\n    # rows is a list of 1-item tuples, like [('bricks',), ('cement',), ...]\n    # build and return a list of just the names\n    pass\n\n\nprint(material_names(conn))\n",
        "tests": HELPERS + '''
def test_names():
    "A list of names, alphabetical"
    v, _ = capture(need("material_names"), site_db())
    want = sorted(["cement", "sand", "gravel", "rebar", "bricks", "timber", "tiles", "paint", "glass"])
    if isinstance(v, list) and v and isinstance(v[0], tuple):
        check(False, "You returned a list of tuples like %r. Take the first item of each: row[0]." % (v[:2],))
    check(v == want, "material_names returned %r\\nexpected %r" % (v, want))
''',
        "solution": STARTER_HEAD + "def material_names(conn):\n    rows = conn.execute(\"SELECT name FROM materials ORDER BY name\").fetchall()\n    names = []\n    for row in rows:\n        names.append(row[0])\n    return names\n\n\nprint(material_names(conn))\n",
        "hints": [
            "Start `names = []`, loop `for row in rows:`, and `names.append(row[0])`.",
            "Or in one line: `return [row[0] for row in rows]`.",
        ],
    },
    {
        "id": "py-params",
        "title": "Parameters",
        "kind": "code",
        "files": FILES,
        "body": """
Queries usually depend on a value from your program, like which site to look at. **Don't** paste the value into the SQL text yourself. Put a `?` where each value goes, and pass the values separately, in a tuple:

```python
site = "RYD-N"
rows = conn.execute(
    "SELECT id, quantity FROM deliveries WHERE site = ? AND quantity > ?",
    (site, 10),
).fetchall()
```

The `?` placeholders are filled in by `sqlite3` itself, safely and with the right quoting. You never write quotes around a `?`.

> **Common slip:** one value still needs a tuple, and a one-item tuple needs a trailing comma: `(site,)`. Writing `(site)` is just `site` in brackets, and you'll get an error about the number of bindings.

## Your task

Write `deliveries_for_site(conn, site)` that returns a list of `(id, quantity)` tuples for that site, sorted by id. Use a `?` parameter.
""",
        "starter": STARTER_HEAD + "def deliveries_for_site(conn, site):\n    pass\n\n\nprint(deliveries_for_site(conn, \"JED-1\"))\n",
        "tests": HELPERS + '''
def test_rows():
    "Right deliveries for any site"
    f = need("deliveries_for_site")
    c = site_db()
    for s in ("RYD-N", "JED-1", "NOWHERE"):
        v, _ = capture(f, c, s)
        want = c.execute("SELECT id, quantity FROM deliveries WHERE site = ? ORDER BY id", (s,)).fetchall()
        check(v == want, "deliveries_for_site(conn, %r) returned %r\\nexpected %r" % (s, v, want))

def test_placeholder():
    "Uses a ? placeholder, not string formatting"
    check("?" in CODE, "Put a ? in the SQL where the site goes.")
    check("f\\"SELECT" not in CODE and "f'SELECT" not in CODE and "+ site" not in CODE and "% site" not in CODE,
          "Don't build the SQL with an f-string or +. Pass the site as a parameter.")
''',
        "solution": STARTER_HEAD + "def deliveries_for_site(conn, site):\n    return conn.execute(\n        \"SELECT id, quantity FROM deliveries WHERE site = ? ORDER BY id\",\n        (site,),\n    ).fetchall()\n\n\nprint(deliveries_for_site(conn, \"JED-1\"))\n",
        "hints": [
            "The SQL is `\"SELECT id, quantity FROM deliveries WHERE site = ? ORDER BY id\"`.",
            "Pass `(site,)` as the second argument to `execute`, then `.fetchall()`.",
        ],
    },
    {
        "id": "injection-quiz",
        "title": "SQL injection",
        "kind": "quiz",
        "body": """
Why all the fuss about `?`? Look what happens when a value is pasted straight into the SQL:

```python
name = input("Supplier name: ")
conn.execute(f"DELETE FROM suppliers WHERE name = '{name}'")
```

Type `Najd Timber` and it deletes one supplier. But the person typing controls part of your SQL.
""",
        "question": "What gets deleted if someone types:  `x' OR '1'='1`",
        "options": [
            "Nothing, because no supplier is called that",
            "One supplier called x",
            "Every supplier",
            "Python raises an error before running it",
        ],
        "answer": 2,
        "explain": "The SQL becomes `DELETE FROM suppliers WHERE name = 'x' OR '1'='1'`, and `'1'='1'` is true for every row. This is **SQL injection**, one of the most common security holes on the web. With `WHERE name = ?` and the value passed separately, the whole input is treated as one piece of text and can never change the SQL.",
    },
    {
        "id": "py-insert",
        "title": "Saving changes",
        "kind": "code",
        "files": FILES,
        "body": """
Changes made through `sqlite3` are held in a transaction until you call `conn.commit()`. Forget it, and your inserts vanish when the program ends.

```python
cur = conn.execute(
    "INSERT INTO sites (code, name, city) VALUES (?, ?, ?)",
    ("DMM-1", "Gulf Yard", "Dammam"),
)
conn.commit()
print(cur.lastrowid)   # the id SQLite gave the new row
```

`cur.lastrowid` is handy when the database picks the id and you need to know what it chose.

## Your task

Write `add_supplier(conn, name, city, rating)` that inserts a supplier using `?` parameters, commits, and **returns the new supplier's id**.
""",
        "starter": STARTER_HEAD + "def add_supplier(conn, name, city, rating):\n    # 1. INSERT with three ? placeholders\n    # 2. conn.commit()\n    # 3. return the new id (cur.lastrowid)\n    pass\n\n\nprint(add_supplier(conn, \"Eastern Fixings\", \"Dammam\", 4))   # should print 7\n",
        "tests": HELPERS + '''
def test_insert():
    "Inserts the supplier and returns its id"
    c = site_db()
    v, _ = capture(need("add_supplier"), c, "Eastern Fixings", "Dammam", 4)
    row = c.execute("SELECT id, city, rating FROM suppliers WHERE name = 'Eastern Fixings'").fetchall()
    check(len(row) == 1, "I couldn't find the new supplier in the table.")
    check(row[0][1:] == ("Dammam", 4), "The new supplier has city and rating %r." % (row[0][1:],))
    check(v == row[0][0], "add_supplier returned %r, but the new row's id is %r. Return cur.lastrowid." % (v, row[0][0]))

def test_commit():
    "Commits the change"
    c = site_db()
    c.commit()
    capture(need("add_supplier"), c, "Test Co", "Abha", 3)
    check(not c.in_transaction, "The change is still waiting to be committed. Call conn.commit().")

def test_params():
    "Uses ? parameters"
    check(CODE.count("?") >= 3, "Use three ? placeholders, one per value.")
''',
        "solution": STARTER_HEAD + "def add_supplier(conn, name, city, rating):\n    cur = conn.execute(\n        \"INSERT INTO suppliers (name, city, rating) VALUES (?, ?, ?)\",\n        (name, city, rating),\n    )\n    conn.commit()\n    return cur.lastrowid\n\n\nprint(add_supplier(conn, \"Eastern Fixings\", \"Dammam\", 4))\n",
        "hints": [
            "`cur = conn.execute(\"INSERT INTO suppliers (name, city, rating) VALUES (?, ?, ?)\", (name, city, rating))`",
            "Then `conn.commit()` and `return cur.lastrowid`.",
        ],
    },
    {
        "id": "py-dicts",
        "title": "Rows as dictionaries",
        "kind": "code",
        "files": FILES,
        "body": """
`row[0]`, `row[3]`: fine for one or two columns, unreadable for ten. Set the connection's `row_factory` to `sqlite3.Row` and you can get columns by name:

```python
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT name, city FROM suppliers WHERE id = 1").fetchone()
print(row["name"], row["city"])
print(dict(row))    # {'name': 'Al Noor Building Supplies', 'city': 'Riyadh'}
```

`dict(row)` turns a row into an ordinary dictionary, which is handy for passing data around the rest of your program, or turning it into JSON later in the back-end track.

## Your task

Write `supplier_dicts(conn)` that returns every supplier as a dictionary with the keys `name`, `city` and `rating`, sorted by name.
""",
        "starter": STARTER_HEAD + "def supplier_dicts(conn):\n    conn.row_factory = sqlite3.Row\n    pass\n\n\nfor s in supplier_dicts(conn):\n    print(s)\n",
        "tests": HELPERS + '''
def test_dicts():
    "A list of dictionaries, sorted by name"
    c = site_db()
    v, _ = capture(need("supplier_dicts"), c)
    c2 = site_db()
    want = [{"name": n, "city": ci, "rating": r} for n, ci, r in
            c2.execute("SELECT name, city, rating FROM suppliers ORDER BY name").fetchall()]
    check(isinstance(v, list) and all(isinstance(x, dict) for x in v),
          "Return a list of real dicts. dict(row) converts each sqlite3.Row.")
    check(v == want, "supplier_dicts returned %r\\nexpected %r" % (v[:2], want[:2]))
''',
        "solution": STARTER_HEAD + "def supplier_dicts(conn):\n    conn.row_factory = sqlite3.Row\n    rows = conn.execute(\"SELECT name, city, rating FROM suppliers ORDER BY name\").fetchall()\n    return [dict(row) for row in rows]\n\n\nfor s in supplier_dicts(conn):\n    print(s)\n",
        "hints": [
            "Select exactly the three columns, `ORDER BY name`, and `fetchall()`.",
            "`return [dict(row) for row in rows]`",
        ],
    },
    {
        "id": "py-tracker",
        "title": "Mini project: a task tracker",
        "kind": "code",
        "body": """
A small app backed by a real database. It uses everything in this chapter.

## Your task

Write four functions for a to-do tracker. Each takes the connection as its first argument.

| Function | Does |
|---|---|
| `setup(conn)` | creates a table `tasks` if it doesn't exist: `id INTEGER PRIMARY KEY`, `title TEXT NOT NULL`, `done INTEGER NOT NULL DEFAULT 0` |
| `add_task(conn, title)` | inserts a task and returns its new id |
| `complete(conn, task_id)` | marks that task as done (`done = 1`) |
| `open_tasks(conn)` | returns a list of the **titles** of tasks not yet done, in id order |

Commit after every change. Use `?` for every value.

`CREATE TABLE IF NOT EXISTS tasks (...)` only creates the table the first time, so `setup` is safe to call every time the app starts.
""",
        "starter": "import sqlite3\n\n\ndef setup(conn):\n    pass\n\n\ndef add_task(conn, title):\n    pass\n\n\ndef complete(conn, task_id):\n    pass\n\n\ndef open_tasks(conn):\n    pass\n\n\nconn = sqlite3.connect(\":memory:\")\nsetup(conn)\na = add_task(conn, \"Order rebar\")\nb = add_task(conn, \"Book crane\")\ncomplete(conn, a)\nprint(open_tasks(conn))   # should print ['Book crane']\n",
        "tests": '''
import sqlite3

def fresh():
    c = sqlite3.connect(":memory:")
    need("setup")(c)
    return c

def test_setup():
    "setup creates the tasks table, and can run twice"
    c = fresh()
    cols = [(r[1], r[2].upper(), r[3]) for r in c.execute("PRAGMA table_info(tasks)")]
    check([x[0] for x in cols] == ["id", "title", "done"], "tasks should have columns id, title, done. It has %r." % [x[0] for x in cols])
    need("setup")(c)

def test_add():
    "add_task returns increasing ids"
    c = fresh()
    a, _ = capture(need("add_task"), c, "one")
    b, _ = capture(need("add_task"), c, "two")
    check(isinstance(a, int) and b == a + 1, "add_task returned %r then %r. Return cur.lastrowid." % (a, b))
    check(not c.in_transaction, "Commit after inserting.")

def test_flow():
    "complete and open_tasks work together"
    c = fresh()
    ids = [need("add_task")(c, t) for t in ("Order rebar", "Book crane", "Pour slab")]
    v, _ = capture(need("open_tasks"), c)
    check(v == ["Order rebar", "Book crane", "Pour slab"], "open_tasks returned %r." % (v,))
    need("complete")(c, ids[0])
    check(not c.in_transaction, "Commit after completing a task.")
    v, _ = capture(need("open_tasks"), c)
    check(v == ["Book crane", "Pour slab"], "After completing the first task, open_tasks returned %r." % (v,))

def test_params():
    "Uses ? parameters"
    check(CODE.count("?") >= 2, "Use ? placeholders for the title and the task id.")
''',
        "solution": "import sqlite3\n\n\ndef setup(conn):\n    conn.execute(\n        \"\"\"CREATE TABLE IF NOT EXISTS tasks (\n            id INTEGER PRIMARY KEY,\n            title TEXT NOT NULL,\n            done INTEGER NOT NULL DEFAULT 0\n        )\"\"\"\n    )\n    conn.commit()\n\n\ndef add_task(conn, title):\n    cur = conn.execute(\"INSERT INTO tasks (title) VALUES (?)\", (title,))\n    conn.commit()\n    return cur.lastrowid\n\n\ndef complete(conn, task_id):\n    conn.execute(\"UPDATE tasks SET done = 1 WHERE id = ?\", (task_id,))\n    conn.commit()\n\n\ndef open_tasks(conn):\n    rows = conn.execute(\"SELECT title FROM tasks WHERE done = 0 ORDER BY id\").fetchall()\n    return [row[0] for row in rows]\n\n\nconn = sqlite3.connect(\":memory:\")\nsetup(conn)\na = add_task(conn, \"Order rebar\")\nb = add_task(conn, \"Book crane\")\ncomplete(conn, a)\nprint(open_tasks(conn))\n",
        "hints": [
            "`setup`: `conn.execute(\"CREATE TABLE IF NOT EXISTS tasks (...)\")`. A triple-quoted string lets the SQL span several lines.",
            "`add_task` is like `add_supplier` with one value: `(title,)`. `complete` is an UPDATE with `WHERE id = ?`.",
            "`open_tasks`: `SELECT title FROM tasks WHERE done = 0 ORDER BY id`, then `[row[0] for row in rows]`.",
        ],
    },
    {
        "id": "sql-next",
        "title": "What comes next",
        "kind": "read",
        "body": """
That's the SQL track. You can now design tables, fill them, ask them almost any question, make queries fast, and drive all of it from Python.

## Using it for real

SQLite is a perfectly good choice for real work: a register of documents, test results, a log of site deliveries. One file, no server, and Python can read it anywhere.

Two tools worth having:

- **DB Browser for SQLite** (free) lets you open a `.db` file and look around, much like a spreadsheet.
- Python's `sqlite3` module, which you now know, for everything automated.

## Other databases

PostgreSQL, MySQL and SQL Server all speak SQL. Almost everything here carries straight over. The differences are mostly extras (stricter types, more functions) and how you connect. The back-end track moves from SQLite to PostgreSQL in its database chapter.

## Next track

**Python for engineering** picks up NumPy, pandas and matplotlib. pandas in particular will feel familiar: filtering, grouping and joining tables, in Python.
""",
    },
]
