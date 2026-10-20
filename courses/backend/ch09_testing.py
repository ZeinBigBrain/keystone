import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Testing back-end code",
    "summary": "Writing your own tests: unittest, plain assert tests, testing endpoints, fresh state for every test, and mocking.",
}

T = 30

# Checks for this chapter grade YOUR tests: they must pass on the correct
# code, and fail on deliberately broken versions of it ("mutants").
RUNNER = '''
import unittest, io

def run_unittest_cases():
    """Run every TestCase class the learner defined. Returns (count, result)."""
    suite = unittest.TestSuite()
    for obj in list(ns.values()):
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj is not unittest.TestCase:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(obj))
    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return suite.countTestCases(), res

def learner_test_functions():
    return [(k, v) for k, v in ns.items() if k.startswith("test_") and callable(v) and not isinstance(v, type)]

def run_functions():
    """Run plain test_ functions. Returns list of (name, error or None)."""
    out = []
    for name, fn in learner_test_functions():
        try:
            fn()
            out.append((name, None))
        except BaseException as e:
            out.append((name, e))
    return out

def with_swapped(name, replacement, runner):
    """Run the learner's tests with ns[name] temporarily replaced."""
    real = ns[name]
    ns[name] = replacement
    try:
        return runner()
    finally:
        ns[name] = real
'''

UTIL_FN = '''def utilisation(demand, capacity):
    """Demand over capacity, to 3 decimal places."""
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    return round(demand / capacity, 3)
'''

