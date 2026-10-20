import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "How the web works",
    "summary": "URLs, DNS and ports, what an HTTP request and response look like, methods, status codes, headers and JSON.",
}

LESSONS = [
    {
        "id": "web-overview",
        "title": "From URL to response",
        "kind": "read",
        "body": """
What actually happens when a program fetches `https://api.example.com:443/materials?category=steel`?

## 1. The URL is split up

| Part | Here | Means |
|---|---|---|
| scheme | `https` | which protocol (HTTP, encrypted) |
| host | `api.example.com` | which computer |
| port | `443` | which program on that computer (443 is the default for https, 80 for http) |
| path | `/materials` | which thing on that program |
| query | `category=steel` | extra options, after the `?`, joined with `&` |

## 2. DNS finds the computer

Computers find each other by IP address (like `93.184.216.34`), not by name. **DNS** is the internet's phone book: it turns `api.example.com` into an address.

## 3. A connection to the port

The client connects to that address on the port. A computer can run many network programs at once, and the port says which one you want. That's why your local Keystone runs at `127.0.0.1:8765`: `127.0.0.1` always means "this same computer".

## 4. Request and response

The client sends an **HTTP request**, the server sends back an **HTTP response**. Both are plain text with a fixed layout: a first line, some **headers**, a blank line, then an optional **body**.

```
GET /materials?category=steel HTTP/1.1
Host: api.example.com
Accept: application/json

```

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 61

[{"id": 4, "name": "rebar", "category": "steel"}]
```

Everything in this track, from calling APIs to writing servers, is building or reading messages like these two.
""",
    },
    {
        "id": "url-parts",
        "title": "Taking a URL apart",
        "kind": "code",
        "body": """
Python's `urllib.parse` splits URLs for you:

```python
from urllib.parse import urlparse, parse_qs

u = urlparse("https://api.example.com/materials?category=steel&page=2")
u.scheme     # 'https'
u.hostname   # 'api.example.com'
u.port       # None, because no port was written
u.path       # '/materials'
u.query      # 'category=steel&page=2'
parse_qs(u.query)    # {'category': ['steel'], 'page': ['2']}
```

`parse_qs` gives a **list** for each key, because a query can repeat a key (`?tag=a&tag=b`).

## Your task

Write `url_parts(url)` that returns a dictionary with:

- `scheme`, `host` and `path`
- `port`: the port as an int, or the default (443 for https, 80 for http) if none is written
- `query`: a dict of the query values, with **single** values instead of lists (take the first of each)
""",
        "starter": "from urllib.parse import urlparse, parse_qs\n\n\ndef url_parts(url):\n    u = urlparse(url)\n    pass\n\n\nprint(url_parts(\"https://api.example.com/materials?category=steel&page=2\"))\n",
        "tests": '''
def test_parts():
    "Splits URLs correctly"
    f = need("url_parts")
    cases = [
        ("https://api.example.com/materials?category=steel&page=2",
         {"scheme": "https", "host": "api.example.com", "port": 443, "path": "/materials", "query": {"category": "steel", "page": "2"}}),
        ("http://127.0.0.1:8765/api/lesson?id=py:while",
         {"scheme": "http", "host": "127.0.0.1", "port": 8765, "path": "/api/lesson", "query": {"id": "py:while"}}),
        ("http://site.local/health",
         {"scheme": "http", "host": "site.local", "port": 80, "path": "/health", "query": {}}),
    ]
    for url, want in cases:
        v, _ = capture(f, url)
        check(v == want, "url_parts(%r) returned\\n%r\\nexpected\\n%r" % (url, v, want))
''',
        "solution": "from urllib.parse import urlparse, parse_qs\n\n\ndef url_parts(url):\n    u = urlparse(url)\n    port = u.port or (443 if u.scheme == \"https\" else 80)\n    query = {k: v[0] for k, v in parse_qs(u.query).items()}\n    return {\"scheme\": u.scheme, \"host\": u.hostname, \"port\": port, \"path\": u.path, \"query\": query}\n\n\nprint(url_parts(\"https://api.example.com/materials?category=steel&page=2\"))\n",
        "hints": [
            "`port = u.port or (443 if u.scheme == \"https\" else 80)`",
            "`query = {k: v[0] for k, v in parse_qs(u.query).items()}`",
        ],
    },
    {
        "id": "ports-quiz",
        "title": "Ports",
        "kind": "quiz",
        "body": "One quick check on the overview.",
        "question": "You start a server on your laptop and it says it's listening on `127.0.0.1:8000`. Which URL reaches it from a browser on the same laptop?",
        "options": [
            "`http://8000.127.0.0.1`",
            "`http://127.0.0.1:8000`",
            "`http://localhost/8000`",
            "`https://127.0.0.1`",
        ],
        "answer": 1,
        "explain": "Host, then a colon, then the port: `http://127.0.0.1:8000` (or `http://localhost:8000`, since localhost means the same computer). Without the port, the browser would try 80, where nothing is listening.",
    },
    {
        "id": "raw-request",
        "title": "Writing a request by hand",
        "kind": "code",
        "lang": "text",
        "body": """
Writing one HTTP request by hand makes everything later make sense. The layout:

```
METHOD /path?query HTTP/1.1
Header-Name: value
Header-Name: value

body (if any)
```

The first line is the **request line**. `Host` is the one header every request must have.

## Your task

Write the request a client would send to **get** the materials in the `aggregate` category from `api.siteco.com`, asking for JSON back. That's three lines:

1. the request line, for path `/materials` with the query `category=aggregate`
2. a `Host` header
3. an `Accept` header of `application/json`
""",
        "starter": "",
        "tests": '''
def test_request():
    "Request line, Host and Accept"
    lines = [l.strip() for l in RAW_CODE.strip().splitlines()]
    check(lines, "Write the three lines of the request.")
    check(lines[0] == "GET /materials?category=aggregate HTTP/1.1",
          "The first line should be: GET /materials?category=aggregate HTTP/1.1  (yours is %r)" % lines[0])
    headers = {}
    for l in lines[1:]:
        if ":" in l:
            k, v = l.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    check(headers.get("host") == "api.siteco.com", "Add the header  Host: api.siteco.com")
    check(headers.get("accept") == "application/json", "Add the header  Accept: application/json")
''',
        "solution": "GET /materials?category=aggregate HTTP/1.1\nHost: api.siteco.com\nAccept: application/json\n",
        "hints": [
            "The host goes in the Host header, not in the request line. The request line only has the path and query.",
        ],
    },
    {
        "id": "methods-status",
        "title": "Methods and status codes",
        "kind": "read",
        "body": """
## Methods: what the client wants to do

| Method | Means | Has a body? |
|---|---|---|
| `GET` | read something | no |
| `POST` | create something new | yes |
| `PUT` | replace something | yes |
| `PATCH` | change part of something | yes |
| `DELETE` | remove something | no |

`GET` must never change anything on the server. Browsers, caches and crawlers send `GET`s freely and assume they're harmless.

## Status codes: how it went

The first digit is the family:

| Range | Family | Common ones |
|---|---|---|
| 1xx | informational | rarely seen |
| 2xx | success | **200** OK, **201** Created, **204** No Content |
| 3xx | redirect | **301** Moved Permanently, **304** Not Modified |
| 4xx | client error: the request was wrong | **400** Bad Request, **401** Unauthorized, **403** Forbidden, **404** Not Found, **422** Unprocessable |
| 5xx | server error: the server failed | **500** Internal Server Error, **503** Service Unavailable |

The 4xx/5xx split matters: 4xx says "fix your request", 5xx says "not your fault, try later".
""",
    },
    {
        "id": "status-family",
        "title": "Status code families",
        "kind": "code",
        "body": """
Client code often only cares about the family. Integer division gets the first digit: `404 // 100` is `4`.

## Your task

Write `status_family(code)` that returns:

| Code | Returns |
|---|---|
| 100 to 199 | `"informational"` |
| 200 to 299 | `"success"` |
| 300 to 399 | `"redirect"` |
| 400 to 499 | `"client error"` |
| 500 to 599 | `"server error"` |

Anything else should raise a `ValueError`.
""",
        "starter": "def status_family(code):\n    pass\n\n\nprint(status_family(404))   # client error\n",
        "tests": '''
def test_families():
    "Right family for each code"
    f = need("status_family")
    for code, want in [(100, "informational"), (200, "success"), (201, "success"), (204, "success"), (301, "redirect"),
                       (400, "client error"), (404, "client error"), (422, "client error"), (500, "server error"), (503, "server error")]:
        v, _ = capture(f, code)
        check(v == want, "status_family(%d) returned %r, expected %r." % (code, v, want))

def test_bad():
    "Rejects nonsense codes"
    for code in (99, 600, 0):
        try:
            need("status_family")(code)
        except ValueError:
            continue
        check(False, "status_family(%d) should raise ValueError." % code)
''',
        "solution": "FAMILIES = {1: \"informational\", 2: \"success\", 3: \"redirect\", 4: \"client error\", 5: \"server error\"}\n\n\ndef status_family(code):\n    first = code // 100\n    if first not in FAMILIES:\n        raise ValueError(f\"{code} isn't an HTTP status code\")\n    return FAMILIES[first]\n\n\nprint(status_family(404))\n",
        "hints": [
            "`first = code // 100`, then look it up in a dict, or use an if/elif chain.",
            "Raise `ValueError` when `first` isn't 1 to 5.",
        ],
    },
    {
        "id": "status-quiz",
        "title": "Picking the right code",
        "kind": "quiz",
        "body": "Use the table from two lessons back.",
        "question": "A client POSTs a new delivery and the server saves it. Which status should the response have?",
        "options": ["200 OK", "201 Created", "204 No Content", "302 Found"],
        "answer": 1,
        "explain": "201 Created says a new thing now exists. The response body usually holds the new item, including the id the server gave it. 200 would work but tells the client less; 204 means there's no body at all.",
    },
    {
        "id": "headers",
        "title": "Headers",
        "kind": "read",
        "body": """
Headers are `Name: value` lines that carry information **about** the message. Names don't care about case. A handful do most of the work:

| Header | Sent by | Says |
|---|---|---|
| `Host` | client | which site (one server can host many) |
| `Accept` | client | which formats it wants back, e.g. `application/json` |
| `Content-Type` | both | what format the body is in |
| `Content-Length` | both | how many bytes the body is |
| `Authorization` | client | who's asking, e.g. `Bearer <token>` |
| `User-Agent` | client | which program is asking |
| `Cache-Control` | server | whether and how long the response may be cached |
| `Location` | server | where something is (redirects, and the URL of a newly created item) |

APIs often add their own, conventionally starting with `X-`, like `X-API-Key` or `X-Request-Id`.

> `Content-Type` is the one that bites. Send JSON without `Content-Type: application/json` and many servers won't parse it, and you'll get a 400 or 415 back.
""",
    },
    {
        "id": "json",
        "title": "JSON",
        "kind": "code",
        "body": """
Most APIs send and receive **JSON**: text that looks almost exactly like Python dicts and lists.

```python
import json

text = '{"site": "RYD-N", "qty": 40, "urgent": true, "notes": null}'
data = json.loads(text)        # text -> Python: {'site': 'RYD-N', 'qty': 40, 'urgent': True, 'notes': None}
back = json.dumps(data)        # Python -> text
pretty = json.dumps(data, indent=2, sort_keys=True)
```

The differences from Python are small but strict: JSON uses `true`, `false` and `null`, and strings **must** use double quotes.

## Your task

Write `total_by_site(text)`. It receives JSON text holding a list of deliveries like `{"site": "RYD-N", "qty": 40}`. Return **JSON text** of an object mapping each site to its total quantity, with the keys sorted.

So `'[{"site": "B", "qty": 1}, {"site": "A", "qty": 2}, {"site": "B", "qty": 3}]'` gives `'{"A": 2, "B": 4}'`.
""",
        "starter": "import json\n\n\ndef total_by_site(text):\n    # 1. json.loads the text\n    # 2. add up qty per site in a dict\n    # 3. return json.dumps(..., sort_keys=True)\n    pass\n\n\nprint(total_by_site('[{\"site\": \"B\", \"qty\": 1}, {\"site\": \"A\", \"qty\": 2}, {\"site\": \"B\", \"qty\": 3}]'))\n",
        "tests": '''
import json

def test_totals():
    "Returns sorted JSON totals"
    f = need("total_by_site")
    v, _ = capture(f, '[{"site": "B", "qty": 1}, {"site": "A", "qty": 2}, {"site": "B", "qty": 3}]')
    check(isinstance(v, str), "Return JSON text (a string), using json.dumps. You returned a %s." % type(v).__name__)
    check(v == '{"A": 2, "B": 4}', "Got %r, expected '{\\"A\\": 2, \\"B\\": 4}'." % (v,))
    v, _ = capture(f, "[]")
    check(v == "{}", "An empty list should give '{}'.")
''',
        "solution": "import json\n\n\ndef total_by_site(text):\n    deliveries = json.loads(text)\n    totals = {}\n    for d in deliveries:\n        totals[d[\"site\"]] = totals.get(d[\"site\"], 0) + d[\"qty\"]\n    return json.dumps(totals, sort_keys=True)\n\n\nprint(total_by_site('[{\"site\": \"B\", \"qty\": 1}, {\"site\": \"A\", \"qty\": 2}, {\"site\": \"B\", \"qty\": 3}]'))\n",
        "hints": [
            "The middle step is the counting pattern from the dictionaries chapter: `totals[site] = totals.get(site, 0) + qty`.",
            "`return json.dumps(totals, sort_keys=True)`",
        ],
    },
    {
        "id": "json-quiz",
        "title": "JSON or not?",
        "kind": "quiz",
        "body": "Spot the invalid one.",
        "question": "Which of these is **not** valid JSON?",
        "options": [
            '`{"ok": true, "count": 3}`',
            '`[1, 2.5, null]`',
            "`{'ok': True}`",
            '`"just a string"`',
        ],
        "answer": 2,
        "explain": "That's Python, not JSON: JSON needs double quotes around strings and keys, and lowercase `true`. `json.loads(\"{'ok': True}\")` raises an error. The others are all valid JSON, including a bare string.",
    },
]
