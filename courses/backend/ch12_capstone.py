import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Capstone project",
    "summary": "Plan, build and test a complete small API: an equipment register for a site store.",
}

T = 40

APP_HEAD = '''import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

STORE_KEY = "store-key"

SCHEMA = """
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    checked_out_to TEXT
)
"""


def fresh_conn():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


class EquipmentIn(BaseModel):
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)


class CheckoutIn(BaseModel):
    person: str = Field(min_length=1)
'''

REFERENCE = APP_HEAD + '''

def make_app(conn):
    app = FastAPI(title="Equipment register")

    def require_key(x_api_key: str = Header(None)):
        if x_api_key != STORE_KEY:
            raise HTTPException(status_code=401, detail="missing or invalid API key")

    def find(item_id):
        row = conn.execute("SELECT * FROM equipment WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="equipment not found")
        return dict(row)

    @app.get("/equipment")
    def list_equipment(available: bool = None):
        rows = conn.execute("SELECT * FROM equipment ORDER BY id").fetchall()
        items = [dict(r) for r in rows]
        if available is None:
            return items
        return [i for i in items if (i["checked_out_to"] is None) == available]

    @app.post("/equipment", status_code=201, dependencies=[Depends(require_key)])
    def add_equipment(e: EquipmentIn):
        cur = conn.execute("INSERT INTO equipment (name, category) VALUES (?, ?)", (e.name, e.category))
        conn.commit()
        return find(cur.lastrowid)

    @app.get("/equipment/{item_id}")
    def get_equipment(item_id: int):
        return find(item_id)

    @app.post("/equipment/{item_id}/checkout", dependencies=[Depends(require_key)])
    def checkout(item_id: int, c: CheckoutIn):
        item = find(item_id)
        if item["checked_out_to"] is not None:
            raise HTTPException(status_code=409, detail="already checked out")
        conn.execute("UPDATE equipment SET checked_out_to = ? WHERE id = ?", (c.person, item_id))
        conn.commit()
        return find(item_id)

    @app.post("/equipment/{item_id}/return", dependencies=[Depends(require_key)])
    def return_item(item_id: int):
        item = find(item_id)
        if item["checked_out_to"] is None:
            raise HTTPException(status_code=409, detail="not checked out")
        conn.execute("UPDATE equipment SET checked_out_to = NULL WHERE id = ?", (item_id,))
        conn.commit()
        return find(item_id)

    return app
'''

SPEC = """
| Route | Key needed? | Does |
|---|---|---|
| `GET /equipment` | no | every item, in id order; with `?available=true` only items not checked out, with `?available=false` only items that are |
| `POST /equipment` | yes | body `{"name", "category"}` (both at least 1 character); **201** with the new item |
| `GET /equipment/{item_id}` | no | one item, or **404** |
| `POST /equipment/{item_id}/checkout` | yes | body `{"person"}`; sets `checked_out_to`; **409** if it's already out; **404** if no such item |
| `POST /equipment/{item_id}/return` | yes | clears `checked_out_to`; **409** if it isn't out; **404** if no such item |

Every item is returned as `{"id", "name", "category", "checked_out_to"}` (`checked_out_to` is `null` when it's in the store). Routes that need a key reply **401** without the header `X-API-Key: store-key`.
"""

