import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Designing an API",
    "summary": "Resources and verbs, status codes that mean something, versioning, and documentation.",
}

T = 20

LESSONS = [
    {
        "id": "rest",
        "title": "Resources and verbs",
        "kind": "read",
        "body": """
An API is a promise to other programmers, so the design matters as much as the code. The most common style is **REST**: URLs name **things** (resources), and the HTTP method says what to **do** to them.

## URLs are nouns

| URL | Means |
|---|---|
| `/sites` | the collection of all sites |
| `/sites/RYD-N` | one site |
| `/sites/RYD-N/deliveries` | the deliveries belonging to that site |
| `/deliveries/12` | one delivery |

Use plural nouns, lowercase, with hyphens for multi-word names (`/tool-loans`). Not `/getSites` or `/deleteDelivery?id=12`: the verb belongs in the method.

## Methods are verbs

| Method + URL | Does | Usual success status |
|---|---|---|
| `GET /deliveries` | list them | 200 |
| `GET /deliveries/12` | get one | 200 |
| `POST /deliveries` | create a new one | 201 |
| `PUT /deliveries/12` | replace it entirely | 200 |
| `PATCH /deliveries/12` | change some fields | 200 |
| `DELETE /deliveries/12` | remove it | 204 |

## Filtering, sorting and paging go in the query

`GET /deliveries?site=RYD-N&sort=-date&page=2`. They narrow down **which** items of the collection you get, so they aren't part of the resource's name.

Get these conventions right and people can guess how your API works before reading the docs.
""",
    },
    {
        "id": "rest-quiz",
        "title": "Which request?",
        "kind": "quiz",
        "body": "Apply the tables.",
        "question": "A client wants to remove delivery 12. Which request fits REST conventions?",
        "options": [
            "`GET /deliveries/12/delete`",
            "`POST /deleteDelivery?id=12`",
            "`DELETE /deliveries/12`",
            "`PUT /deliveries?remove=12`",
        ],
        "answer": 2,
        "explain": "The URL names the thing, and the method says what to do with it. A GET that deletes is dangerous, since browsers and crawlers send GETs freely, assuming they change nothing.",
    },
    {
        "id": "design-routes",
        "title": "Designing the routes",
        "kind": "code",
        "lang": "text",
        "body": """
Before writing any code, list the routes. It's quick to change a list, slow to change an API people already use.

## Your task

Design the routes for a site deliveries API. Write one route per line as `METHOD /path`, using `{code}` or `{id}` for the parts that change:

1. list all sites
2. get one site (sites are identified by their `code`)
3. list the deliveries for one site
4. record a new delivery for one site
5. change some fields of a delivery (deliveries have an `id`)
6. remove a delivery
""",
        "starter": "# one route per line, like:  GET /things/{id}\n",
        "tests": S.TEXT_HELPERS + '''
def routes():
    out = []
    for l in cmd_lines():
        parts = l.split()
        if len(parts) == 2:
            m, p = parts
            out.append((m.upper(), p.rstrip("/").lower()))
    return out

def test_routes():
    "All six routes"
    got = routes()
    want = [
        ("list all sites", [("GET", "/sites")]),
        ("get one site", [("GET", "/sites/{code}")]),
        ("list a site's deliveries", [("GET", "/sites/{code}/deliveries")]),
        ("record a delivery for a site", [("POST", "/sites/{code}/deliveries")]),
        ("change some fields of a delivery", [("PATCH", "/deliveries/{id}"), ("PATCH", "/sites/{code}/deliveries/{id}")]),
        ("remove a delivery", [("DELETE", "/deliveries/{id}"), ("DELETE", "/sites/{code}/deliveries/{id}")]),
    ]
    for label, options in want:
        check(any(o in got for o in options), "I couldn't find a route to %s. Expected something like: %s %s" % (label, options[0][0], options[0][1]))
''',
        "solution": "GET /sites\nGET /sites/{code}\nGET /sites/{code}/deliveries\nPOST /sites/{code}/deliveries\nPATCH /deliveries/{id}\nDELETE /deliveries/{id}\n",
        "hints": [
            "A site's deliveries live under the site: `/sites/{code}/deliveries`.",
            "\"Change some fields\" is PATCH, not PUT.",
        ],
    },
    {
        "id": "status-codes",
        "title": "Status codes that make sense",
        "kind": "read",
        "body": """
A good status code lets a client react correctly without reading the message. The ones worth using deliberately:

| Code | When |
|---|---|
| **200 OK** | a successful read or update, with a body |
| **201 Created** | a POST created something; return it (with its new id) |
| **204 No Content** | success with nothing to say, typical for DELETE |
| **400 Bad Request** | the request is malformed (unreadable JSON, nonsense values) |
| **401 Unauthorized** | not logged in, or the key or token is missing or wrong |
| **403 Forbidden** | logged in, but not allowed to do this |
| **404 Not Found** | no such resource |
| **409 Conflict** | the request clashes with the current state, e.g. a duplicate code |
| **422 Unprocessable Entity** | well-formed but invalid (FastAPI uses this for validation errors) |
| **500 Internal Server Error** | a bug on the server; never send this on purpose |

## Error bodies

Make every error body look the same, so clients can handle them in one place. FastAPI's `{"detail": "..."}` is a perfectly good standard. Say what was wrong in words a person can act on: `"site code 'XYZ' does not exist"` beats `"invalid input"`.

## 401 versus 403

401 means "I don't know who you are". 403 means "I know who you are, and the answer is no". Mixing them up confuses every client that tries to handle them.
""",
    },
    {
        "id": "crud",
        "title": "A full set of operations",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
Time to put the status codes to work. Two FastAPI details you'll need:

```python
from fastapi import Response

@app.delete("/sites/{code}", status_code=204)
def delete_site(code: str):
    ...
    return Response(status_code=204)      # no body at all

raise HTTPException(status_code=409, detail="site code already exists")
```

## Your task

Build `/sites` on an in-memory `SITES` dict (code to site), with these rules:

| Request | Success | Errors |
|---|---|---|
| `GET /sites` | 200, list of sites sorted by code | |
| `POST /sites` with `{"code", "name", "city"}` | **201** with the site | **409** if the code already exists |
| `GET /sites/{code}` | 200 | **404** |
| `PATCH /sites/{code}` with any of `name` or `city` | 200 with the updated site | **404** |
| `DELETE /sites/{code}` | **204**, no body | **404** |

For PATCH, the starter has a model where both fields are optional (`Optional[str] = None`). Only change the fields that were actually sent: `changes.model_dump(exclude_unset=True)` gives just those.
""",
        "starter": "from typing import Optional\n\nfrom fastapi import FastAPI, HTTPException, Response\nfrom pydantic import BaseModel\n\napp = FastAPI()\nSITES = {}\n\n\nclass SiteIn(BaseModel):\n    code: str\n    name: str\n    city: str\n\n\nclass SitePatch(BaseModel):\n    name: Optional[str] = None\n    city: Optional[str] = None\n\n\n# your five routes here\n\n\ncall(app, \"POST\", \"/sites\", json={\"code\": \"RYD-N\", \"name\": \"North Plaza\", \"city\": \"Riyadh\"})\ncall(app, \"POST\", \"/sites\", json={\"code\": \"RYD-N\", \"name\": \"Copy\", \"city\": \"Riyadh\"})\n",
        "tests": '''
from fastapi.testclient import TestClient

def fresh():
    need("SITES").clear()
    return TestClient(need("app"))

N = {"code": "RYD-N", "name": "North Plaza", "city": "Riyadh"}

def test_create():
    "POST gives 201, then 409 for a duplicate"
    c = fresh()
    r = c.post("/sites", json=N)
    check(r.status_code == 201 and r.json() == N, "POST /sites gave %s %s." % (r.status_code, r.text))
    r = c.post("/sites", json=dict(N, name="Copy"))
    check(r.status_code == 409, "A duplicate code gave %s, expected 409." % r.status_code)

def test_read():
    "GET list and one"
    c = fresh()
    c.post("/sites", json=N); c.post("/sites", json={"code": "JED-1", "name": "Harbour Hall", "city": "Jeddah"})
    check([s["code"] for s in c.get("/sites").json()] == ["JED-1", "RYD-N"], "GET /sites should be sorted by code.")
    check(c.get("/sites/RYD-N").json() == N, "GET /sites/RYD-N gave %s." % c.get("/sites/RYD-N").text)
    check(c.get("/sites/XYZ").status_code == 404, "GET /sites/XYZ should be 404.")

def test_patch():
    "PATCH changes only what's sent"
    c = fresh()
    c.post("/sites", json=N)
    r = c.patch("/sites/RYD-N", json={"city": "Diriyah"})
    check(r.status_code == 200 and r.json() == dict(N, city="Diriyah"), "PATCH gave %s %s. Only the city should change." % (r.status_code, r.text))
    check(c.patch("/sites/XYZ", json={"city": "x"}).status_code == 404, "PATCH on a missing site should be 404.")

def test_delete():
    "DELETE gives 204, then 404"
    c = fresh()
    c.post("/sites", json=N)
    r = c.delete("/sites/RYD-N")
    check(r.status_code == 204 and r.content == b"", "DELETE gave %s with body %r. Expected 204 and no body." % (r.status_code, r.content))
    check(c.get("/sites/RYD-N").status_code == 404, "The site should be gone after DELETE.")
    check(c.delete("/sites/RYD-N").status_code == 404, "Deleting it again should be 404.")
''',
        "solution": "from typing import Optional\n\nfrom fastapi import FastAPI, HTTPException, Response\nfrom pydantic import BaseModel\n\napp = FastAPI()\nSITES = {}\n\n\nclass SiteIn(BaseModel):\n    code: str\n    name: str\n    city: str\n\n\nclass SitePatch(BaseModel):\n    name: Optional[str] = None\n    city: Optional[str] = None\n\n\ndef find(code):\n    if code not in SITES:\n        raise HTTPException(status_code=404, detail=f\"site {code} not found\")\n    return SITES[code]\n\n\n@app.get(\"/sites\")\ndef list_sites():\n    return [SITES[c] for c in sorted(SITES)]\n\n\n@app.post(\"/sites\", status_code=201)\ndef create_site(s: SiteIn):\n    if s.code in SITES:\n        raise HTTPException(status_code=409, detail=f\"site {s.code} already exists\")\n    SITES[s.code] = s.model_dump()\n    return SITES[s.code]\n\n\n@app.get(\"/sites/{code}\")\ndef get_site(code: str):\n    return find(code)\n\n\n@app.patch(\"/sites/{code}\")\ndef update_site(code: str, changes: SitePatch):\n    site = find(code)\n    site.update(changes.model_dump(exclude_unset=True))\n    return site\n\n\n@app.delete(\"/sites/{code}\", status_code=204)\ndef delete_site(code: str):\n    find(code)\n    del SITES[code]\n    return Response(status_code=204)\n\n\ncall(app, \"POST\", \"/sites\", json={\"code\": \"RYD-N\", \"name\": \"North Plaza\", \"city\": \"Riyadh\"})\ncall(app, \"POST\", \"/sites\", json={\"code\": \"RYD-N\", \"name\": \"Copy\", \"city\": \"Riyadh\"})\n",
        "hints": [
            "A small helper `find(code)` that returns the site or raises the 404 saves repeating yourself in three routes.",
            "PATCH: `site.update(changes.model_dump(exclude_unset=True))`. DELETE: `del SITES[code]` then `return Response(status_code=204)`.",
        ],
    },
    {
        "id": "versioning",
        "title": "Versioning",
        "kind": "quiz",
        "body": """
Once other programs depend on your API, changing it can break them. So the rule is:

- **Adding** is safe: a new endpoint, a new optional field, a new field in a response.
- **Changing or removing** breaks clients: renaming a field, changing its type, making an optional field required, removing an endpoint.

When a breaking change is unavoidable, publish a new **version** alongside the old one, most often in the path: `/v1/deliveries` and `/v2/deliveries`. Old clients keep using v1 until they've moved over, then v1 is retired with plenty of warning.

Put `/v1/` in from day one. It costs nothing, and you'll be glad of it later.
""",
        "question": "Which change can you make to `/v1/deliveries` without a new version?",
        "options": [
            "Renaming the `qty` field to `quantity`",
            "Adding a new optional `notes` field to responses",
            "Making `supplier` a required field when creating",
            "Changing `qty` from a number to text",
        ],
        "answer": 1,
        "explain": "Clients ignore fields they don't know about, so adding `notes` breaks nobody. The other three would make existing clients send or read data that no longer matches.",
    },
    {
        "id": "docs",
        "title": "Documenting the API",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
FastAPI builds an **OpenAPI** description of your API from your code: every route, parameter and model. That's what powers the interactive page at `/docs`. You make it better by adding a few words:

```python
app = FastAPI(title="Site API", version="1.0")

@app.get("/sites", summary="List all sites", tags=["sites"])
def list_sites():
    \"\"\"Returns every site, sorted by code.\"\"\"
    ...
```

- `summary` is the one-line title shown for the route.
- `tags` group routes into sections.
- The function's **docstring** becomes the longer description.

`app.openapi()` returns the whole description as a dict, which is handy for checking it.

## Your task

Give the app the title `Site API` and version `1.0`. Then document `GET /sites`: summary `List all sites`, tag `sites`, and a docstring.
""",
        "starter": "from fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get(\"/sites\")\ndef list_sites():\n    return [{\"code\": \"RYD-N\"}, {\"code\": \"JED-1\"}]\n\n\nprint(app.openapi()[\"info\"])\nprint(app.openapi()[\"paths\"][\"/sites\"][\"get\"].get(\"summary\"))\n",
        "tests": '''
def test_docs():
    "Title, version, summary, tag and description"
    spec = need("app").openapi()
    check(spec["info"]["title"] == "Site API" and spec["info"]["version"] == "1.0", "Set FastAPI(title=\\"Site API\\", version=\\"1.0\\"). Info is %r." % spec["info"])
    op = spec["paths"]["/sites"]["get"]
    check(op.get("summary") == "List all sites", "Set summary=\\"List all sites\\" on the route.")
    check(op.get("tags") == ["sites"], "Set tags=[\\"sites\\"] on the route.")
    check((op.get("description") or "").strip(), "Add a docstring to list_sites: it becomes the description.")
''',
        "solution": "from fastapi import FastAPI\n\napp = FastAPI(title=\"Site API\", version=\"1.0\")\n\n\n@app.get(\"/sites\", summary=\"List all sites\", tags=[\"sites\"])\ndef list_sites():\n    \"\"\"Returns every site, sorted by code.\"\"\"\n    return [{\"code\": \"RYD-N\"}, {\"code\": \"JED-1\"}]\n\n\nprint(app.openapi()[\"info\"])\nprint(app.openapi()[\"paths\"][\"/sites\"][\"get\"].get(\"summary\"))\n",
        "hints": [
            "`app = FastAPI(title=\"Site API\", version=\"1.0\")`",
            "`@app.get(\"/sites\", summary=\"List all sites\", tags=[\"sites\"])`, and a triple-quoted string as the first line of the function.",
        ],
    },
]
