"""
Pieces shared by the back-end chapters (not a chapter itself: content.py only
loads files named chNN_*.py).

TEXT_HELPERS  test helpers for "text" lessons, where the learner types
              commands or file contents and the checks read them.
MOCK_API      a lesson prelude that starts a small local web API in the
              background and sets BASE_URL, so HTTP lessons work offline.
SERVER_TOOLS  a lesson prelude with try_server(), which runs a learner's
              http.server handler for one request and shows the response.
FASTAPI_TOOLS a lesson prelude with call(), which sends one request to a
              learner's FastAPI app through TestClient and shows the response.
"""

TEXT_HELPERS = r'''
def cmd_lines():
    """Non-blank, non-comment lines, with spaces tidied and any prompt like
    '$ ' or 'PS C:\\> ' removed."""
    import re
    out = []
    for line in RAW_CODE.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^(\$|PS [^>]*>|>)\s*", "", line)
        out.append(" ".join(line.split()))
    return out

def same(a, b):
    """Commands equal, ignoring repeated spaces and the type of quotes."""
    norm = lambda s: " ".join(s.replace("'", '"').split())
    return norm(a) == norm(b)

def find(options, lines=None, start=0):
    """Index of the first line (from start) matching any of the options, or -1."""
    lines = cmd_lines() if lines is None else lines
    for i in range(start, len(lines)):
        if any(same(lines[i], o) for o in options):
            return i
    return -1

def in_order(steps, what="the commands"):
    """steps: list of (label, [accepted forms]). Each must appear after the last."""
    lines = cmd_lines()
    pos = 0
    for label, options in steps:
        i = find(options, lines, pos)
        if i == -1:
            if find(options, lines, 0) != -1:
                check(False, "%s is there, but in the wrong order." % label)
            check(False, "I couldn't find %s. Expected something like: %s" % (label, options[0]))
        pos = i + 1
'''

MOCK_API = r'''
import json as _json, threading as _threading, time as _time, os as _os
from http.server import BaseHTTPRequestHandler as _BH, ThreadingHTTPServer as _TS
from urllib.parse import urlparse as _up, parse_qs as _pq

_os.environ["NO_PROXY"] = "127.0.0.1,localhost"
_os.environ["no_proxy"] = "127.0.0.1,localhost"

_MATERIALS = [
    {"id": 1, "name": "cement", "category": "binder", "unit_price": 18.5},
    {"id": 2, "name": "sand", "category": "aggregate", "unit_price": 45.0},
    {"id": 3, "name": "gravel", "category": "aggregate", "unit_price": 52.0},
    {"id": 4, "name": "rebar", "category": "steel", "unit_price": 2950.0},
    {"id": 5, "name": "bricks", "category": "masonry", "unit_price": 640.0},
]
_DELIVERIES = [
    {"id": i + 1, "site": s, "material": m, "qty": q} for i, (s, m, q) in enumerate([
        ("RYD-N", "cement", 40), ("RYD-N", "sand", 12), ("RYD-S", "cement", 25), ("RYD-N", "rebar", 3.5),
        ("JED-1", "cement", 30), ("RYD-N", "gravel", 18), ("RYD-S", "bricks", 6), ("RYD-S", "sand", 20),
        ("JED-1", "rebar", 2), ("RYD-N", "cement", 35), ("JED-1", "sand", 15), ("RYD-S", "rebar", 5)])
]
RECEIVED = []   # bodies posted to the server, for the checks

class _Mock(_BH):
    def log_message(self, *a):
        pass
    def _send(self, code, data):
        body = _json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        u = _up(self.path); q = {k: v[0] for k, v in _pq(u.query).items()}
        if u.path == "/status":
            return self._send(200, {"ok": True, "service": "site-api"})
        if u.path == "/materials":
            items = [m for m in _MATERIALS if "category" not in q or m["category"] == q["category"]]
            return self._send(200, items)
        if u.path.startswith("/materials/"):
            try:
                mid = int(u.path.rsplit("/", 1)[1])
            except ValueError:
                return self._send(400, {"error": "id must be a number"})
            if mid == 13:   # unlucky: used by the checks to test 500 handling
                return self._send(500, {"error": "database unavailable"})
            for m in _MATERIALS:
                if m["id"] == mid:
                    return self._send(200, m)
            return self._send(404, {"error": "not found"})
        if u.path == "/deliveries":
            page = int(q.get("page", 1)); size = 5
            items = _DELIVERIES[(page - 1) * size: page * size]
            more = page * size < len(_DELIVERIES)
            return self._send(200, {"page": page, "items": items, "next_page": page + 1 if more else None})
        if u.path == "/slow":
            _time.sleep(2)
            return self._send(200, {"ok": True})
        if u.path == "/broken":
            return self._send(500, {"error": "something went wrong"})
        if u.path == "/whoami":
            key = self.headers.get("X-API-Key")
            if key != "demo-key-123":
                return self._send(401, {"error": "missing or wrong API key"})
            return self._send(200, {"user": "sara", "role": "engineer"})
        return self._send(404, {"error": "not found"})
    def do_POST(self):
        u = _up(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n)
        try:
            data = _json.loads(raw or b"null")
        except ValueError:
            return self._send(400, {"error": "body must be JSON"})
        RECEIVED.append({"path": u.path, "content_type": self.headers.get("Content-Type"), "body": data})
        if u.path == "/deliveries":
            if not isinstance(data, dict) or not {"site", "material", "qty"} <= set(data):
                return self._send(400, {"error": "site, material and qty are required"})
            new = dict(data, id=100 + len(RECEIVED))
            return self._send(201, new)
        return self._send(404, {"error": "not found"})

_srv = _TS(("127.0.0.1", 0), _Mock)
_threading.Thread(target=_srv.serve_forever, daemon=True).start()
BASE_URL = "http://127.0.0.1:%d" % _srv.server_address[1]
'''