LESSONS = [
    {
        "id": "capstone-plan",
        "title": "The project",
        "kind": "read",
        "body": """
The last chapter is one complete API, built the way you would at work: plan it, build it, test it, package it.

## The brief

The site store lends out equipment (laser levels, drills, harnesses) and loses track of who has what. They want a small API that their tablet app can use to:

- list the equipment, and see what's available,
- add new equipment (store staff only),
- check an item out to a person, and back in (store staff only).

## The design

Following the API design chapter: resources as nouns, methods as verbs, meaningful status codes, and an API key for anything that changes data.
""" + SPEC + """
## The plan

1. **Build it** with FastAPI and SQLite, inside a `make_app(conn)` function so each test can give it a fresh database.
2. **Test it**, with tests good enough to catch real bugs.
3. **Package it** with the Dockerfile and compose file from the Docker chapter.

Read the table twice. Most bugs in real projects come from not reading the spec closely.
""",
    },
    {
        "id": "capstone-build",
        "title": "Build the API",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
The starter has the database schema, the request models and a `fresh_conn()` helper. Everything else goes inside `make_app(conn)`, which builds and returns the app. Putting the routes inside a function means each test can build its own app around its own empty database.

Here's the spec again:
""" + SPEC + """
Suggested order, using **Run** after each step:

1. `require_key`, a dependency that raises 401 (the authentication chapter's `current_user`, simplified). Attach it to a route with `dependencies=[Depends(require_key)]` in the decorator.
2. a `find(item_id)` helper returning the item as a dict, or raising 404.
3. `GET /equipment/{item_id}` and `POST /equipment`.
4. `GET /equipment`, then the `available` filter (`available: bool = None`).
5. checkout and return, with their 409s.
""",
        "starter": APP_HEAD + '''

def make_app(conn):
    app = FastAPI(title="Equipment register")

    # 1. require_key dependency
    # 2. find(item_id) helper
    # 3-5. routes

    return app


app = make_app(fresh_conn())
H = {"X-API-Key": STORE_KEY}
call(app, "POST", "/equipment", json={"name": "Laser level", "category": "survey"}, headers=H)
call(app, "POST", "/equipment/1/checkout", json={"person": "Karim"}, headers=H)
call(app, "GET", "/equipment?available=false")
''',
        "tests": '''
from fastapi.testclient import TestClient

H = {"X-API-Key": "store-key"}

def client():
    return TestClient(need("make_app")(need("fresh_conn")()))

def test_add_and_get():
    "Add (with a key) and get"
    c = client()
    r = c.post("/equipment", json={"name": "Laser level", "category": "survey"}, headers=H)
    check(r.status_code == 201, "POST /equipment with the key gave %s %s." % (r.status_code, r.text))
    check(r.json() == {"id": 1, "name": "Laser level", "category": "survey", "checked_out_to": None}, "The new item came back as %s." % r.text)
    r = c.get("/equipment/1")
    check(r.status_code == 200 and r.json()["name"] == "Laser level", "GET /equipment/1 gave %s %s." % (r.status_code, r.text))
    check(c.get("/equipment/42").status_code == 404, "GET /equipment/42 should be 404.")
    check(c.post("/equipment", json={"name": "", "category": "survey"}, headers=H).status_code == 422, "An empty name should be 422.")

def test_auth():
    "Changes need the key"
    c = client()
    check(c.post("/equipment", json={"name": "Drill", "category": "power"}).status_code == 401, "POST /equipment without a key should be 401.")
    check(c.post("/equipment", json={"name": "Drill", "category": "power"}, headers={"X-API-Key": "nope"}).status_code == 401, "A wrong key should be 401.")
    c.post("/equipment", json={"name": "Drill", "category": "power"}, headers=H)
    check(c.post("/equipment/1/checkout", json={"person": "Omar"}).status_code == 401, "checkout without a key should be 401.")
    check(c.post("/equipment/1/return").status_code == 401, "return without a key should be 401.")
    check(c.get("/equipment").status_code == 200, "Reading the list shouldn't need a key.")

def test_checkout_return():
    "Checkout and return, with their errors"
    c = client()
    c.post("/equipment", json={"name": "Harness", "category": "safety"}, headers=H)
    r = c.post("/equipment/1/checkout", json={"person": "Rana"}, headers=H)
    check(r.status_code == 200 and r.json()["checked_out_to"] == "Rana", "Checkout gave %s %s." % (r.status_code, r.text))
    check(c.post("/equipment/1/checkout", json={"person": "Omar"}, headers=H).status_code == 409, "Checking out an item that's already out should be 409.")
    r = c.post("/equipment/1/return", headers=H)
    check(r.status_code == 200 and r.json()["checked_out_to"] is None, "Return gave %s %s." % (r.status_code, r.text))
    check(c.post("/equipment/1/return", headers=H).status_code == 409, "Returning an item that isn't out should be 409.")
    check(c.post("/equipment/9/checkout", json={"person": "x"}, headers=H).status_code == 404, "Checking out a missing item should be 404.")
    check(c.post("/equipment/9/return", headers=H).status_code == 404, "Returning a missing item should be 404.")

def test_list_filter():
    "The list and its available filter"
    c = client()
    for n in ("Level", "Drill", "Saw"):
        c.post("/equipment", json={"name": n, "category": "tools"}, headers=H)
    c.post("/equipment/2/checkout", json={"person": "Adel"}, headers=H)
    names = lambda r: [i["name"] for i in r.json()]
    check(names(c.get("/equipment")) == ["Level", "Drill", "Saw"], "GET /equipment gave %s." % c.get("/equipment").text)
    check(names(c.get("/equipment", params={"available": "true"})) == ["Level", "Saw"], "?available=true gave %s." % c.get("/equipment", params={"available": "true"}).text)
    check(names(c.get("/equipment", params={"available": "false"})) == ["Drill"], "?available=false gave %s." % c.get("/equipment", params={"available": "false"}).text)
''',
        "solution": REFERENCE + '''

app = make_app(fresh_conn())
H = {"X-API-Key": STORE_KEY}
call(app, "POST", "/equipment", json={"name": "Laser level", "category": "survey"}, headers=H)
call(app, "POST", "/equipment/1/checkout", json={"person": "Karim"}, headers=H)
call(app, "GET", "/equipment?available=false")
''',
        "hints": [
            "require_key: `def require_key(x_api_key: str = Header(None)):` and raise a 401 HTTPException if it isn't `STORE_KEY`.",
            "find: `SELECT * FROM equipment WHERE id = ?`, 404 if None, else `dict(row)`. Every route can return `find(...)` at the end.",
            "Filter: `[i for i in items if (i[\"checked_out_to\"] is None) == available]` when `available` isn't None.",
        ],
    },
    {
        "id": "capstone-tests",
        "title": "Test the API",
        "kind": "code",
        "timeout": T,
        "body": """
The starter holds a working version of the equipment API (the model answer to the last lesson). Your job now is the test suite that would protect it from future changes.

Each test should build its own app with a fresh database, so tests can't affect each other:

```python
def new_client():
    return TestClient(make_app(fresh_conn()))
```

As in the testing chapter, the checks run your tests against the working API (they must pass), then against broken versions (they must fail).

## Your task

Write `test_` functions that together cover:

- adding equipment **without** a key is refused with 401
- adding with the key gives 201
- checking out an item that's already checked out gives 409
- returning an item that isn't checked out gives 409
- the `available=true` filter leaves out checked-out items
""",
        "starter": REFERENCE + '''

from fastapi.testclient import TestClient

H = {"X-API-Key": STORE_KEY}


def new_client():
    return TestClient(make_app(fresh_conn()))


def test_add_needs_key():
    c = new_client()
    r = c.post("/equipment", json={"name": "Drill", "category": "power"})
    assert r.status_code == 401


# more test_ functions here


for name, fn in list(globals().items()):
    if name.startswith("test_"):
        fn()
        print("passed:", name)
''',
        "tests": '''
import sqlite3
from fastapi import Depends, FastAPI, Header, HTTPException

def learner_tests():
    return [(k, v) for k, v in ns.items() if k.startswith("test_") and callable(v)]

def run_all():
    out = []
    for n, fn in learner_tests():
        try:
            fn()
            out.append((n, None))
        except BaseException as e:
            out.append((n, e))
    return out

def with_factory(factory):
    real = ns["make_app"]
    ns["make_app"] = factory
    try:
        return run_all()
    finally:
        ns["make_app"] = real

def mutant(bug):
    EquipmentIn, CheckoutIn, KEY = ns["EquipmentIn"], ns["CheckoutIn"], ns["STORE_KEY"]
    def make(conn):
        app = FastAPI()
        def require_key(x_api_key: str = Header(None)):
            if bug != "no_auth" and x_api_key != KEY:
                raise HTTPException(status_code=401, detail="no")
        def find(i):
            row = conn.execute("SELECT * FROM equipment WHERE id = ?", (i,)).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="no")
            return dict(row)
        @app.get("/equipment")
        def lst(available: bool = None):
            items = [dict(r) for r in conn.execute("SELECT * FROM equipment ORDER BY id")]
            if available is None or bug == "no_filter":
                return items
            return [i for i in items if (i["checked_out_to"] is None) == available]
        @app.post("/equipment", status_code=200 if bug == "status_200" else 201, dependencies=[Depends(require_key)])
        def add(e: EquipmentIn):
            cur = conn.execute("INSERT INTO equipment (name, category) VALUES (?, ?)", (e.name, e.category))
            return find(cur.lastrowid)
        @app.post("/equipment/{i}/checkout", dependencies=[Depends(require_key)])
        def co(i: int, c: CheckoutIn):
            item = find(i)
            if item["checked_out_to"] is not None and bug != "double_checkout":
                raise HTTPException(status_code=409, detail="no")
            conn.execute("UPDATE equipment SET checked_out_to = ? WHERE id = ?", (c.person, i))
            return find(i)
        @app.post("/equipment/{i}/return", dependencies=[Depends(require_key)])
        def ret(i: int):
            item = find(i)
            if item["checked_out_to"] is None and bug != "double_return":
                raise HTTPException(status_code=409, detail="no")
            conn.execute("UPDATE equipment SET checked_out_to = NULL WHERE id = ?", (i,))
            return find(i)
        return app
    return make

def test_pass_on_good_code():
    "Your tests pass on the working API"
    res = run_all()
    check(len(res) >= 5, "Write at least 5 test_ functions. Found %d." % len(res))
    bad = [(n, e) for n, e in res if e is not None]
    check(not bad, "%s fails on the working API: %r" % (bad[0][0], bad[0][1]) if bad else "")

def test_catches_bugs():
    "Your tests catch broken versions"
    msgs = {
        "no_auth": "An API that lets anyone add equipment passed your tests.",
        "status_200": "An API that replies 200 instead of 201 when adding passed.",
        "double_checkout": "An API that lets an item be checked out twice passed.",
        "double_return": "An API that lets an item be returned when it isn't out passed.",
        "no_filter": "An API that ignores ?available=true passed.",
    }
    for bug, msg in msgs.items():
        res = with_factory(mutant(bug))
        check(any(e is not None for _, e in res), msg)
''',
        "solution": REFERENCE + '''

from fastapi.testclient import TestClient

H = {"X-API-Key": STORE_KEY}


def new_client():
    return TestClient(make_app(fresh_conn()))


def test_add_needs_key():
    c = new_client()
    r = c.post("/equipment", json={"name": "Drill", "category": "power"})
    assert r.status_code == 401


def test_add_with_key():
    c = new_client()
    r = c.post("/equipment", json={"name": "Drill", "category": "power"}, headers=H)
    assert r.status_code == 201
    assert r.json()["name"] == "Drill"


def test_double_checkout():
    c = new_client()
    c.post("/equipment", json={"name": "Drill", "category": "power"}, headers=H)
    assert c.post("/equipment/1/checkout", json={"person": "Omar"}, headers=H).status_code == 200
    assert c.post("/equipment/1/checkout", json={"person": "Lina"}, headers=H).status_code == 409


def test_return_when_not_out():
    c = new_client()
    c.post("/equipment", json={"name": "Drill", "category": "power"}, headers=H)
    assert c.post("/equipment/1/return", headers=H).status_code == 409


def test_available_filter():
    c = new_client()
    c.post("/equipment", json={"name": "Drill", "category": "power"}, headers=H)
    c.post("/equipment", json={"name": "Level", "category": "survey"}, headers=H)
    c.post("/equipment/1/checkout", json={"person": "Omar"}, headers=H)
    names = [i["name"] for i in c.get("/equipment", params={"available": "true"}).json()]
    assert names == ["Level"]


for name, fn in list(globals().items()):
    if name.startswith("test_"):
        fn()
        print("passed:", name)
''',
        "hints": [
            "Every test starts with `c = new_client()` and adds the equipment it needs, so it doesn't depend on any other test.",
            "For the 409 tests, set up the state first (check an item out, or not), then make the request that should be refused.",
        ],
    },
    {
        "id": "capstone-ship",
        "title": "Shipping it",
        "kind": "read",
        "body": """
You've built and tested a real API. Here's how it becomes a running service, using everything from the last three chapters.

## The project folder

```
equipment-api/
    main.py            make_app(), plus: app = make_app(sqlite3.connect(DATABASE_PATH, ...))
    test_main.py       your tests
    requirements.txt   fastapi, uvicorn
    Dockerfile         from the Docker chapter
    .dockerignore
    .gitignore
    .env.example       STORE_KEY=change-me
    README.md          what it is, how to run it, how to test it
```

Two changes from the exercise version: `STORE_KEY` comes from `os.environ`, not the code, and the database is a file path (or, later, a PostgreSQL URL) from the environment too.

## The routine

1. `pytest` passes locally.
2. Commit on a branch, push, open a pull request.
3. Merge to `main`.
4. The platform builds the Docker image and deploys it, with `STORE_KEY` and the database settings set in its dashboard.
5. Check `/health` and `/docs` on the live URL.

## Where to go next

- **SQLAlchemy** and **Alembic**: the standard tools for databases and migrations in larger Python apps.
- **GitHub Actions**: run your tests automatically on every pull request.
- **Async Python** (`async def` routes): handling many slow requests at once.
- Build something you need. A register like this one, a calculator service for your team's spreadsheets, a small dashboard API. That's where it all comes together.

Well done. That's the whole path: Python, SQL, engineering computation and back-end development.
""",
    },
]
