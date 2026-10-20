import importlib.util as _u
import os as _o

_here = _o.path.dirname(_o.path.abspath(__file__))
_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_here, "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

with open(_o.path.join(_here, "..", "sql", "site.sql"), encoding="utf-8") as _f:
    SITE_SQL = _f.read()

CHAPTER = {
    "title": "Servers and databases",
    "summary": "An API backed by SQLite, migrations, moving to PostgreSQL, and the N+1 query problem.",
}

T = 20

DB_PRELUDE = S.FASTAPI_TOOLS + r'''
import sqlite3 as _sqlite3

def _site_db():
    c = _sqlite3.connect(":memory:", check_same_thread=False)
    c.row_factory = _sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    with open("site.sql", encoding="utf-8") as f:
        c.executescript(f.read())
    return c

conn = _site_db()   # the practice database from the SQL track
'''

FILES = {"site.sql": SITE_SQL}

LESSONS = [
    {
        "id": "api-db",
        "title": "Putting a database behind the API",
        "kind": "read",
        "body": """
The APIs so far kept their data in a Python dict, which vanishes when the server stops. Real APIs keep it in a database, and each route becomes a small piece of SQL:

```python
@app.get("/sites/{code}")
def get_site(code: str):
    row = conn.execute("SELECT code, name, city FROM sites WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="site not found")
    return dict(row)
```

Everything from the SQL track's last chapter applies: **always** `?` parameters, `conn.commit()` after changes, `row_factory = sqlite3.Row` so `dict(row)` gives JSON-ready dicts.

## In these exercises

The lessons set up `conn` for you: a connection to the practice database from the SQL track (sites, materials, suppliers, deliveries, staff), with `row_factory` already set. In a real app you'd create it at start-up:

```python
conn = sqlite3.connect("site.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
```

`check_same_thread=False` is needed because FastAPI may run your route functions on different threads. For a busy production API you'd use a connection **pool** or a fresh connection per request instead of sharing one, but one shared connection is fine while learning.
""",
    },
    {
        "id": "db-read",
        "title": "Reading from the database",
        "kind": "code",
        "timeout": T,
        "files": FILES,
        "prelude": DB_PRELUDE,
        "body": """
The query parameter trick from the FastAPI lessons works with SQL too. When the filter is optional, choose between two queries:

```python
@app.get("/suppliers")
def list_suppliers(city: str = None):
    if city is None:
        rows = conn.execute("SELECT id, name, city FROM suppliers ORDER BY id").fetchall()
    else:
        rows = conn.execute("SELECT id, name, city FROM suppliers WHERE city = ? ORDER BY id", (city,)).fetchall()
    return [dict(r) for r in rows]
```

## Your task

Add two routes using `conn`:

- `GET /materials` returns every material as `{"id", "name", "category", "unit_price"}`, sorted by id, optionally filtered by a `category` query parameter
- `GET /materials/{material_id}` returns one material with the same fields, or 404
""",
        "starter": "from fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n\n# conn is ready to use\n\n\ncall(app, \"GET\", \"/materials?category=aggregate\")\ncall(app, \"GET\", \"/materials/99\")\n",
        "tests": '''
from fastapi.testclient import TestClient

def test_list():
    "List, with and without a category"
    c = TestClient(need("app"))
    r = c.get("/materials")
    check(r.status_code == 200 and len(r.json()) == 9, "GET /materials should return all 9 materials. Got %s %s." % (r.status_code, r.text[:200]))
    check(set(r.json()[0]) == {"id", "name", "category", "unit_price"}, "Each material should have exactly id, name, category and unit_price.")
    r = c.get("/materials", params={"category": "aggregate"})
    check([m["name"] for m in r.json()] == ["sand", "gravel"], "?category=aggregate gave %s." % r.text)

def test_one():
    "One material, or 404"
    c = TestClient(need("app"))
    r = c.get("/materials/4")
    check(r.status_code == 200 and r.json() == {"id": 4, "name": "rebar", "category": "steel", "unit_price": 2950.0}, "GET /materials/4 gave %s %s." % (r.status_code, r.text))
    check(c.get("/materials/99").status_code == 404, "GET /materials/99 should be 404.")

def test_params():
    "Uses ? parameters"
    check("?" in CODE, "Pass values with ? placeholders, never by building the SQL text.")
''',
        "solution": "from fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n\nCOLS = \"id, name, category, unit_price\"\n\n\n@app.get(\"/materials\")\ndef list_materials(category: str = None):\n    if category is None:\n        rows = conn.execute(f\"SELECT {COLS} FROM materials ORDER BY id\").fetchall()\n    else:\n        rows = conn.execute(f\"SELECT {COLS} FROM materials WHERE category = ? ORDER BY id\", (category,)).fetchall()\n    return [dict(r) for r in rows]\n\n\n@app.get(\"/materials/{material_id}\")\ndef get_material(material_id: int):\n    row = conn.execute(f\"SELECT {COLS} FROM materials WHERE id = ?\", (material_id,)).fetchone()\n    if row is None:\n        raise HTTPException(status_code=404, detail=\"material not found\")\n    return dict(row)\n\n\ncall(app, \"GET\", \"/materials?category=aggregate\")\ncall(app, \"GET\", \"/materials/99\")\n",
        "hints": [
            "The list route has the same shape as `list_suppliers`.",
            "For one: `row = conn.execute(\"SELECT ... WHERE id = ?\", (material_id,)).fetchone()`, then 404 if `row is None`, else `return dict(row)`.",
        ],
    },
    {
        "id": "db-write",
        "title": "Writing to the database",
        "kind": "code",
        "timeout": T,
        "files": FILES,
        "prelude": DB_PRELUDE,
        "body": """
A POST becomes an `INSERT`, then a commit, then a read-back of the new row so the client gets exactly what was stored:

```python
@app.post("/suppliers", status_code=201)
def create_supplier(s: SupplierIn):
    cur = conn.execute("INSERT INTO suppliers (name, city) VALUES (?, ?)", (s.name, s.city))
    conn.commit()
    return get_supplier(cur.lastrowid)
```

The database's own rules are a second line of defence. The `deliveries` table has foreign keys, so a delivery for a site that doesn't exist raises `sqlite3.IntegrityError`. Catch it and turn it into a clear 400 or 422, rather than letting the client see a 500:

```python
try:
    cur = conn.execute(...)
except sqlite3.IntegrityError:
    raise HTTPException(status_code=422, detail="unknown site, material or supplier")
```

## Your task

Add `POST /deliveries` taking `delivery_date` (text), `site` (text), `material_id`, `supplier_id` (ints) and `quantity` (a number above 0). Insert it, commit, and reply **201** with the new row (all six columns, including the new `id`). If the database rejects it, reply **422** with detail `unknown site, material or supplier`.
""",
        "starter": "import sqlite3\n\nfrom fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\n\n\nclass DeliveryIn(BaseModel):\n    delivery_date: str\n    site: str\n    material_id: int\n    supplier_id: int\n    quantity: float = Field(gt=0)\n\n\n# your route here\n\n\ncall(app, \"POST\", \"/deliveries\", json={\"delivery_date\": \"2026-10-20\", \"site\": \"RYD-N\", \"material_id\": 1, \"supplier_id\": 1, \"quantity\": 30})\ncall(app, \"POST\", \"/deliveries\", json={\"delivery_date\": \"2026-10-20\", \"site\": \"XYZ\", \"material_id\": 1, \"supplier_id\": 1, \"quantity\": 30})\n",
        "tests": '''
from fastapi.testclient import TestClient

BODY = {"delivery_date": "2026-10-21", "site": "JED-1", "material_id": 2, "supplier_id": 4, "quantity": 12.5}

def test_create():
    "Inserted, committed and returned"
    c = TestClient(need("app"))
    db = need("conn")
    before = db.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]
    r = c.post("/deliveries", json=BODY)
    check(r.status_code == 201, "A valid delivery gave %s %s." % (r.status_code, r.text))
    body = r.json()
    check(isinstance(body.get("id"), int) and {k: body.get(k) for k in BODY} == BODY, "The response was %s." % r.text)
    check(db.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0] == before + 1, "The delivery should be in the table.")
    check(not db.in_transaction, "Commit after inserting.")

def test_rejected():
    "422 when the database refuses"
    c = TestClient(need("app"))
    for bad in (dict(BODY, site="XYZ"), dict(BODY, material_id=99)):
        r = c.post("/deliveries", json=bad)
        check(r.status_code == 422 and r.json().get("detail") == "unknown site, material or supplier",
              "%r gave %s %s." % (bad, r.status_code, r.text))
''',
        "solution": "import sqlite3\n\nfrom fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\n\n\nclass DeliveryIn(BaseModel):\n    delivery_date: str\n    site: str\n    material_id: int\n    supplier_id: int\n    quantity: float = Field(gt=0)\n\n\n@app.post(\"/deliveries\", status_code=201)\ndef create_delivery(d: DeliveryIn):\n    try:\n        cur = conn.execute(\n            \"INSERT INTO deliveries (delivery_date, site, material_id, supplier_id, quantity) VALUES (?, ?, ?, ?, ?)\",\n            (d.delivery_date, d.site, d.material_id, d.supplier_id, d.quantity),\n        )\n        conn.commit()\n    except sqlite3.IntegrityError:\n        conn.rollback()\n        raise HTTPException(status_code=422, detail=\"unknown site, material or supplier\")\n    row = conn.execute(\"SELECT * FROM deliveries WHERE id = ?\", (cur.lastrowid,)).fetchone()\n    return dict(row)\n\n\ncall(app, \"POST\", \"/deliveries\", json={\"delivery_date\": \"2026-10-20\", \"site\": \"RYD-N\", \"material_id\": 1, \"supplier_id\": 1, \"quantity\": 30})\ncall(app, \"POST\", \"/deliveries\", json={\"delivery_date\": \"2026-10-20\", \"site\": \"XYZ\", \"material_id\": 1, \"supplier_id\": 1, \"quantity\": 30})\n",
        "hints": [
            "The INSERT names five columns with five `?`s. Put it and `conn.commit()` inside a `try:`.",
            "After the try: `row = conn.execute(\"SELECT * FROM deliveries WHERE id = ?\", (cur.lastrowid,)).fetchone()` and `return dict(row)`.",
        ],
    },
    {
        "id": "migrations",
        "title": "Migrations",
        "kind": "read",
        "body": """
Your app's tables will change: a new column here, a new table there. On your laptop you can delete the database and start again. On a live server, the data must survive every change.

A **migration** is one numbered, written-down change to the database structure:

```python
MIGRATIONS = [
    "CREATE TABLE sites (code TEXT PRIMARY KEY, name TEXT NOT NULL)",       # 1
    "ALTER TABLE sites ADD COLUMN city TEXT",                               # 2
    "CREATE INDEX idx_deliveries_site ON deliveries(site)",                 # 3
]
```

The database remembers which number it's at. On start-up, the app runs any migrations after that number, in order, then records the new number. So every copy of the database (yours, a colleague's, the server's) ends up with the same structure by the same steps.

## The golden rule

Never edit a migration that has already run somewhere. Add a new one instead. Otherwise databases that ran the old version and ones that run the new version quietly end up different.

## Tools

Bigger projects use a library for this: **Alembic** (with SQLAlchemy) or **Django**'s built-in migrations. They do exactly what you'll write by hand next, plus generating migrations from your models.
""",
    },
    {
        "id": "migrate",
        "title": "A migration runner",
        "kind": "code",
        "timeout": T,
        "body": """
SQLite has a spare number in every database file that you can use to track the version: `PRAGMA user_version`.

```python
version = conn.execute("PRAGMA user_version").fetchone()[0]   # 0 for a new database
conn.execute("PRAGMA user_version = 3")                        # record a new value
```

(`PRAGMA` can't take a `?` parameter, so build that one statement with an f-string from an int you control.)

## Your task

Write `migrate(conn, migrations)`. `migrations` is a list of SQL statements, migration 1 first. Run every migration the database hasn't had yet, in order, update `user_version` after each one, commit, and return **how many** were applied.

Running it twice in a row must apply nothing the second time.
""",
        "starter": "import sqlite3\n\nMIGRATIONS = [\n    \"CREATE TABLE sites (code TEXT PRIMARY KEY, name TEXT NOT NULL)\",\n    \"ALTER TABLE sites ADD COLUMN city TEXT\",\n    \"CREATE TABLE inspections (id INTEGER PRIMARY KEY, site TEXT REFERENCES sites(code), passed INTEGER)\",\n]\n\n\ndef migrate(conn, migrations):\n    # 1. read the current version\n    # 2. run each migration after it, setting user_version as you go\n    # 3. commit and return how many ran\n    pass\n\n\nconn = sqlite3.connect(\":memory:\")\nprint(migrate(conn, MIGRATIONS))   # 3\nprint(migrate(conn, MIGRATIONS))   # 0\n",
        "tests": '''
import sqlite3

M = [
    "CREATE TABLE sites (code TEXT PRIMARY KEY, name TEXT NOT NULL)",
    "ALTER TABLE sites ADD COLUMN city TEXT",
    "CREATE TABLE inspections (id INTEGER PRIMARY KEY, site TEXT, passed INTEGER)",
]

def test_fresh():
    "A new database gets everything, once"
    c = sqlite3.connect(":memory:")
    v, _ = capture(need("migrate"), c, M)
    check(v == 3, "migrate on a new database returned %r, expected 3." % (v,))
    check(c.execute("PRAGMA user_version").fetchone()[0] == 3, "user_version should be 3 afterwards.")
    cols = [r[1] for r in c.execute("PRAGMA table_info(sites)")]
    check(cols == ["code", "name", "city"], "sites has columns %r." % cols)
    v, _ = capture(need("migrate"), c, M)
    check(v == 0, "Running it again returned %r, expected 0." % (v,))

def test_partial():
    "An older database only gets the new ones"
    c = sqlite3.connect(":memory:")
    need("migrate")(c, M[:1])
    c.execute("INSERT INTO sites VALUES ('RYD-N', 'North Plaza')")
    c.commit()
    v, _ = capture(need("migrate"), c, M)
    check(v == 2, "A database at version 1 should get 2 more, got %r." % (v,))
    check(c.execute("SELECT name FROM sites").fetchone()[0] == "North Plaza", "Existing data must survive migrations.")
''',
        "solution": "import sqlite3\n\nMIGRATIONS = [\n    \"CREATE TABLE sites (code TEXT PRIMARY KEY, name TEXT NOT NULL)\",\n    \"ALTER TABLE sites ADD COLUMN city TEXT\",\n    \"CREATE TABLE inspections (id INTEGER PRIMARY KEY, site TEXT REFERENCES sites(code), passed INTEGER)\",\n]\n\n\ndef migrate(conn, migrations):\n    version = conn.execute(\"PRAGMA user_version\").fetchone()[0]\n    applied = 0\n    for number, sql in enumerate(migrations, start=1):\n        if number <= version:\n            continue\n        conn.execute(sql)\n        conn.execute(f\"PRAGMA user_version = {number}\")\n        applied += 1\n    conn.commit()\n    return applied\n\n\nconn = sqlite3.connect(\":memory:\")\nprint(migrate(conn, MIGRATIONS))\nprint(migrate(conn, MIGRATIONS))\n",
        "hints": [
            "`for number, sql in enumerate(migrations, start=1):` numbers them from 1. Skip (`continue`) when `number <= version`.",
            "For the rest: `conn.execute(sql)`, `conn.execute(f\"PRAGMA user_version = {number}\")`, and count it.",
        ],
    },
    {
        "id": "migration-quiz",
        "title": "Fixing a migration",
        "kind": "quiz",
        "body": "The golden rule, tested.",
        "question": "Migration 4, already run on the live server, added a column called `qnty` (a typo). What should you do?",
        "options": [
            "Edit migration 4 to say `quantity`",
            "Add migration 5 that renames `qnty` to `quantity`",
            "Delete the live database and start again",
            "Leave it, typos don't matter",
        ],
        "answer": 1,
        "explain": "The server's database is already at version 4, so an edited migration 4 would never run there, while a fresh database would get the new version. They'd silently differ. A new migration 5 fixes every copy the same way.",
    },
    {
        "id": "postgres",
        "title": "Moving to PostgreSQL",
        "kind": "read",
        "body": """
SQLite is a file that your program opens. That's perfect on one machine, but it struggles once a busy site has many processes writing at once, or several servers sharing one database.

**PostgreSQL** (Postgres) is the usual next step: a database **server** that many apps connect to over the network. Almost all the SQL you know carries straight over. What changes:

| | SQLite | PostgreSQL |
|---|---|---|
| Where | a file | a server you connect to |
| Connect with | `sqlite3.connect("site.db")` | `psycopg.connect(DATABASE_URL)` |
| Parameter marker | `?` | `%s` |
| Auto-numbered id | `INTEGER PRIMARY KEY` | `id SERIAL PRIMARY KEY` or `GENERATED ALWAYS AS IDENTITY` |
| Types | relaxed | strict: text in an INTEGER column is refused |
| Extras | a few | many: JSON columns, full-text search, arrays, proper date/time types |

## Connecting

The connection details go in one environment variable, never in code:

```
DATABASE_URL=postgresql://site_app:secret@localhost:5432/site
```

That's user `site_app`, password `secret`, host `localhost`, port `5432` (Postgres's default), database `site`.

```python
import os
import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    rows = conn.execute("SELECT name FROM sites WHERE city = %s", ("Riyadh",)).fetchall()
```

The easiest way to run Postgres locally is in Docker, which is two chapters away.
""",
    },
    {
        "id": "postgres-quiz",
        "title": "SQLite to PostgreSQL",
        "kind": "quiz",
        "body": "One practical difference that trips up everyone moving across.",
        "question": "You move this line from SQLite to psycopg (PostgreSQL). What has to change?\n\n```python\nconn.execute(\"SELECT * FROM sites WHERE code = ?\", (code,))\n```",
        "options": [
            "Nothing",
            "`?` becomes `%s`",
            "`(code,)` becomes `[code]`",
            "SELECT * isn't allowed in PostgreSQL",
        ],
        "answer": 1,
        "explain": "psycopg uses `%s` as its placeholder. It's still a safe parameter, not Python string formatting, so never fill it in yourself with `%`.",
    },
    {
        "id": "n-plus-one",
        "title": "The N+1 query problem",
        "kind": "code",
        "timeout": T,
        "files": FILES,
        "prelude": DB_PRELUDE,
        "body": """
This looks innocent:

```python
def deliveries_with_names():
    out = []
    for d in conn.execute("SELECT id, material_id, quantity FROM deliveries").fetchall():
        m = conn.execute("SELECT name FROM materials WHERE id = ?", (d["material_id"],)).fetchone()
        out.append({"id": d["id"], "material": m["name"], "quantity": d["quantity"]})
    return out
```

One query for the list, then **one more per row**: with 24 deliveries that's 25 queries. With 10,000 rows on a networked database, the page takes seconds. It's called the **N+1 problem**, and it's one of the most common causes of slow APIs.

The fix is to let the database do the matching in **one** query, with the JOIN from the SQL track.

## Your task

Rewrite `deliveries_with_names()` so it returns the same list (sorted by delivery id) using a **single** query.
""",
        "starter": "def deliveries_with_names():\n    out = []\n    for d in conn.execute(\"SELECT id, material_id, quantity FROM deliveries ORDER BY id\").fetchall():\n        m = conn.execute(\"SELECT name FROM materials WHERE id = ?\", (d[\"material_id\"],)).fetchone()\n        out.append({\"id\": d[\"id\"], \"material\": m[\"name\"], \"quantity\": d[\"quantity\"]})\n    return out\n\n\nprint(deliveries_with_names()[:3])\n",
        "tests": '''
def test_result():
    "Same answer as before"
    db = need("conn")
    want = [{"id": r["id"], "material": r["name"], "quantity": r["quantity"]} for r in db.execute(
        "SELECT d.id, m.name, d.quantity FROM deliveries d JOIN materials m ON d.material_id = m.id ORDER BY d.id")]
    v, _ = capture(need("deliveries_with_names"))
    check(v == want, "The result changed. First rows: %r" % (v[:2] if isinstance(v, list) else v,))

def test_one_query():
    "Uses one query"
    db = need("conn")
    seen = []
    db.set_trace_callback(lambda sql: seen.append(sql))
    try:
        need("deliveries_with_names")()
    finally:
        db.set_trace_callback(None)
    n = len([s for s in seen if s.strip().upper().startswith("SELECT")])
    check(n == 1, "deliveries_with_names ran %d SELECT queries. Use one JOIN instead of a query per row." % n)
''',
        "solution": "def deliveries_with_names():\n    rows = conn.execute(\n        \"\"\"SELECT d.id, m.name AS material, d.quantity\n           FROM deliveries d\n           JOIN materials m ON d.material_id = m.id\n           ORDER BY d.id\"\"\"\n    ).fetchall()\n    return [dict(r) for r in rows]\n\n\nprint(deliveries_with_names()[:3])\n",
        "hints": [
            "`SELECT d.id, m.name AS material, d.quantity FROM deliveries d JOIN materials m ON d.material_id = m.id ORDER BY d.id`",
            "Naming the column `material` with AS means `dict(row)` already has the right keys: `return [dict(r) for r in rows]`.",
        ],
    },
]
