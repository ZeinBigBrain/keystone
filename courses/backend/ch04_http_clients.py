import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "HTTP clients",
    "summary": "Calling an API from Python: GET, query parameters, sending JSON, errors and timeouts, and pagination.",
}

T = 15

INTRO = """
> **About this chapter's practice API.** Each run starts a small API on your own computer, and its address is in the variable `BASE_URL` (something like `http://127.0.0.1:53817`). Nothing goes over the internet. It has these endpoints:
>
> - `GET /status`
> - `GET /materials`, optionally `?category=...`
> - `GET /materials/<id>` (404 if there's no such id)
> - `POST /deliveries` with a JSON body
> - `GET /deliveries?page=N` (5 per page)
> - `GET /slow` (takes 2 seconds), `GET /broken` (always fails with 500)
"""

LESSONS = [
    {
        "id": "get-json",
        "title": "Your first GET",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
Python's standard library can call APIs with `urllib.request`:

```python
import json
import urllib.request

with urllib.request.urlopen(BASE_URL + "/status") as response:
    print(response.status)          # 200
    data = json.load(response)      # read the body and parse the JSON
print(data)                         # {'ok': True, 'service': 'site-api'}
```

`urlopen` sends a GET and gives back the response. `json.load(response)` (no `s`) reads it and turns the JSON into Python in one step.
""" + INTRO + """
## Your task

Write `get_json(url)` that GETs the URL and returns the parsed JSON. Then print `get_json(BASE_URL + "/materials")`.
""",
        "starter": "import json\nimport urllib.request\n\n\ndef get_json(url):\n    pass\n\n\nprint(get_json(BASE_URL + \"/materials\"))\n",
        "tests": '''
def test_get():
    "Returns the parsed JSON"
    f = need("get_json")
    v, _ = capture(f, BASE_URL + "/status")
    check(v == {"ok": True, "service": "site-api"}, "get_json(BASE_URL + '/status') returned %r." % (v,))
    v, _ = capture(f, BASE_URL + "/materials")
    check(isinstance(v, list) and len(v) == 5, "get_json(BASE_URL + '/materials') should return a list of 5 materials.")
''',
        "solution": "import json\nimport urllib.request\n\n\ndef get_json(url):\n    with urllib.request.urlopen(url) as response:\n        return json.load(response)\n\n\nprint(get_json(BASE_URL + \"/materials\"))\n",
        "hints": [
            "Inside the function: `with urllib.request.urlopen(url) as response:` then `return json.load(response)`.",
        ],
    },
    {
        "id": "query-params",
        "title": "Query parameters",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
Don't glue query strings together by hand: spaces, `&` and other characters need **encoding**. `urlencode` does it:

```python
from urllib.parse import urlencode

params = {"category": "aggregate", "sort": "name"}
url = BASE_URL + "/materials?" + urlencode(params)
# .../materials?category=aggregate&sort=name
```

## Your task

Write `material_names(category)` that GETs `/materials` with a `category` query parameter and returns a **list of the names** of the materials that come back.

`material_names("aggregate")` gives `["sand", "gravel"]`.
""",
        "starter": "import json\nimport urllib.request\nfrom urllib.parse import urlencode\n\n\ndef material_names(category):\n    pass\n\n\nprint(material_names(\"aggregate\"))\n",
        "tests": '''
def test_names():
    "Names for each category"
    f = need("material_names")
    for cat, want in [("aggregate", ["sand", "gravel"]), ("steel", ["rebar"]), ("glass", [])]:
        v, _ = capture(f, cat)
        check(v == want, "material_names(%r) returned %r, expected %r." % (cat, v, want))
    check("urlencode" in CODE, "Build the query with urlencode.")
''',
        "solution": "import json\nimport urllib.request\nfrom urllib.parse import urlencode\n\n\ndef material_names(category):\n    url = BASE_URL + \"/materials?\" + urlencode({\"category\": category})\n    with urllib.request.urlopen(url) as response:\n        items = json.load(response)\n    return [m[\"name\"] for m in items]\n\n\nprint(material_names(\"aggregate\"))\n",
        "hints": [
            "`url = BASE_URL + \"/materials?\" + urlencode({\"category\": category})`",
            "Then GET it as before and `return [m[\"name\"] for m in items]`.",
        ],
    },
    {
        "id": "post-json",
        "title": "Sending JSON",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
To send data, build a `Request` with a body (as **bytes**), the right `Content-Type`, and the method:

```python
body = json.dumps({"site": "RYD-N", "material": "sand", "qty": 12}).encode()
req = urllib.request.Request(
    BASE_URL + "/deliveries",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as response:
    print(response.status)       # 201
    created = json.load(response)
```

- `.encode()` turns the JSON text into bytes, which is what goes over the network.
- Forget the `Content-Type` header and many APIs won't know the body is JSON.

## Your task

Write `create_delivery(site, material, qty)` that POSTs those three values as JSON to `/deliveries` and returns the **id** the server gave the new delivery.
""",
        "starter": "import json\nimport urllib.request\n\n\ndef create_delivery(site, material, qty):\n    pass\n\n\nprint(create_delivery(\"RYD-N\", \"sand\", 12))\n",
        "tests": '''
def test_post():
    "Posts JSON and returns the new id"
    f = need("create_delivery")
    before = len(RECEIVED)
    v, _ = capture(f, "JED-1", "cement", 30)
    check(len(RECEIVED) > before, "The server didn't receive a POST.")
    got = RECEIVED[-1]
    check(got["body"] == {"site": "JED-1", "material": "cement", "qty": 30}, "The server received %r." % (got["body"],))
    check(got["content_type"] == "application/json", "Send the header Content-Type: application/json.")
    check(isinstance(v, int) and v >= 100, "Return the new delivery's id (from the response). You returned %r." % (v,))
''',
        "solution": "import json\nimport urllib.request\n\n\ndef create_delivery(site, material, qty):\n    body = json.dumps({\"site\": site, \"material\": material, \"qty\": qty}).encode()\n    req = urllib.request.Request(\n        BASE_URL + \"/deliveries\",\n        data=body,\n        headers={\"Content-Type\": \"application/json\"},\n        method=\"POST\",\n    )\n    with urllib.request.urlopen(req) as response:\n        return json.load(response)[\"id\"]\n\n\nprint(create_delivery(\"RYD-N\", \"sand\", 12))\n",
        "hints": [
            "Copy the example, using the function's parameters in the dict.",
            "The response is the new delivery as JSON, so `return json.load(response)[\"id\"]`.",
        ],
    },
    {
        "id": "errors",
        "title": "When it goes wrong",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
`urlopen` raises an exception for any 4xx or 5xx response:

```python
import urllib.error

try:
    with urllib.request.urlopen(BASE_URL + "/materials/99") as r:
        data = json.load(r)
except urllib.error.HTTPError as e:
    print(e.code)            # 404
    print(json.load(e))      # the error body: {'error': 'not found'}
```

There's a second kind, `urllib.error.URLError`, for when the server can't be reached at all (no network, wrong host). `HTTPError` is a kind of `URLError`, so catch `HTTPError` **first** if you want to tell them apart.

What to do with an error depends on its meaning. A 404 for "get material 99" is a normal answer ("there isn't one"). A 500 isn't, and hiding it would hide a real problem.

## Your task

Write `get_material(material_id)` that returns the material as a dict, returns `None` if the server says **404**, and lets any other error raise as normal.
""",
        "starter": "import json\nimport urllib.request\nimport urllib.error\n\n\ndef get_material(material_id):\n    pass\n\n\nprint(get_material(4))\nprint(get_material(99))   # should print None\n",
        "tests": '''
import urllib.error

def test_found():
    "Returns a material that exists"
    v, _ = capture(need("get_material"), 2)
    check(isinstance(v, dict) and v.get("name") == "sand", "get_material(2) returned %r." % (v,))

def test_missing():
    "None for a 404"
    v, _ = capture(need("get_material"), 99)
    check(v is None, "get_material(99) returned %r, expected None." % (v,))

def test_other_errors():
    "Other errors are not hidden"
    try:
        v = need("get_material")(13)     # the practice API fails this one with a 500
    except urllib.error.HTTPError as e:
        check(e.code == 500, "Expected the 500 error to come through, got %r." % e.code)
        return
    check(False, "A 500 error was swallowed (you returned %r). Only catch 404, and re-raise the rest with raise." % (v,))
''',
        "solution": "import json\nimport urllib.request\nimport urllib.error\n\n\ndef get_material(material_id):\n    try:\n        with urllib.request.urlopen(f\"{BASE_URL}/materials/{material_id}\") as r:\n            return json.load(r)\n    except urllib.error.HTTPError as e:\n        if e.code == 404:\n            return None\n        raise\n\n\nprint(get_material(4))\nprint(get_material(99))\n",
        "hints": [
            "Wrap the GET in `try:` and add `except urllib.error.HTTPError as e:`.",
            "In the except: `if e.code == 404: return None`, then a bare `raise` re-raises anything else.",
        ],
    },
    {
        "id": "timeouts",
        "title": "Timeouts",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
By default `urlopen` will wait a very long time for a server that's hung. In a real app, one slow service can then freeze everything that calls it. Always pass a `timeout` in seconds:

```python
import socket

try:
    with urllib.request.urlopen(BASE_URL + "/slow", timeout=0.5) as r:
        data = json.load(r)
except (socket.timeout, urllib.error.URLError) as e:
    print("gave up:", e)
```

A timeout shows up as `socket.timeout` (called `TimeoutError` in newer Pythons) or a `URLError` wrapping it, depending on when it happens, so catch both.

## Your task

Write `fetch_or_none(path, seconds)` that GETs `BASE_URL + path` with that timeout and returns the parsed JSON, or `None` if it times out.

`/slow` takes 2 seconds to answer, so `fetch_or_none("/slow", 0.5)` gives `None`.
""",
        "starter": "import json\nimport socket\nimport urllib.request\nimport urllib.error\n\n\ndef fetch_or_none(path, seconds):\n    pass\n\n\nprint(fetch_or_none(\"/status\", 2))\nprint(fetch_or_none(\"/slow\", 0.5))   # should print None\n",
        "tests": '''
def test_fast():
    "Fast responses come back"
    v, _ = capture(need("fetch_or_none"), "/status", 2)
    check(v == {"ok": True, "service": "site-api"}, "fetch_or_none('/status', 2) returned %r." % (v,))

def test_slow():
    "Slow responses give None"
    import time
    t0 = time.time()
    v, _ = capture(need("fetch_or_none"), "/slow", 0.5)
    check(v is None, "fetch_or_none('/slow', 0.5) returned %r, expected None." % (v,))
    check(time.time() - t0 < 1.8, "It waited for the whole slow response. Pass timeout=seconds to urlopen.")
''',
        "solution": "import json\nimport socket\nimport urllib.request\nimport urllib.error\n\n\ndef fetch_or_none(path, seconds):\n    try:\n        with urllib.request.urlopen(BASE_URL + path, timeout=seconds) as r:\n            return json.load(r)\n    except (socket.timeout, urllib.error.URLError):\n        return None\n\n\nprint(fetch_or_none(\"/status\", 2))\nprint(fetch_or_none(\"/slow\", 0.5))\n",
        "hints": [
            "`urllib.request.urlopen(BASE_URL + path, timeout=seconds)`",
            "`except (socket.timeout, urllib.error.URLError): return None`",
        ],
    },
    {
        "id": "pagination",
        "title": "Pagination",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
APIs rarely send thousands of rows at once. They send a **page**, plus a way to get the next one. This practice API's `/deliveries?page=1` returns:

```json
{"page": 1, "items": [... 5 deliveries ...], "next_page": 2}
```

and on the last page, `next_page` is `null` (`None` in Python).

So: keep fetching while there's a next page. It's the `while` loop from the Python course:

```python
page = 1
while page is not None:
    data = get_json(f"{BASE_URL}/deliveries?page={page}")
    ... use data["items"] ...
    page = data["next_page"]
```

## Your task

Write `all_deliveries()` that fetches **every** page and returns one list of all the deliveries, in order.
""",
        "starter": "import json\nimport urllib.request\n\n\ndef get_json(url):\n    with urllib.request.urlopen(url, timeout=5) as r:\n        return json.load(r)\n\n\ndef all_deliveries():\n    pass\n\n\nitems = all_deliveries()\nprint(len(items), \"deliveries\")\n",
        "tests": '''
def test_all():
    "Collects every page"
    v, _ = capture(need("all_deliveries"))
    check(isinstance(v, list), "Return a list.")
    check(len(v) == 12, "Got %d deliveries, expected 12 across 3 pages." % len(v))
    check([d["id"] for d in v] == list(range(1, 13)), "The deliveries should be in order, ids 1 to 12.")
''',
        "solution": "import json\nimport urllib.request\n\n\ndef get_json(url):\n    with urllib.request.urlopen(url, timeout=5) as r:\n        return json.load(r)\n\n\ndef all_deliveries():\n    items = []\n    page = 1\n    while page is not None:\n        data = get_json(f\"{BASE_URL}/deliveries?page={page}\")\n        items.extend(data[\"items\"])\n        page = data[\"next_page\"]\n    return items\n\n\nitems = all_deliveries()\nprint(len(items), \"deliveries\")\n",
        "hints": [
            "Start `items = []` and `page = 1`, then the loop from the example.",
            "`items.extend(data[\"items\"])` adds a whole page at once. Return `items` after the loop.",
        ],
    },
    {
        "id": "requests-lib",
        "title": "The requests library",
        "kind": "quiz",
        "body": """
`urllib` is always available, which is why this chapter uses it. Most real projects use the **requests** package instead, because it's shorter and friendlier (install it from the \"Installing FastAPI\" lesson in a later chapter, or with `python -m pip install requests`):

```python
import requests

r = requests.get(BASE_URL + "/materials", params={"category": "steel"}, timeout=5)
r.status_code          # 200
r.json()               # parsed JSON

r = requests.post(BASE_URL + "/deliveries", json={"site": "RYD-N", "material": "sand", "qty": 12}, timeout=5)
r.raise_for_status()   # raises for 4xx/5xx, if you want an exception
```

`params=` encodes the query for you, and `json=` sets the body and the `Content-Type` header in one go. One difference catches people out: **requests does not raise for 4xx/5xx by itself.** You check `r.status_code` or call `r.raise_for_status()`.
""",
        "question": "`r = requests.get(BASE_URL + \"/materials/99\", timeout=5)` and the server replies 404. What happens?",
        "options": [
            "requests raises an HTTPError straight away",
            "Nothing is raised; `r.status_code` is 404, and `r.raise_for_status()` would raise",
            "It returns None",
            "It retries until it gets a 200",
        ],
        "answer": 1,
        "explain": "Unlike `urlopen`, requests hands you the response whatever the status. Check `r.ok` or `r.status_code`, or call `r.raise_for_status()` when an error status should become an exception.",
    },
    {
        "id": "client-task",
        "title": "Chapter task: a site summary from the API",
        "kind": "code",
        "timeout": T,
        "prelude": S.MOCK_API,
        "body": """
Pull it together: several calls, one useful answer.

## Your task

Write `site_spend()` that:

1. fetches **all** deliveries (every page),
2. fetches the materials list once, to get each material's `unit_price`,
3. returns a dict mapping each site to its total spend (`qty * unit_price`), rounded to 2 places.

Use timeouts on every call.
""",
        "starter": "import json\nimport urllib.request\n\n\ndef get_json(url):\n    with urllib.request.urlopen(url, timeout=5) as r:\n        return json.load(r)\n\n\ndef site_spend():\n    pass\n\n\nprint(site_spend())\n",
        "tests": '''
def test_spend():
    "Spend per site"
    v, _ = capture(need("site_spend"))
    price = {"cement": 18.5, "sand": 45.0, "gravel": 52.0, "rebar": 2950.0, "bricks": 640.0}
    rows = [("RYD-N", "cement", 40), ("RYD-N", "sand", 12), ("RYD-S", "cement", 25), ("RYD-N", "rebar", 3.5),
            ("JED-1", "cement", 30), ("RYD-N", "gravel", 18), ("RYD-S", "bricks", 6), ("RYD-S", "sand", 20),
            ("JED-1", "rebar", 2), ("RYD-N", "cement", 35), ("JED-1", "sand", 15), ("RYD-S", "rebar", 5)]
    want = {}
    for s, m, q in rows:
        want[s] = want.get(s, 0) + q * price[m]
    want = {k: round(v2, 2) for k, v2 in want.items()}
    check(v == want, "site_spend() returned %r\\nexpected %r" % (v, want))
''',
        "solution": "import json\nimport urllib.request\n\n\ndef get_json(url):\n    with urllib.request.urlopen(url, timeout=5) as r:\n        return json.load(r)\n\n\ndef site_spend():\n    deliveries = []\n    page = 1\n    while page is not None:\n        data = get_json(f\"{BASE_URL}/deliveries?page={page}\")\n        deliveries.extend(data[\"items\"])\n        page = data[\"next_page\"]\n\n    price = {m[\"name\"]: m[\"unit_price\"] for m in get_json(BASE_URL + \"/materials\")}\n\n    spend = {}\n    for d in deliveries:\n        spend[d[\"site\"]] = spend.get(d[\"site\"], 0) + d[\"qty\"] * price[d[\"material\"]]\n    return {site: round(total, 2) for site, total in spend.items()}\n\n\nprint(site_spend())\n",
        "hints": [
            "Step 1 is `all_deliveries` from the pagination lesson.",
            "Step 2: `price = {m[\"name\"]: m[\"unit_price\"] for m in get_json(BASE_URL + \"/materials\")}`.",
            "Step 3 is the counting pattern, adding `d[\"qty\"] * price[d[\"material\"]]`.",
        ],
    },
]