SERVER_TOOLS = r'''
import threading as _threading, os as _os, json as _json
from http.server import ThreadingHTTPServer as _TS
import urllib.request as _ur, urllib.error as _ue

_os.environ["NO_PROXY"] = "127.0.0.1,localhost"
_os.environ["no_proxy"] = "127.0.0.1,localhost"

def request_server(handler_cls, method="GET", path="/", body=None, headers=None):
    """Start handler_cls on a free port, send one request, stop it.
    Returns (status, headers dict, body text)."""
    srv = _TS(("127.0.0.1", 0), handler_cls)
    t = _threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        url = "http://127.0.0.1:%d%s" % (srv.server_address[1], path)
        data = None
        hdrs = dict(headers or {})
        if body is not None:
            data = body if isinstance(body, bytes) else _json.dumps(body).encode()
            hdrs.setdefault("Content-Type", "application/json")
        req = _ur.Request(url, data=data, method=method, headers=hdrs)
        try:
            with _ur.urlopen(req, timeout=3) as r:
                return r.status, dict(r.headers), r.read().decode()
        except _ue.HTTPError as e:
            return e.code, dict(e.headers), e.read().decode()
    finally:
        srv.shutdown()
        srv.server_close()

def try_server(handler_cls, method="GET", path="/", body=None):
    """Print what your server sends back for one request."""
    status, headers, text = request_server(handler_cls, method, path, body)
    print("%s %s -> %s" % (method, path, status))
    print("Content-Type:", headers.get("Content-Type"))
    print(text)
    print()
'''

FASTAPI_TOOLS = r'''
def call(app, method="GET", path="/", json=None, headers=None):
    """Send one request to a FastAPI app (no real server needed) and print the response."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    r = client.request(method, path, json=json, headers=headers)
    print("%s %s -> %s" % (method, path, r.status_code))
    print(r.text)
    print()
    return r
'''