LESSONS = [
    {
        "id": "why-test",
        "title": "Why write tests",
        "kind": "read",
        "body": """
Every exercise in Keystone has had tests: the checks that run when you press Submit. Now you write them yourself.

An automated test is a small piece of code that runs your code with known inputs and **checks** the result. Once written, it runs in a second, as often as you like, and it never gets bored or forgets a case.

## What tests buy you

- **Confidence to change things.** Refactor, upgrade a library, fix a bug: if the tests still pass, you haven't broken the things they check.
- **Bugs stay fixed.** When you fix a bug, add a test that would have caught it. It can never quietly come back.
- **Documentation that can't go stale.** A test shows exactly how the code is meant to be used, and it fails the moment that stops being true.

## What makes a good test

1. **Arrange** the inputs, **act** (call the code), **assert** the result.
2. One behaviour per test, named after it: `test_rejects_zero_capacity`.
3. Cover the **edges**, not just the easy middle: zero, empty, the boundary value, the wrong type, the error case.

## How this chapter checks your tests

A test that always passes is worthless. So the checks run your tests twice: once against the correct code (they must **pass**), and then against deliberately broken versions of it (they must **fail**). If a broken version slips through, the message tells you which behaviour you haven't tested yet.
""",
    },
    {
        "id": "unittest",
        "title": "unittest",
        "kind": "code",
        "timeout": T,
        "body": """
Python's built-in test framework is `unittest`. Tests are methods on a class that inherits from `unittest.TestCase`, and each method's name starts with `test_`:

```python
import unittest

class TestGrade(unittest.TestCase):
    def test_pass_mark(self):
        self.assertEqual(grade(40), "D")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            grade(-5)
```

The checks you'll use most:

| Method | Passes when |
|---|---|
| `assertEqual(a, b)` | `a == b` |
| `assertTrue(x)` / `assertFalse(x)` | `x` is truthy / falsy |
| `assertAlmostEqual(a, b, places=3)` | floats agree to 3 places |
| `assertRaises(SomeError)` | the code inside the `with` raises that error |

At the bottom of a test file, `unittest.main()` runs them. In the editor, use `unittest.main(argv=["x"], exit=False)` so it doesn't try to quit.

## Your task

`utilisation(demand, capacity)` is given. Write a `TestCase` with **at least three** tests that together check:

- a normal value (for example, 50 out of 100 is 0.5)
- that the result is **rounded to 3 places** (2 out of 3 is 0.667)
- that a capacity of 0 raises `ValueError`
""",
        "starter": "import unittest\n\n\n" + UTIL_FN + "\n\nclass TestUtilisation(unittest.TestCase):\n    def test_normal(self):\n        pass   # replace with an assertEqual\n\n\nunittest.main(argv=[\"x\"], exit=False)\n",
        "tests": RUNNER + '''
def good_run():
    n, res = run_unittest_cases()
    return n, res

def test_pass_on_good_code():
    "Your tests pass on the correct code"
    n, res = good_run()
    check(n >= 3, "Write at least 3 test methods (their names must start with test_). Found %d." % n)
    problems = res.failures + res.errors
    check(not problems, "Your tests fail on the correct code:\\n" + (problems[0][1].strip().splitlines()[-1] if problems else ""))
    check("pass   # replace" not in RAW_CODE, "Replace the placeholder pass with a real assert.")

def caught(mutant):
    n, res = with_swapped("utilisation", mutant, run_unittest_cases)
    return bool(res.failures or res.errors)

def test_catches_bugs():
    "Your tests catch broken versions"
    def no_round(d, c):
        if c <= 0:
            raise ValueError("x")
        return d / c
    def swapped(d, c):
        if c <= 0:
            raise ValueError("x")
        return round(c / d, 3) if d else 0
    def no_check(d, c):
        return round(d / c, 3) if c else 0.0
    check(caught(swapped), "A version that divides the wrong way round still passed your tests. Check a normal value like utilisation(50, 100) == 0.5.")
    check(caught(no_round), "A version that doesn't round still passed. Check utilisation(2, 3) == 0.667.")
    check(caught(no_check), "A version that accepts capacity 0 still passed. Use assertRaises(ValueError).")
''',
        "solution": "import unittest\n\n\n" + UTIL_FN + "\n\nclass TestUtilisation(unittest.TestCase):\n    def test_normal(self):\n        self.assertEqual(utilisation(50, 100), 0.5)\n\n    def test_rounds_to_three_places(self):\n        self.assertEqual(utilisation(2, 3), 0.667)\n\n    def test_rejects_zero_capacity(self):\n        with self.assertRaises(ValueError):\n            utilisation(10, 0)\n\n\nunittest.main(argv=[\"x\"], exit=False)\n",
        "hints": [
            "`self.assertEqual(utilisation(50, 100), 0.5)` for the first.",
            "For the error: `with self.assertRaises(ValueError):` then `utilisation(10, 0)` indented under it.",
        ],
    },
    {
        "id": "assert-tests",
        "title": "Plain assert tests",
        "kind": "code",
        "timeout": T,
        "body": """
Most Python projects use **pytest** instead of `unittest`. Its big appeal: a test is just a function starting with `test_`, and it checks things with plain `assert`:

```python
def test_pass_mark():
    assert grade(40) == "D"

def test_top_band():
    assert grade(95) == "A"
```

`assert condition` does nothing when the condition is true, and raises `AssertionError` when it's false. pytest finds every `test_` function in files named `test_*.py`, runs them, and reports in detail. You'd install it with `python -m pip install pytest` and run `pytest` in the project folder.

The checks here run your `test_` functions the same way pytest would.

## Your task

`parse_qty(text)` turns text like `"12 t"` into the number `12.0`. Write `test_` functions with `assert` that check it handles:

- a space between the number and the unit: `"12 t"` gives `12.0`
- no space: `"3.5t"` gives `3.5`
- a decimal value is kept as a decimal (not rounded to a whole number)
- spaces around the whole thing: `" 7 t "` gives `7.0`
""",
        "starter": "def parse_qty(text):\n    \"\"\"'12 t' -> 12.0\"\"\"\n    return float(text.strip().rstrip(\"t\").strip())\n\n\ndef test_with_space():\n    assert parse_qty(\"12 t\") == 12.0\n\n\n# more test_ functions here\n\n\n# run them all (pytest would do this for you)\nfor name, fn in list(globals().items()):\n    if name.startswith(\"test_\"):\n        fn()\n        print(\"passed:\", name)\n",
        "tests": RUNNER + '''
def test_pass_on_good_code():
    "Your tests pass on the correct code"
    results = run_functions()
    check(len(results) >= 3, "Write at least 3 test_ functions. Found %d." % len(results))
    bad = [(n, e) for n, e in results if e is not None]
    check(not bad, "%s fails on the correct code: %r" % (bad[0][0], bad[0][1]) if bad else "")

def caught(mutant):
    return any(e is not None for _, e in with_swapped("parse_qty", mutant, run_functions))

def test_catches_bugs():
    "Your tests catch broken versions"
    check(caught(lambda t: float(t.split()[0])), "A version that only works with a space before the unit passed. Test \\"3.5t\\".")
    check(caught(lambda t: float(int(float(t.strip().rstrip("t").strip())))), "A version that drops the decimals passed. Test a value like 3.5.")
    check(caught(lambda t: float(t.rstrip("t"))), "A version that can't cope with spaces around the text passed. Test \\" 7 t \\".")
''',
        "solution": "def parse_qty(text):\n    \"\"\"'12 t' -> 12.0\"\"\"\n    return float(text.strip().rstrip(\"t\").strip())\n\n\ndef test_with_space():\n    assert parse_qty(\"12 t\") == 12.0\n\n\ndef test_without_space():\n    assert parse_qty(\"3.5t\") == 3.5\n\n\ndef test_keeps_decimals():\n    assert parse_qty(\"0.25 t\") == 0.25\n\n\ndef test_outer_spaces():\n    assert parse_qty(\" 7 t \") == 7.0\n\n\nfor name, fn in list(globals().items()):\n    if name.startswith(\"test_\"):\n        fn()\n        print(\"passed:\", name)\n",
        "hints": [
            "Each test is two lines: `def test_something():` and an `assert parse_qty(...) == ...`.",
            "\"3.5t\" covers both \"no space\" and \"keeps the decimal\".",
        ],
    },
    {
        "id": "good-test-quiz",
        "title": "Which test is most useful?",
        "kind": "quiz",
        "body": "Testing time is limited. Spend it where bugs live.",
        "question": "`shipping_cost(kg)` charges 5 up to 2 kg and 12 above. Which single test is most likely to catch a bug?",
        "options": [
            "`assert shipping_cost(1) == 5`",
            "`assert shipping_cost(2) == 5` (exactly on the boundary)",
            "`assert shipping_cost(100) == 12`",
            "`assert shipping_cost(1) == shipping_cost(1)`",
        ],
        "answer": 1,
        "explain": "Bugs cluster at boundaries: `<` written where `<=` was meant. 1 kg and 100 kg sit comfortably inside their bands and pass either way. The last option tests nothing at all.",
    },
    {
        "id": "test-endpoints",
        "title": "Testing endpoints",
        "kind": "code",
        "timeout": T,
        "body": """
FastAPI's `TestClient` (which the exercises have been using behind the scenes) lets a test call your API without starting a server:

```python
from fastapi.testclient import TestClient

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

Test the **status code** as well as the body. A route that returns the right data with the wrong status (200 instead of 201, say) will confuse every client.

## Your task

The starter's `app` has `POST /items` (name required, at least 1 character; replies 201) and `GET /items/{item_id}` (404 if missing). Write `test_` functions that check:

- creating an item gives **201** and returns its name
- an empty name is rejected with **422**
- getting a missing item gives **404**
""",
        "starter": "from fastapi import FastAPI, HTTPException\nfrom fastapi.testclient import TestClient\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\nITEMS = {}\n\n\nclass ItemIn(BaseModel):\n    name: str = Field(min_length=1)\n\n\n@app.post(\"/items\", status_code=201)\ndef create_item(item: ItemIn):\n    new = {\"id\": len(ITEMS) + 1, \"name\": item.name}\n    ITEMS[new[\"id\"]] = new\n    return new\n\n\n@app.get(\"/items/{item_id}\")\ndef get_item(item_id: int):\n    if item_id not in ITEMS:\n        raise HTTPException(status_code=404, detail=\"not found\")\n    return ITEMS[item_id]\n\n\n# your test_ functions here (use TestClient(app) inside each one)\n\n\nfor name, fn in list(globals().items()):\n    if name.startswith(\"test_\"):\n        fn()\n        print(\"passed:\", name)\n",
        "tests": RUNNER + '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

def test_pass_on_good_code():
    "Your tests pass on the correct app"
    results = run_functions()
    check(len(results) >= 3, "Write at least 3 test_ functions. Found %d." % len(results))
    bad = [(n, e) for n, e in results if e is not None]
    check(not bad, "%s fails on the correct app: %r" % (bad[0][0], bad[0][1]) if bad else "")

def make_app(status=201, min_len=1, missing_404=True):
    a = FastAPI()
    items = {}
    class In(BaseModel):
        name: str = Field(min_length=min_len)
    @a.post("/items", status_code=status)
    def c(item: In):
        new = {"id": len(items) + 1, "name": item.name}
        items[new["id"]] = new
        return new
    @a.get("/items/{item_id}")
    def g(item_id: int):
        if item_id not in items:
            if missing_404:
                raise HTTPException(status_code=404, detail="not found")
            return None
        return items[item_id]
    return a

def caught(mutant_app):
    return any(e is not None for _, e in with_swapped("app", mutant_app, run_functions))

def test_catches_bugs():
    "Your tests catch broken apps"
    check(caught(make_app(status=200)), "An app that replies 200 instead of 201 passed your tests. Check r.status_code == 201.")
    check(caught(make_app(min_len=0)), "An app that accepts an empty name passed. Post {\\"name\\": \\"\\"} and check for 422.")
    check(caught(make_app(missing_404=False)), "An app that returns 200 for a missing item passed. GET a missing id and check for 404.")
''',
        "solution": "from fastapi import FastAPI, HTTPException\nfrom fastapi.testclient import TestClient\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\nITEMS = {}\n\n\nclass ItemIn(BaseModel):\n    name: str = Field(min_length=1)\n\n\n@app.post(\"/items\", status_code=201)\ndef create_item(item: ItemIn):\n    new = {\"id\": len(ITEMS) + 1, \"name\": item.name}\n    ITEMS[new[\"id\"]] = new\n    return new\n\n\n@app.get(\"/items/{item_id}\")\ndef get_item(item_id: int):\n    if item_id not in ITEMS:\n        raise HTTPException(status_code=404, detail=\"not found\")\n    return ITEMS[item_id]\n\n\ndef test_create_gives_201():\n    r = TestClient(app).post(\"/items\", json={\"name\": \"laser level\"})\n    assert r.status_code == 201\n    assert r.json()[\"name\"] == \"laser level\"\n\n\ndef test_empty_name_rejected():\n    r = TestClient(app).post(\"/items\", json={\"name\": \"\"})\n    assert r.status_code == 422\n\n\ndef test_missing_item_404():\n    r = TestClient(app).get(\"/items/9999\")\n    assert r.status_code == 404\n\n\nfor name, fn in list(globals().items()):\n    if name.startswith(\"test_\"):\n        fn()\n        print(\"passed:\", name)\n",
        "hints": [
            "Each test: `r = TestClient(app).post(...)` or `.get(...)`, then `assert r.status_code == ...`.",
            "Use an id that can't exist, like 9999, for the 404 test.",
        ],
    },
    {
        "id": "fresh-state",
        "title": "A fresh start for every test",
        "kind": "code",
        "timeout": T,
        "body": """
Tests must not depend on each other. If test B only passes because test A happened to run first and leave data behind, you've got a test suite that breaks in mysterious ways.

`unittest` runs a method called `setUp` before **every** test. Build fresh objects there:

```python
class TestTank(unittest.TestCase):
    def setUp(self):
        self.tank = Tank(1000)          # a brand-new tank for each test

    def test_starts_empty(self):
        self.assertEqual(self.tank.level, 0)

    def test_fill(self):
        self.tank.fill(300)
        self.assertEqual(self.tank.level, 300)
```

(pytest's version of this is called a **fixture**. Same idea.) For database code, `setUp` typically creates a fresh in-memory SQLite database, so every test starts from the same known data.

## Your task

`Store` keeps stock levels. Write a `TestCase` with a `setUp` that makes a new `Store` and adds `10` of `"cement"`. Then write tests that check:

- `remove("cement", 4)` leaves 6
- removing more than there is raises `ValueError` and leaves the stock unchanged
- `level("sand")` is 0 for something never added
""",
        "starter": "import unittest\n\n\nclass Store:\n    def __init__(self):\n        self.stock = {}\n\n    def add(self, item, qty):\n        self.stock[item] = self.stock.get(item, 0) + qty\n\n    def remove(self, item, qty):\n        if qty > self.stock.get(item, 0):\n            raise ValueError(\"not enough stock\")\n        self.stock[item] -= qty\n\n    def level(self, item):\n        return self.stock.get(item, 0)\n\n\nclass TestStore(unittest.TestCase):\n    def setUp(self):\n        pass   # a fresh Store with 10 cement\n\n    # your tests here\n\n\nunittest.main(argv=[\"x\"], exit=False)\n",
        "tests": RUNNER + '''
import unittest

def test_setup():
    "setUp builds a fresh store"
    cases = [o for o in ns.values() if isinstance(o, type) and issubclass(o, unittest.TestCase) and o is not unittest.TestCase]
    check(cases and any("setUp" in c.__dict__ for c in cases), "Define setUp on your TestCase.")
    n, res = run_unittest_cases()
    check(n >= 3, "Write at least 3 tests. Found %d." % n)
    problems = res.failures + res.errors
    check(not problems, "Your tests fail on the correct code:\\n" + (problems[0][1].strip().splitlines()[-1] if problems else ""))

def caught(mutant_cls):
    n, res = with_swapped("Store", mutant_cls, run_unittest_cases)
    return bool(res.failures or res.errors)

def test_catches_bugs():
    "Your tests catch broken stores"
    Real = ns["Store"]
    class NoCheck(Real):
        def remove(self, item, qty):
            self.stock[item] = self.stock.get(item, 0) - qty
    class PartialRemove(Real):
        def remove(self, item, qty):
            have = self.stock.get(item, 0)
            self.stock[item] = max(0, have - qty)
            if qty > have:
                raise ValueError("not enough stock")
    class AddsInstead(Real):
        def remove(self, item, qty):
            if qty > self.stock.get(item, 0):
                raise ValueError("not enough stock")
            self.stock[item] = self.stock[item] + 0
    class Missing(Real):
        def level(self, item):
            return self.stock[item]
    check(caught(AddsInstead), "A store whose remove() doesn't reduce the stock passed. Check the level is 6 after removing 4.")
    check(caught(NoCheck), "A store that lets stock go negative passed. Check that removing too much raises ValueError.")
    check(caught(PartialRemove), "A store that changes the stock before refusing passed. After the ValueError, check the level is still 10.")
    check(caught(Missing), "A store that crashes for items never added passed. Check level(\\"sand\\") == 0.")
''',
        "solution": "import unittest\n\n\nclass Store:\n    def __init__(self):\n        self.stock = {}\n\n    def add(self, item, qty):\n        self.stock[item] = self.stock.get(item, 0) + qty\n\n    def remove(self, item, qty):\n        if qty > self.stock.get(item, 0):\n            raise ValueError(\"not enough stock\")\n        self.stock[item] -= qty\n\n    def level(self, item):\n        return self.stock.get(item, 0)\n\n\nclass TestStore(unittest.TestCase):\n    def setUp(self):\n        self.store = Store()\n        self.store.add(\"cement\", 10)\n\n    def test_remove(self):\n        self.store.remove(\"cement\", 4)\n        self.assertEqual(self.store.level(\"cement\"), 6)\n\n    def test_remove_too_much(self):\n        with self.assertRaises(ValueError):\n            self.store.remove(\"cement\", 11)\n        self.assertEqual(self.store.level(\"cement\"), 10)\n\n    def test_unknown_item(self):\n        self.assertEqual(self.store.level(\"sand\"), 0)\n\n\nunittest.main(argv=[\"x\"], exit=False)\n",
        "hints": [
            "setUp: `self.store = Store()` and `self.store.add(\"cement\", 10)`. Every test then uses `self.store`.",
            "For the too-much test, put the remove inside `with self.assertRaises(ValueError):`, then check the level after the `with` block.",
        ],
    },
    {
        "id": "mocking",
        "title": "Mocking outside services",
        "kind": "code",
        "timeout": T,
        "body": """
Some code talks to the outside world: an exchange-rate API, an email service, a payment gateway. Your tests shouldn't. They'd be slow, flaky, need the internet, and might even send real emails.

The answer is to **mock** that call: replace it, just for the test, with a stand-in that returns a fixed answer. `unittest.mock.patch.object` swaps an attribute on an object for the length of a `with` block:

```python
from unittest.mock import patch

with patch.object(weather, "fetch_forecast", return_value={"rain_mm": 0}):
    assert can_pour_today() is True       # fetch_forecast is fake in here
# ...and back to the real one out here
```

You're testing **your** logic (what you do with the rate), not the other company's API.

## Your task

`price_in_usd(sar)` asks `exchange.fetch_rate()` for the SAR to USD rate. The real `fetch_rate` refuses to run in tests. Write `test_` functions that mock `fetch_rate` and check:

- with a rate of `0.2666`, `price_in_usd(100)` is `26.66`
- the result is rounded to 2 places: with a rate of `0.12345`, `price_in_usd(10)` is `1.23`
""",
        "starter": "from unittest.mock import patch\n\n\nclass exchange:\n    \"\"\"Stands in for a module that calls a real exchange-rate API.\"\"\"\n    @staticmethod\n    def fetch_rate():\n        raise RuntimeError(\"fetch_rate tried to call the internet. Mock it in tests.\")\n\n\ndef price_in_usd(sar):\n    return round(sar * exchange.fetch_rate(), 2)\n\n\n# your test_ functions here\n\n\nfor name, fn in list(globals().items()):\n    if name.startswith(\"test_\"):\n        fn()\n        print(\"passed:\", name)\n",
        "tests": RUNNER + '''
def test_pass_on_good_code():
    "Your tests pass, without calling the internet"
    results = run_functions()
    check(len(results) >= 2, "Write at least 2 test_ functions. Found %d." % len(results))
    bad = [(n, e) for n, e in results if e is not None]
    if bad and "internet" in str(bad[0][1]):
        check(False, "%s called the real fetch_rate. Wrap the call in: with patch.object(exchange, \\"fetch_rate\\", return_value=...):" % bad[0][0])
    check(not bad, "%s fails on the correct code: %r" % (bad[0][0], bad[0][1]) if bad else "")

def caught(mutant):
    return any(e is not None for _, e in with_swapped("price_in_usd", mutant, run_functions))

def test_catches_bugs():
    "Your tests catch broken versions"
    ex = ns["exchange"]
    check(caught(lambda sar: round(sar / ex.fetch_rate(), 2)), "A version that divides by the rate passed your tests. Check price_in_usd(100) == 26.66.")
    check(caught(lambda sar: sar * ex.fetch_rate()), "A version that doesn't round passed. Check the 1.23 case.")
    check(caught(lambda sar: round(sar * 0.2666, 2)), "A version that ignores fetch_rate and uses a fixed rate passed. Use a different rate (0.12345) in your second test.")
''',
        "solution": "from unittest.mock import patch\n\n\nclass exchange:\n    \"\"\"Stands in for a module that calls a real exchange-rate API.\"\"\"\n    @staticmethod\n    def fetch_rate():\n        raise RuntimeError(\"fetch_rate tried to call the internet. Mock it in tests.\")\n\n\ndef price_in_usd(sar):\n    return round(sar * exchange.fetch_rate(), 2)\n\n\ndef test_converts():\n    with patch.object(exchange, \"fetch_rate\", return_value=0.2666):\n        assert price_in_usd(100) == 26.66\n\n\ndef test_rounds():\n    with patch.object(exchange, \"fetch_rate\", return_value=0.12345):\n        assert price_in_usd(10) == 1.23\n\n\nfor name, fn in list(globals().items()):\n    if name.startswith(\"test_\"):\n        fn()\n        print(\"passed:\", name)\n",
        "hints": [
            "`with patch.object(exchange, \"fetch_rate\", return_value=0.2666):` then the assert, indented inside the `with`.",
        ],
    },
]
