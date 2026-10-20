import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Writing a web server",
    "summary": "A server from the standard library: handlers, routing, JSON in and out. Then the same with FastAPI, including validation.",
}

T = 20

HANDLER_HEAD = "from http.server import BaseHTTPRequestHandler\n\n\n"

LESSONS = [
    {
        "id": "server-what",
        "title": "What a server does",
        "kind": "read",
        "body": """
Last chapter you were the client. Now you write the other side.

A web server is a program that:

1. **listens** on a port,
2. waits for a request to arrive,
3. works out what's being asked for (method and path),
4. sends back a response (status, headers, body),
5. goes back to step 2, forever.

Python's standard library has one: `http.server`. You write a **handler** class with a method per HTTP method (`do_GET`, `do_POST` ...), and the server calls it for each request:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)                          # status line
        self.send_header("Content-Type", "text/plain")   # headers
        self.end_headers()                               # the blank line
        self.wfile.write(b"Hello from the server")       # body, as bytes

HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
```

Run that file and open `http://127.0.0.1:8000` in a browser to see it.

## How the exercises work

A server runs forever, which would never finish inside an exercise. So the lessons give you `try_server(Handler, method, path)`, which starts your handler on a spare port, sends it one request, prints the response, and stops it. Use it at the bottom of your code to test with **Run**.
""",
    },
    {
        "id": "first-handler",
        "title": "Your first handler",
        "kind": "code",
        "timeout": T,
        "prelude": S.SERVER_TOOLS,
        "body": """
Inside a handler, four calls make up every response, always in this order:

```python
self.send_response(200)                          # 1. status
self.send_header("Content-Type", "text/plain")   # 2. headers (as many as you like)
self.end_headers()                               # 3. end of headers
self.wfile.write(b"some text")                   # 4. the body, as bytes
```

`b"..."` is a **bytes** literal. For text you've built yourself, use `"...".encode()` to turn it into bytes.

> **Common slip:** writing the body before `end_headers()`, or forgetting `end_headers()` altogether. The client then waits for a response that never properly arrives.

## Your task

Finish `Handler` so every GET gets a `200` with `Content-Type: text/plain` and the body `Site API is running`.
""",
        "starter": HANDLER_HEAD + "class Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        # 1. status 200\n        # 2. Content-Type header\n        # 3. end the headers\n        # 4. write the body (as bytes)\n        pass\n\n\ntry_server(Handler, \"GET\", \"/\")\n",
        "tests": '''
def test_response():
    "200, text/plain, the right body"
    status, headers, body = request_server(need("Handler"), "GET", "/")
    check(status == 200, "The status was %r, expected 200." % status)
    check((headers.get("Content-Type") or "").startswith("text/plain"), "Send the header Content-Type: text/plain.")
    check(body == "Site API is running", "The body was %r." % body)
''',
        "solution": HANDLER_HEAD + "class Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        self.send_response(200)\n        self.send_header(\"Content-Type\", \"text/plain\")\n        self.end_headers()\n        self.wfile.write(b\"Site API is running\")\n\n\ntry_server(Handler, \"GET\", \"/\")\n",
        "hints": [
            "Each numbered comment is one line from the example above it.",
        ],
    },
    {
        "id": "routing",
        "title": "Routing",
        "kind": "code",
        "timeout": T,
        "prelude": S.SERVER_TOOLS,
        "body": """
`self.path` holds the path the client asked for (including any `?query`). Choosing what to do based on it is called **routing**:

```python
def do_GET(self):
    if self.path == "/health":
        self.reply(200, "ok")
    elif self.path == "/version":
        self.reply(200, "1.0")
    else:
        self.reply(404, "not found")

def reply(self, status, text):
    self.send_response(status)
    self.send_header("Content-Type", "text/plain")
    self.end_headers()
    self.wfile.write(text.encode())
```

Putting the four response calls into one helper method, `reply`, keeps each route to a single line. Every route needs an answer, including the "anything else" case: a 404.

## Your task

Route these GETs:

| Path | Status | Body |
|---|---|---|
| `/health` | 200 | `ok` |
| `/version` | 200 | `1.0` |
| anything else | 404 | `not found` |
""",
        "starter": HANDLER_HEAD + "class Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        pass\n\n    def reply(self, status, text):\n        self.send_response(status)\n        self.send_header(\"Content-Type\", \"text/plain\")\n        self.end_headers()\n        self.wfile.write(text.encode())\n\n\ntry_server(Handler, \"GET\", \"/health\")\ntry_server(Handler, \"GET\", \"/nope\")\n",
        "tests": '''
def test_routes():
    "Each path gets the right answer"
    H = need("Handler")
    for path, want in [("/health", (200, "ok")), ("/version", (200, "1.0")), ("/nope", (404, "not found")), ("/", (404, "not found"))]:
        status, _, body = request_server(H, "GET", path)
        check((status, body) == want, "GET %s gave %r, expected %r." % (path, (status, body), want))
''',
        "solution": HANDLER_HEAD + "class Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        if self.path == \"/health\":\n            self.reply(200, \"ok\")\n        elif self.path == \"/version\":\n            self.reply(200, \"1.0\")\n        else:\n            self.reply(404, \"not found\")\n\n    def reply(self, status, text):\n        self.send_response(status)\n        self.send_header(\"Content-Type\", \"text/plain\")\n        self.end_headers()\n        self.wfile.write(text.encode())\n\n\ntry_server(Handler, \"GET\", \"/health\")\ntry_server(Handler, \"GET\", \"/nope\")\n",
        "hints": [
            "An `if` / `elif` / `else` on `self.path`, each branch calling `self.reply(...)`.",
        ],
    },
    {
        "id": "json-responses",
        "title": "JSON responses",
        "kind": "code",
        "timeout": T,
        "prelude": S.SERVER_TOOLS,
        "body": """
An API answers in JSON. Same four calls, with `json.dumps` for the body and the JSON content type:

```python
def send_json(self, status, data):
    body = json.dumps(data).encode()
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
```

For paths with an id in them, like `/materials/cement`, check how the path starts and take the last part:

```python
if self.path.startswith("/materials/"):
    name = self.path.split("/")[-1]       # 'cement'
```

## Your task

Using the `MATERIALS` dict in the starter, handle:

| Path | Response |
|---|---|
| `/materials` | 200, a JSON **list** of all the material names, sorted |
| `/materials/<name>` | 200, that material's dict as JSON, or 404 with `{"error": "not found"}` |
| anything else | 404 with `{"error": "not found"}` |
""",
        "starter": "import json\n" + HANDLER_HEAD + "MATERIALS = {\n    \"cement\": {\"unit\": \"bag\", \"unit_price\": 18.5},\n    \"sand\": {\"unit\": \"t\", \"unit_price\": 45.0},\n    \"rebar\": {\"unit\": \"t\", \"unit_price\": 2950.0},\n}\n\n\nclass Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        pass\n\n    def send_json(self, status, data):\n        body = json.dumps(data).encode()\n        self.send_response(status)\n        self.send_header(\"Content-Type\", \"application/json\")\n        self.send_header(\"Content-Length\", str(len(body)))\n        self.end_headers()\n        self.wfile.write(body)\n\n\ntry_server(Handler, \"GET\", \"/materials\")\ntry_server(Handler, \"GET\", \"/materials/sand\")\n",
        "tests": '''
import json

def get(path):
    status, headers, body = request_server(need("Handler"), "GET", path)
    check((headers.get("Content-Type") or "").startswith("application/json"), "GET %s should send Content-Type: application/json." % path)
    return status, json.loads(body)

def test_list():
    "/materials lists the names"
    check(get("/materials") == (200, ["cement", "rebar", "sand"]), "GET /materials gave %r." % (get("/materials"),))

def test_one():
    "/materials/<name> gives one, or a 404"
    check(get("/materials/sand") == (200, {"unit": "t", "unit_price": 45.0}), "GET /materials/sand gave %r." % (get("/materials/sand"),))
    check(get("/materials/glass") == (404, {"error": "not found"}), "GET /materials/glass gave %r." % (get("/materials/glass"),))
    check(get("/other") == (404, {"error": "not found"}), "GET /other gave %r." % (get("/other"),))
''',
        "solution": "import json\n" + HANDLER_HEAD + "MATERIALS = {\n    \"cement\": {\"unit\": \"bag\", \"unit_price\": 18.5},\n    \"sand\": {\"unit\": \"t\", \"unit_price\": 45.0},\n    \"rebar\": {\"unit\": \"t\", \"unit_price\": 2950.0},\n}\n\n\nclass Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        if self.path == \"/materials\":\n            self.send_json(200, sorted(MATERIALS))\n        elif self.path.startswith(\"/materials/\"):\n            name = self.path.split(\"/\")[-1]\n            if name in MATERIALS:\n                self.send_json(200, MATERIALS[name])\n            else:\n                self.send_json(404, {\"error\": \"not found\"})\n        else:\n            self.send_json(404, {\"error\": \"not found\"})\n\n    def send_json(self, status, data):\n        body = json.dumps(data).encode()\n        self.send_response(status)\n        self.send_header(\"Content-Type\", \"application/json\")\n        self.send_header(\"Content-Length\", str(len(body)))\n        self.end_headers()\n        self.wfile.write(body)\n\n\ntry_server(Handler, \"GET\", \"/materials\")\ntry_server(Handler, \"GET\", \"/materials/sand\")\n",
        "hints": [
            "`sorted(MATERIALS)` gives the sorted keys of the dict as a list.",
            "For one material: `name = self.path.split(\"/\")[-1]`, then `if name in MATERIALS:`.",
        ],
    },
    {
        "id": "post-body",
        "title": "Reading a request body",
        "kind": "code",
        "timeout": T,
        "prelude": S.SERVER_TOOLS,
        "body": """
For a POST, the client's data is in the body. The `Content-Length` header says how many bytes to read:

```python
def do_POST(self):
    length = int(self.headers.get("Content-Length", 0))
    raw = self.rfile.read(length)
    try:
        data = json.loads(raw)
    except ValueError:
        return self.send_json(400, {"error": "body must be JSON"})
```

Never trust what arrives. Check it has what you need **before** using it, and reply 400 (or 422) with a clear message when it doesn't.

## Your task

Handle `POST /deliveries`. The body should be JSON with `site` (text) and `qty` (a number above 0).

- Valid: add it to the `DELIVERIES` list with an `id` (one more than the list's current length) and reply **201** with the stored delivery.
- Not JSON: **400** with `{"error": "body must be JSON"}`.
- JSON but missing a field, or `qty` not above 0: **400** with `{"error": "site and a positive qty are required"}`.
""",
        "starter": "import json\n" + HANDLER_HEAD + "DELIVERIES = []\n\n\nclass Handler(BaseHTTPRequestHandler):\n    def do_POST(self):\n        if self.path != \"/deliveries\":\n            return self.send_json(404, {\"error\": \"not found\"})\n        # 1. read and parse the body (400 if it isn't JSON)\n        # 2. check site and qty (400 if wrong)\n        # 3. store it with an id, reply 201\n\n    def send_json(self, status, data):\n        body = json.dumps(data).encode()\n        self.send_response(status)\n        self.send_header(\"Content-Type\", \"application/json\")\n        self.send_header(\"Content-Length\", str(len(body)))\n        self.end_headers()\n        self.wfile.write(body)\n\n\ntry_server(Handler, \"POST\", \"/deliveries\", {\"site\": \"RYD-N\", \"qty\": 12})\ntry_server(Handler, \"POST\", \"/deliveries\", {\"site\": \"RYD-N\"})\n",
        "tests": '''
import json

def post(body):
    status, _, text = request_server(need("Handler"), "POST", "/deliveries", body)
    return status, json.loads(text)

def test_valid():
    "A good delivery is stored and returned with 201"
    D = need("DELIVERIES")
    D.clear()
    st, data = post({"site": "JED-1", "qty": 30})
    check(st == 201, "A valid POST should get 201, got %r." % st)
    check(data == {"site": "JED-1", "qty": 30, "id": 1}, "The response was %r, expected the delivery with id 1." % (data,))
    check(len(D) == 1, "Store the delivery in DELIVERIES.")
    st, data = post({"site": "RYD-S", "qty": 2.5})
    check(data.get("id") == 2, "The second delivery should get id 2.")

def test_not_json():
    "400 for a body that isn't JSON"
    st, data = post(b"site=RYD-N")
    check(st == 400 and data == {"error": "body must be JSON"}, "Non-JSON body gave %r." % ((st, data),))

def test_invalid():
    "400 for missing or bad fields"
    for body in ({"site": "RYD-N"}, {"qty": 5}, {"site": "RYD-N", "qty": 0}, {"site": "RYD-N", "qty": -3}):
        st, data = post(body)
        check(st == 400 and data == {"error": "site and a positive qty are required"}, "%r gave %r." % (body, (st, data)))
''',
        "solution": "import json\n" + HANDLER_HEAD + "DELIVERIES = []\n\n\nclass Handler(BaseHTTPRequestHandler):\n    def do_POST(self):\n        if self.path != \"/deliveries\":\n            return self.send_json(404, {\"error\": \"not found\"})\n        length = int(self.headers.get(\"Content-Length\", 0))\n        try:\n            data = json.loads(self.rfile.read(length))\n        except ValueError:\n            return self.send_json(400, {\"error\": \"body must be JSON\"})\n        ok = isinstance(data, dict) and \"site\" in data and isinstance(data.get(\"qty\"), (int, float)) and data[\"qty\"] > 0\n        if not ok:\n            return self.send_json(400, {\"error\": \"site and a positive qty are required\"})\n        delivery = {\"site\": data[\"site\"], \"qty\": data[\"qty\"], \"id\": len(DELIVERIES) + 1}\n        DELIVERIES.append(delivery)\n        self.send_json(201, delivery)\n\n    def send_json(self, status, data):\n        body = json.dumps(data).encode()\n        self.send_response(status)\n        self.send_header(\"Content-Type\", \"application/json\")\n        self.send_header(\"Content-Length\", str(len(body)))\n        self.end_headers()\n        self.wfile.write(body)\n\n\ntry_server(Handler, \"POST\", \"/deliveries\", {\"site\": \"RYD-N\", \"qty\": 12})\ntry_server(Handler, \"POST\", \"/deliveries\", {\"site\": \"RYD-N\"})\n",
        "hints": [
            "Step 1 is the example's `try` / `except ValueError`. `return self.send_json(...)` sends and stops in one line.",
            "Step 2: `\"site\" in data` and `isinstance(data.get(\"qty\"), (int, float)) and data[\"qty\"] > 0`.",
            "Step 3: `delivery = {\"site\": ..., \"qty\": ..., \"id\": len(DELIVERIES) + 1}`, append it, `self.send_json(201, delivery)`.",
        ],
    },
    {
        "id": "stdlib-quiz",
        "title": "Why not stop here?",
        "kind": "quiz",
        "body": "You've now built a working JSON API with nothing but the standard library.",
        "question": "Why do real projects use a framework like FastAPI instead of `http.server`?",
        "options": [
            "http.server can't send JSON",
            "Frameworks handle routing, validation, error responses, docs and concurrency for you, so your code is only the parts that are actually yours",
            "http.server only works on Windows",
            "Frameworks don't need Python",
        ],
        "answer": 1,
        "explain": "Look at how much of the last lesson was plumbing: reading lengths, parsing, checking types, building error replies. A framework does all of that, plus security details you'd otherwise have to know about. The Python docs themselves warn that `http.server` isn't meant for production.",
    },
    {
        "id": "fastapi-install",
        "title": "Installing FastAPI",
        "kind": "read",
        "widget": "packages:backend",
        "body": """
**FastAPI** is a popular Python framework for building APIs. You write ordinary functions; FastAPI handles the HTTP.

It needs a few packages:

| Package | For |
|---|---|
| **fastapi** | the framework |
| **uvicorn** | the server that runs a FastAPI app |
| **httpx** | used by FastAPI's TestClient, which the exercises (and your own tests) use |
| **requests** | the friendly HTTP client from the last chapter |

Use the panel below to install them with one click (it skips anything you already have), or from a terminal: `python -m pip install fastapi uvicorn httpx requests`.

## Running a FastAPI app for real

Save your app as `main.py` with `app = FastAPI()` in it, then:

```
uvicorn main:app --reload
```

`main:app` means "the variable `app` in the file `main.py`". `--reload` restarts the server whenever you save a change. Open `http://127.0.0.1:8000/docs` and you'll find interactive documentation FastAPI wrote for you.

In the exercises, `call(app, "GET", "/path")` sends one request straight to your app and prints the response, with no server to start or stop.
""",
    },
    {
        "id": "fastapi-first",
        "title": "Your first FastAPI app",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

That's a whole API. The line starting with `@` is a **decorator**: it registers the function below it as the handler for `GET /health`. Whatever the function returns (a dict, a list, a number) is sent back as JSON with status 200. All the plumbing from the last five lessons happens for you.

## Your task

Make an app with two routes:

- `GET /health` returns `{"status": "ok"}`
- `GET /version` returns `{"version": "1.0"}`
""",
        "starter": "from fastapi import FastAPI\n\napp = FastAPI()\n\n# your routes here\n\n\ncall(app, \"GET\", \"/health\")\ncall(app, \"GET\", \"/version\")\n",
        "tests": '''
from fastapi.testclient import TestClient

def test_routes():
    "Both routes answer"
    c = TestClient(need("app"))
    r = c.get("/health")
    check(r.status_code == 200 and r.json() == {"status": "ok"}, "GET /health gave %s %s." % (r.status_code, r.text))
    r = c.get("/version")
    check(r.status_code == 200 and r.json() == {"version": "1.0"}, "GET /version gave %s %s." % (r.status_code, r.text))
''',
        "solution": "from fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}\n\n\n@app.get(\"/version\")\ndef version():\n    return {\"version\": \"1.0\"}\n\n\ncall(app, \"GET\", \"/health\")\ncall(app, \"GET\", \"/version\")\n",
        "hints": [
            "Copy the `health` example, then a second decorator and function for `/version`.",
            "Each route needs its own function name.",
        ],
    },
    {
        "id": "fastapi-params",
        "title": "Path and query parameters",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
Curly brackets in the path capture part of the URL, and FastAPI passes it to your function as a parameter of the same name. Any **other** parameter becomes a query parameter:

```python
from fastapi import FastAPI, HTTPException

@app.get("/materials/{name}")
def get_material(name: str):
    if name not in MATERIALS:
        raise HTTPException(status_code=404, detail="material not found")
    return MATERIALS[name]

@app.get("/materials")
def list_materials(max_price: float = 1e9):        # ?max_price=100
    return [n for n, m in MATERIALS.items() if m["unit_price"] <= max_price]
```

- The type hints (`: str`, `: float`) matter: FastAPI converts the text from the URL to that type, and replies 422 automatically if it can't.
- A default value makes a query parameter optional.
- `raise HTTPException(...)` stops and sends that error status, with `{"detail": ...}` as the body.

## Your task

Using `MATERIALS` from the starter:

- `GET /materials/{name}` returns that material's dict, or 404 with detail `material not found`
- `GET /materials` returns a sorted list of names, optionally filtered by a `category` query parameter (no filter when it isn't given)
""",
        "starter": "from fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n\nMATERIALS = {\n    \"cement\": {\"category\": \"binder\", \"unit_price\": 18.5},\n    \"sand\": {\"category\": \"aggregate\", \"unit_price\": 45.0},\n    \"gravel\": {\"category\": \"aggregate\", \"unit_price\": 52.0},\n    \"rebar\": {\"category\": \"steel\", \"unit_price\": 2950.0},\n}\n\n# your two routes here\n\n\ncall(app, \"GET\", \"/materials?category=aggregate\")\ncall(app, \"GET\", \"/materials/glass\")\n",
        "tests": '''
from fastapi.testclient import TestClient

def test_one():
    "/materials/{name}"
    c = TestClient(need("app"))
    r = c.get("/materials/rebar")
    check(r.status_code == 200 and r.json() == {"category": "steel", "unit_price": 2950.0}, "GET /materials/rebar gave %s %s." % (r.status_code, r.text))
    r = c.get("/materials/glass")
    check(r.status_code == 404 and r.json() == {"detail": "material not found"}, "GET /materials/glass gave %s %s." % (r.status_code, r.text))

def test_list():
    "/materials with and without a category"
    c = TestClient(need("app"))
    r = c.get("/materials")
    check(r.json() == ["cement", "gravel", "rebar", "sand"], "GET /materials gave %s." % r.text)
    r = c.get("/materials", params={"category": "aggregate"})
    check(r.json() == ["gravel", "sand"], "GET /materials?category=aggregate gave %s." % r.text)
''',
        "solution": "from fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n\nMATERIALS = {\n    \"cement\": {\"category\": \"binder\", \"unit_price\": 18.5},\n    \"sand\": {\"category\": \"aggregate\", \"unit_price\": 45.0},\n    \"gravel\": {\"category\": \"aggregate\", \"unit_price\": 52.0},\n    \"rebar\": {\"category\": \"steel\", \"unit_price\": 2950.0},\n}\n\n\n@app.get(\"/materials/{name}\")\ndef get_material(name: str):\n    if name not in MATERIALS:\n        raise HTTPException(status_code=404, detail=\"material not found\")\n    return MATERIALS[name]\n\n\n@app.get(\"/materials\")\ndef list_materials(category: str = None):\n    return sorted(n for n, m in MATERIALS.items() if category is None or m[\"category\"] == category)\n\n\ncall(app, \"GET\", \"/materials?category=aggregate\")\ncall(app, \"GET\", \"/materials/glass\")\n",
        "hints": [
            "The first route is the example's `get_material`, as it is.",
            "For the list: `def list_materials(category: str = None):` and keep names where `category is None or m[\"category\"] == category`. `sorted(...)` the result.",
        ],
    },
    {
        "id": "fastapi-validation",
        "title": "Validating input with models",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
Remember all that checking in the `post-body` lesson? In FastAPI you describe the shape of the data once, as a **model**, and the checking happens for you:

```python
from pydantic import BaseModel, Field

class DeliveryIn(BaseModel):
    site: str
    material: str
    qty: float = Field(gt=0)        # must be greater than 0

@app.post("/deliveries", status_code=201)
def create_delivery(d: DeliveryIn):
    record = {"id": len(DELIVERIES) + 1, **d.model_dump()}
    DELIVERIES.append(record)
    return record
```

- A parameter whose type is a model is read from the JSON **body**.
- A missing field, a wrong type, or `qty` of 0 gets an automatic **422** response, explaining exactly what's wrong. Your function never even runs.
- `status_code=201` on the decorator sets the success status.
- `d.model_dump()` turns the model back into a plain dict. (Older pydantic versions call it `d.dict()`.)

## Your task

Add `POST /deliveries` to the app. Accept `site` (text), `material` (text) and `qty` (a number **greater than 0**), store each delivery in `DELIVERIES` with an `id`, and reply **201** with the stored record.
""",
        "starter": "from fastapi import FastAPI\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\nDELIVERIES = []\n\n\n# class DeliveryIn(BaseModel): ...\n\n# @app.post(...)\n\n\ncall(app, \"POST\", \"/deliveries\", json={\"site\": \"RYD-N\", \"material\": \"sand\", \"qty\": 12})\ncall(app, \"POST\", \"/deliveries\", json={\"site\": \"RYD-N\", \"material\": \"sand\", \"qty\": 0})\n",
        "tests": '''
from fastapi.testclient import TestClient

def test_valid():
    "201 with the stored delivery"
    need("DELIVERIES").clear()
    c = TestClient(need("app"))
    r = c.post("/deliveries", json={"site": "JED-1", "material": "cement", "qty": 30})
    check(r.status_code == 201, "A valid POST gave %s %s. Set status_code=201." % (r.status_code, r.text))
    body = r.json()
    check(body.get("site") == "JED-1" and body.get("material") == "cement" and body.get("qty") == 30 and body.get("id") == 1,
          "The response was %s." % r.text)

def test_invalid():
    "422 for bad input"
    c = TestClient(need("app"))
    for bad in ({"site": "JED-1", "material": "cement"}, {"site": "JED-1", "material": "cement", "qty": 0},
                {"site": "JED-1", "material": "cement", "qty": "lots"}, {"material": "cement", "qty": 3}):
        r = c.post("/deliveries", json=bad)
        check(r.status_code == 422, "%r gave %s, expected 422. Is qty a Field(gt=0) on a model?" % (bad, r.status_code))
''',
        "solution": "from fastapi import FastAPI\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\nDELIVERIES = []\n\n\nclass DeliveryIn(BaseModel):\n    site: str\n    material: str\n    qty: float = Field(gt=0)\n\n\n@app.post(\"/deliveries\", status_code=201)\ndef create_delivery(d: DeliveryIn):\n    record = {\"id\": len(DELIVERIES) + 1, **d.model_dump()}\n    DELIVERIES.append(record)\n    return record\n\n\ncall(app, \"POST\", \"/deliveries\", json={\"site\": \"RYD-N\", \"material\": \"sand\", \"qty\": 12})\ncall(app, \"POST\", \"/deliveries\", json={\"site\": \"RYD-N\", \"material\": \"sand\", \"qty\": 0})\n",
        "hints": [
            "The example is the whole answer. Type it out rather than pasting: it's worth knowing by heart.",
            "If `model_dump` gives an AttributeError, your pydantic is older: use `d.dict()`.",
        ],
    },
    {
        "id": "server-task",
        "title": "Chapter task: a task list API",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
A complete little API, using every piece of this chapter.

## Your task

Build an app with an in-memory `TASKS` dict (id to task):

| Route | Does |
|---|---|
| `POST /tasks` | body `{"title": ...}` (title must be at least 1 character: `Field(min_length=1)`). Store `{"id": n, "title": ..., "done": False}` with ids 1, 2, 3 ... Reply **201** with it. |
| `GET /tasks` | a list of all tasks, in id order |
| `GET /tasks/{task_id}` | one task, or **404** |
| `POST /tasks/{task_id}/done` | mark it done and return it, or **404** |

`task_id` is a number: declare it as `task_id: int`.
""",
        "starter": "from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\nTASKS = {}\n\n\n# model and routes here\n\n\ncall(app, \"POST\", \"/tasks\", json={\"title\": \"Order rebar\"})\ncall(app, \"GET\", \"/tasks\")\n",
        "tests": '''
from fastapi.testclient import TestClient

def fresh():
    need("TASKS").clear()
    return TestClient(need("app"))

def test_create_list():
    "Create and list tasks"
    c = fresh()
    r = c.post("/tasks", json={"title": "Order rebar"})
    check(r.status_code == 201 and r.json() == {"id": 1, "title": "Order rebar", "done": False}, "POST /tasks gave %s %s." % (r.status_code, r.text))
    c.post("/tasks", json={"title": "Book crane"})
    r = c.get("/tasks")
    check([t["title"] for t in r.json()] == ["Order rebar", "Book crane"], "GET /tasks gave %s." % r.text)
    r = c.post("/tasks", json={"title": ""})
    check(r.status_code == 422, "An empty title should be rejected with 422.")

def test_one_and_done():
    "Get one, mark done, and 404s"
    c = fresh()
    c.post("/tasks", json={"title": "Pour slab"})
    r = c.get("/tasks/1")
    check(r.status_code == 200 and r.json()["title"] == "Pour slab", "GET /tasks/1 gave %s %s." % (r.status_code, r.text))
    r = c.post("/tasks/1/done")
    check(r.status_code == 200 and r.json()["done"] is True, "POST /tasks/1/done gave %s %s." % (r.status_code, r.text))
    check(c.get("/tasks/1").json()["done"] is True, "The task should stay done.")
    check(c.get("/tasks/99").status_code == 404, "GET /tasks/99 should be 404.")
    check(c.post("/tasks/99/done").status_code == 404, "POST /tasks/99/done should be 404.")
''',
        "solution": "from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\nTASKS = {}\n\n\nclass TaskIn(BaseModel):\n    title: str = Field(min_length=1)\n\n\n@app.post(\"/tasks\", status_code=201)\ndef create_task(t: TaskIn):\n    task = {\"id\": len(TASKS) + 1, \"title\": t.title, \"done\": False}\n    TASKS[task[\"id\"]] = task\n    return task\n\n\n@app.get(\"/tasks\")\ndef list_tasks():\n    return [TASKS[k] for k in sorted(TASKS)]\n\n\n@app.get(\"/tasks/{task_id}\")\ndef get_task(task_id: int):\n    if task_id not in TASKS:\n        raise HTTPException(status_code=404, detail=\"task not found\")\n    return TASKS[task_id]\n\n\n@app.post(\"/tasks/{task_id}/done\")\ndef complete_task(task_id: int):\n    task = get_task(task_id)\n    task[\"done\"] = True\n    return task\n\n\ncall(app, \"POST\", \"/tasks\", json={\"title\": \"Order rebar\"})\ncall(app, \"GET\", \"/tasks\")\n",
        "hints": [
            "The model is one line: `title: str = Field(min_length=1)`. Creating is the `fastapi-validation` lesson again.",
            "Get-one is the `fastapi-params` lesson. The done route can call `get_task(task_id)` to reuse its 404.",
        ],
    },
]
