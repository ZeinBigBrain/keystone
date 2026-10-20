import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Authentication",
    "summary": "Storing passwords safely, sessions and tokens, signed tokens (how JWTs work), API keys, and who can do what.",
}

T = 20

LESSONS = [
    {
        "id": "passwords-read",
        "title": "Storing passwords",
        "kind": "read",
        "body": """
**Authentication** is finding out who someone is. **Authorisation** (the end of this chapter) is deciding what they may do.

It starts with passwords, and the first rule is absolute: **never store a password**. Not in plain text, not "encrypted". If the database leaks (and databases do leak), every user's password leaks with it, and people reuse passwords everywhere.

## Store a hash instead

A **hash function** turns any text into a fixed-length fingerprint, and it can't be run backwards. At sign-up you store the hash. At login you hash what they typed and compare.

But a plain fast hash (like SHA-256 on its own) isn't enough:

- **Salt.** Hash the same password twice and you get the same fingerprint, so an attacker can precompute hashes of common passwords once and look them all up. Add a random **salt** per user, stored next to the hash, and every hash is unique.
- **Slow on purpose.** Attackers try billions of guesses per second against a fast hash. Password hashes are designed to be slow: thousands of rounds (PBKDF2), or memory-hungry (bcrypt, scrypt, Argon2). 100 ms per login is nothing to a user, but crippling to someone guessing.

Python's standard library has PBKDF2 built in: `hashlib.pbkdf2_hmac`. In real projects, a library like `argon2-cffi` or `passlib` picks good settings for you.

## Comparing safely

Compare hashes with `hmac.compare_digest(a, b)`, not `==`. `==` stops at the first different character, and with careful timing, an attacker can measure how far it got.
""",
    },
    {
        "id": "hash-password",
        "title": "Hashing a password",
        "kind": "code",
        "timeout": T,
        "body": """
```python
import hashlib, hmac, os

salt = os.urandom(16)                    # 16 random bytes, new for every password
digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)   # 200,000 rounds
stored = salt.hex() + "$" + digest.hex() # keep both, as text
```

To check a login attempt, split the stored text, turn the salt back into bytes (`bytes.fromhex`), hash the attempt with the **same** salt and rounds, and compare.

## Your task

Write two functions:

- `hash_password(password)` returns a string `"<salt hex>$<hash hex>"` using a fresh 16-byte salt and 200,000 rounds of PBKDF2-SHA256
- `verify_password(password, stored)` returns `True` if the password matches the stored string, `False` otherwise, comparing with `hmac.compare_digest`
""",
        "starter": "import hashlib\nimport hmac\nimport os\n\nROUNDS = 200_000\n\n\ndef hash_password(password):\n    pass\n\n\ndef verify_password(password, stored):\n    # split stored on \"$\", rebuild the salt with bytes.fromhex, hash, compare\n    pass\n\n\nstored = hash_password(\"correct horse\")\nprint(stored)\nprint(verify_password(\"correct horse\", stored))   # True\nprint(verify_password(\"wrong\", stored))           # False\n",
        "tests": '''
import hashlib

def test_format():
    "Salt and hash, and a new salt every time"
    h1, _ = capture(need("hash_password"), "pa55word")
    h2, _ = capture(need("hash_password"), "pa55word")
    check(isinstance(h1, str) and h1.count("$") == 1, "hash_password should return 'salt$hash' as text. Got %r." % (h1,))
    salt, digest = h1.split("$")
    check(len(bytes.fromhex(salt)) == 16, "The salt should be 16 bytes (32 hex characters).")
    check(digest == hashlib.pbkdf2_hmac("sha256", b"pa55word", bytes.fromhex(salt), 200000).hex(), "The hash should be PBKDF2-SHA256 with 200,000 rounds.")
    check(h1 != h2, "Hashing the same password twice gave the same result. Use a fresh os.urandom(16) salt each time.")
    check("pa55word" not in h1, "The password itself mustn't appear in the stored text.")

def test_verify():
    "Accepts the right password only"
    stored = need("hash_password")("site-office-2026")
    v, _ = capture(need("verify_password"), "site-office-2026", stored)
    check(v is True, "verify_password with the right password returned %r." % (v,))
    for wrong in ("site-office-2025", "", "SITE-OFFICE-2026"):
        v, _ = capture(need("verify_password"), wrong, stored)
        check(v is False, "verify_password(%r, ...) returned %r, expected False." % (wrong, v))
    check("compare_digest" in CODE, "Compare with hmac.compare_digest.")
''',
        "solution": "import hashlib\nimport hmac\nimport os\n\nROUNDS = 200_000\n\n\ndef hash_password(password):\n    salt = os.urandom(16)\n    digest = hashlib.pbkdf2_hmac(\"sha256\", password.encode(), salt, ROUNDS)\n    return salt.hex() + \"$\" + digest.hex()\n\n\ndef verify_password(password, stored):\n    salt_hex, digest_hex = stored.split(\"$\")\n    digest = hashlib.pbkdf2_hmac(\"sha256\", password.encode(), bytes.fromhex(salt_hex), ROUNDS)\n    return hmac.compare_digest(digest.hex(), digest_hex)\n\n\nstored = hash_password(\"correct horse\")\nprint(stored)\nprint(verify_password(\"correct horse\", stored))\nprint(verify_password(\"wrong\", stored))\n",
        "hints": [
            "`hash_password` is the three lines of the example, then `return stored`.",
            "`salt_hex, digest_hex = stored.split(\"$\")`, hash again with `bytes.fromhex(salt_hex)`, then `return hmac.compare_digest(new.hex(), digest_hex)`.",
        ],
    },
    {
        "id": "salt-quiz",
        "title": "Why salt?",
        "kind": "quiz",
        "body": "Make sure the reason sticks, not just the recipe.",
        "question": "Two users both choose the password `Riyadh2026`. With a salted hash, what's in the database?",
        "options": [
            "The same hash twice, so the password is easy to spot",
            "Two different hashes, because each user has their own random salt",
            "The password in plain text with a salt next to it",
            "Nothing, salted passwords aren't stored",
        ],
        "answer": 1,
        "explain": "Different salts give different hashes, so an attacker can't see that two users share a password, and a precomputed table of common-password hashes is useless. They'd have to attack each hash separately, and slowly.",
    },
    {
        "id": "sessions-tokens",
        "title": "Sessions and tokens",
        "kind": "read",
        "body": """
HTTP forgets everything between requests. After a user logs in once, how does the server know the next request is them? Two common answers.

## Sessions (common for websites)

1. On login, the server creates a random **session id**, stores "session abc123 belongs to user 7" (in memory or a database), and sends the id back in a **cookie**.
2. The browser sends that cookie with every request automatically.
3. The server looks the id up to find the user.

Logging out is easy (delete the session). The cost is a lookup on every request.

## Tokens (common for APIs and mobile apps)

1. On login, the server gives the client a **token**: a string that proves who they are.
2. The client sends it with every request, in a header: `Authorization: Bearer <token>`.
3. The server checks it.

A **signed** token carries the user's details inside it, plus a signature only the server can make. The server checks the signature and trusts the contents, with no lookup at all. That's how **JWTs** (JSON Web Tokens) work, and you'll build a small one next.

The catch with signed tokens: you can't easily take one back before it expires. So they're given short lifetimes (minutes to hours), often paired with a longer-lived "refresh" token.

## Whatever you choose

- Always use **HTTPS**, or anyone on the network can copy the cookie or token.
- Tokens and session ids are as good as a password while they're valid. Never log them, never put them in URLs.
""",
    },
    {
        "id": "signed-token",
        "title": "A signed token",
        "kind": "code",
        "timeout": T,
        "body": """
A signature proves a message came from someone holding a secret key, and hasn't changed. **HMAC** makes one:

```python
import hmac, hashlib, base64, json

SECRET = b"keep-this-out-of-git"

def sign(data: bytes) -> str:
    sig = hmac.new(SECRET, data, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode()
```

A token is then: the payload (as JSON, base64-encoded so it's URL-safe text), a dot, and the signature of that payload:

```
eyJ1c2VyIjogN30=.pJ7v1x...
```

Anyone can **read** the payload (base64 isn't encryption), but nobody without `SECRET` can change it and produce a matching signature.

## Your task

Write:

- `make_token(user_id)` returning `<payload>.<signature>`, where the payload is `{"user": user_id}` as JSON, base64url-encoded
- `read_token(token)` returning the user id if the signature is valid, or `None` if it's been tampered with or isn't a token at all. Compare signatures with `hmac.compare_digest`.
""",
        "starter": "import base64\nimport hashlib\nimport hmac\nimport json\n\nSECRET = b\"keep-this-out-of-git\"\n\n\ndef sign(data):\n    sig = hmac.new(SECRET, data, hashlib.sha256).digest()\n    return base64.urlsafe_b64encode(sig).decode()\n\n\ndef make_token(user_id):\n    pass\n\n\ndef read_token(token):\n    pass\n\n\nt = make_token(7)\nprint(t)\nprint(read_token(t))                   # 7\nprint(read_token(\"x\" + t))             # None\n",
        "tests": '''
import base64, json

def test_round_trip():
    "A token reads back to its user"
    t, _ = capture(need("make_token"), 42)
    check(isinstance(t, str) and t.count(".") == 1, "make_token should return 'payload.signature'. Got %r." % (t,))
    payload = json.loads(base64.urlsafe_b64decode(t.split(".")[0]))
    check(payload == {"user": 42}, "The payload should decode to {'user': 42}, got %r." % (payload,))
    v, _ = capture(need("read_token"), t)
    check(v == 42, "read_token on a fresh token returned %r, expected 42." % (v,))

def test_tampered():
    "Changed or junk tokens give None"
    t = need("make_token")(42)
    p, s = t.split(".")
    forged = base64.urlsafe_b64encode(json.dumps({"user": 1}).encode()).decode() + "." + s
    for bad in (forged, p + "." + s[:-2] + "AA", "nonsense", "", "a.b.c"):
        try:
            v = need("read_token")(bad)
        except Exception as e:
            check(False, "read_token(%r) crashed with %s. Return None for anything that isn't a valid token." % (bad, type(e).__name__))
        check(v is None, "read_token accepted a tampered token %r and returned %r." % (bad, v))
    check("compare_digest" in CODE, "Compare signatures with hmac.compare_digest.")
''',
        "solution": "import base64\nimport hashlib\nimport hmac\nimport json\n\nSECRET = b\"keep-this-out-of-git\"\n\n\ndef sign(data):\n    sig = hmac.new(SECRET, data, hashlib.sha256).digest()\n    return base64.urlsafe_b64encode(sig).decode()\n\n\ndef make_token(user_id):\n    payload = base64.urlsafe_b64encode(json.dumps({\"user\": user_id}).encode()).decode()\n    return payload + \".\" + sign(payload.encode())\n\n\ndef read_token(token):\n    parts = token.split(\".\")\n    if len(parts) != 2:\n        return None\n    payload, sig = parts\n    if not hmac.compare_digest(sign(payload.encode()), sig):\n        return None\n    try:\n        return json.loads(base64.urlsafe_b64decode(payload))[\"user\"]\n    except (ValueError, KeyError, TypeError):\n        return None\n\n\nt = make_token(7)\nprint(t)\nprint(read_token(t))\nprint(read_token(\"x\" + t))\n",
        "hints": [
            "make_token: `payload = base64.urlsafe_b64encode(json.dumps({\"user\": user_id}).encode()).decode()`, then `return payload + \".\" + sign(payload.encode())`.",
            "read_token: split on `.` (return None unless there are exactly 2 parts), check `hmac.compare_digest(sign(payload.encode()), sig)`, then decode the payload.",
        ],
    },
    {
        "id": "jwt-quiz",
        "title": "What's inside a JWT",
        "kind": "quiz",
        "body": """
A real **JWT** has three parts, `header.payload.signature`, but it's the same idea you just built. The header names the algorithm; the payload holds **claims** like the user id (`sub`) and an expiry time (`exp`).

In real code, use a library rather than your own: `PyJWT` (`jwt.encode(payload, key, algorithm="HS256")` and `jwt.decode(token, key, algorithms=["HS256"])`). It checks expiry and the other edge cases for you.
""",
        "question": "A JWT's payload says `{\"sub\": \"7\", \"role\": \"engineer\"}`. Can the user read it?",
        "options": [
            "No, it's encrypted",
            "Yes, it's only base64-encoded. The signature stops them changing it, not reading it",
            "Only with the server's secret key",
            "Only if it has expired",
        ],
        "answer": 1,
        "explain": "Anyone can base64-decode a JWT's payload. Signing protects it from being *changed*, not from being *read*. So never put secrets in one.",
    },
    {
        "id": "api-keys",
        "title": "API keys",
        "kind": "code",
        "timeout": T,
        "body": """
For program-to-program access (a script pulling data overnight, say), the usual tool is an **API key**: a long random string, sent with each request in a header like `X-API-Key`.

```python
import secrets
key = secrets.token_urlsafe(32)    # about 43 random URL-safe characters
```

Use `secrets`, never `random`: `random` is predictable, and `secrets` is built for exactly this.

Treat stored keys like passwords: keep only a **hash** of each one. Since keys are long and random already, a fast hash like SHA-256 is fine here (no salt or slowness needed). Show the key to its owner once, when it's created, and never again.

## Your task

Write:

- `new_key()` returning a fresh key from `secrets.token_urlsafe(32)`
- `key_hash(key)` returning the SHA-256 hex digest of the key
- `is_valid(key, stored_hashes)` returning `True` if the key's hash is in the set `stored_hashes`, checking each with `hmac.compare_digest`
""",
        "starter": "import hashlib\nimport hmac\nimport secrets\n\n\ndef new_key():\n    pass\n\n\ndef key_hash(key):\n    pass\n\n\ndef is_valid(key, stored_hashes):\n    pass\n\n\nk = new_key()\nstored = {key_hash(k)}\nprint(is_valid(k, stored), is_valid(\"guess\", stored))   # True False\n",
        "tests": '''
import hashlib

def test_keys():
    "Long, random, URL-safe"
    a, _ = capture(need("new_key"))
    b, _ = capture(need("new_key"))
    check(isinstance(a, str) and len(a) >= 40 and a != b, "new_key should return a long random string (secrets.token_urlsafe(32)).")
    check("secrets" in CODE, "Use the secrets module, not random.")

def test_hash_and_check():
    "Hash and check"
    k = "abc123"
    h, _ = capture(need("key_hash"), k)
    check(h == hashlib.sha256(b"abc123").hexdigest(), "key_hash should return hashlib.sha256(key.encode()).hexdigest().")
    stored = {hashlib.sha256(b"key-one").hexdigest(), hashlib.sha256(b"key-two").hexdigest()}
    for key, want in [("key-one", True), ("key-two", True), ("key-three", False), ("", False)]:
        v, _ = capture(need("is_valid"), key, stored)
        check(v is want, "is_valid(%r, ...) returned %r, expected %r." % (key, v, want))
    check("compare_digest" in CODE, "Compare with hmac.compare_digest.")
''',
        "solution": "import hashlib\nimport hmac\nimport secrets\n\n\ndef new_key():\n    return secrets.token_urlsafe(32)\n\n\ndef key_hash(key):\n    return hashlib.sha256(key.encode()).hexdigest()\n\n\ndef is_valid(key, stored_hashes):\n    h = key_hash(key)\n    return any(hmac.compare_digest(h, s) for s in stored_hashes)\n\n\nk = new_key()\nstored = {key_hash(k)}\nprint(is_valid(k, stored), is_valid(\"guess\", stored))\n",
        "hints": [
            "`return hashlib.sha256(key.encode()).hexdigest()`",
            "`return any(hmac.compare_digest(h, s) for s in stored_hashes)`",
        ],
    },
    {
        "id": "authorisation",
        "title": "Who can do what",
        "kind": "code",
        "timeout": T,
        "body": """
Once you know **who** someone is, decide **what** they may do. Keep those rules in one place, as a function, rather than scattered through the routes:

```python
def can_view_report(user):
    return user["role"] in ("manager", "admin")
```

A common pattern mixes **roles** (what kind of user) with **ownership** (whose thing it is): anyone can edit their own records, managers can edit anyone's at their site, admins can do anything.

The API returns **403 Forbidden** when the answer is no.

## Your task

Write `can_edit(user, delivery)`. Both are dicts: the user has `id`, `role` and `site`; the delivery has `created_by` (a user id) and `site`. Return `True` when:

- the user is an `admin`, **or**
- the user is a `manager` and the delivery is at their site, **or**
- the user created the delivery

and `False` otherwise.
""",
        "starter": "def can_edit(user, delivery):\n    pass\n\n\nsara = {\"id\": 1, \"role\": \"engineer\", \"site\": \"RYD-N\"}\nprint(can_edit(sara, {\"created_by\": 1, \"site\": \"RYD-N\"}))   # True: hers\nprint(can_edit(sara, {\"created_by\": 2, \"site\": \"RYD-N\"}))   # False\n",
        "tests": '''
def test_rules():
    "Admins, site managers and owners"
    f = need("can_edit")
    admin = {"id": 9, "role": "admin", "site": "JED-1"}
    mgr = {"id": 5, "role": "manager", "site": "RYD-N"}
    eng = {"id": 1, "role": "engineer", "site": "RYD-N"}
    cases = [
        (admin, {"created_by": 1, "site": "RYD-N"}, True),
        (mgr, {"created_by": 1, "site": "RYD-N"}, True),
        (mgr, {"created_by": 1, "site": "RYD-S"}, False),
        (eng, {"created_by": 1, "site": "RYD-S"}, True),
        (eng, {"created_by": 2, "site": "RYD-N"}, False),
        ({"id": 3, "role": "viewer", "site": "RYD-N"}, {"created_by": 1, "site": "RYD-N"}, False),
    ]
    for user, d, want in cases:
        v, _ = capture(f, user, d)
        check(v is want, "can_edit(%s, %s) returned %r, expected %r." % (user, d, v, want))
''',
        "solution": "def can_edit(user, delivery):\n    if user[\"role\"] == \"admin\":\n        return True\n    if user[\"role\"] == \"manager\" and delivery[\"site\"] == user[\"site\"]:\n        return True\n    return delivery[\"created_by\"] == user[\"id\"]\n\n\nsara = {\"id\": 1, \"role\": \"engineer\", \"site\": \"RYD-N\"}\nprint(can_edit(sara, {\"created_by\": 1, \"site\": \"RYD-N\"}))\nprint(can_edit(sara, {\"created_by\": 2, \"site\": \"RYD-N\"}))\n",
        "hints": [
            "The \"returning early\" shape: one `if` per rule that returns True, then a final return.",
            "The last line can be `return delivery[\"created_by\"] == user[\"id\"]`.",
        ],
    },
    {
        "id": "fastapi-auth",
        "title": "Protecting routes in FastAPI",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
FastAPI can run a check before a route, using a **dependency**. Write the check once as a function; any route that lists it with `Depends` gets it:

```python
from fastapi import Depends, Header, HTTPException

def current_user(x_api_key: str = Header(None)):     # reads the X-API-Key header
    user = USERS_BY_KEY.get(x_api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="missing or invalid API key")
    return user

@app.get("/me")
def me(user: dict = Depends(current_user)):
    return user
```

`Header(None)` reads a request header. FastAPI turns the parameter name `x_api_key` into the header name `X-API-Key` for you. If the dependency raises, the route never runs.

## Your task

Using `current_user` as above (it's in the starter), add:

- `GET /me` returning the current user
- `DELETE /deliveries/{delivery_id}` that needs a logged-in user, replies **403** with detail `not allowed` unless the user's `role` is `manager`, and otherwise deletes it from `DELIVERIES` and replies **204** (or **404** if there's no such delivery)
""",
        "starter": "from fastapi import Depends, FastAPI, Header, HTTPException, Response\n\napp = FastAPI()\n\nUSERS_BY_KEY = {\n    \"key-sara\": {\"name\": \"Sara\", \"role\": \"engineer\"},\n    \"key-hana\": {\"name\": \"Hana\", \"role\": \"manager\"},\n}\nDELIVERIES = {1: {\"site\": \"RYD-N\", \"qty\": 40}, 2: {\"site\": \"JED-1\", \"qty\": 30}}\n\n\ndef current_user(x_api_key: str = Header(None)):\n    user = USERS_BY_KEY.get(x_api_key)\n    if user is None:\n        raise HTTPException(status_code=401, detail=\"missing or invalid API key\")\n    return user\n\n\n# GET /me and DELETE /deliveries/{delivery_id} here\n\n\ncall(app, \"GET\", \"/me\", headers={\"X-API-Key\": \"key-sara\"})\ncall(app, \"DELETE\", \"/deliveries/1\", headers={\"X-API-Key\": \"key-sara\"})\n",
        "tests": '''
from fastapi.testclient import TestClient

def test_me():
    "GET /me needs a valid key"
    c = TestClient(need("app"))
    r = c.get("/me", headers={"X-API-Key": "key-hana"})
    check(r.status_code == 200 and r.json() == {"name": "Hana", "role": "manager"}, "GET /me with Hana's key gave %s %s." % (r.status_code, r.text))
    check(c.get("/me").status_code == 401, "GET /me without a key should be 401.")
    check(c.get("/me", headers={"X-API-Key": "nope"}).status_code == 401, "A wrong key should be 401.")

def test_delete():
    "Only managers may delete"
    D = need("DELIVERIES")
    D.clear(); D.update({1: {"site": "RYD-N", "qty": 40}, 2: {"site": "JED-1", "qty": 30}})
    c = TestClient(need("app"))
    check(c.delete("/deliveries/1").status_code == 401, "No key should give 401.")
    r = c.delete("/deliveries/1", headers={"X-API-Key": "key-sara"})
    check(r.status_code == 403 and r.json().get("detail") == "not allowed", "An engineer deleting gave %s %s, expected 403." % (r.status_code, r.text))
    check(1 in D, "The engineer's request mustn't delete anything.")
    r = c.delete("/deliveries/1", headers={"X-API-Key": "key-hana"})
    check(r.status_code == 204 and 1 not in D, "A manager deleting delivery 1 gave %s." % r.status_code)
    check(c.delete("/deliveries/99", headers={"X-API-Key": "key-hana"}).status_code == 404, "A missing delivery should be 404.")
''',
        "solution": "from fastapi import Depends, FastAPI, Header, HTTPException, Response\n\napp = FastAPI()\n\nUSERS_BY_KEY = {\n    \"key-sara\": {\"name\": \"Sara\", \"role\": \"engineer\"},\n    \"key-hana\": {\"name\": \"Hana\", \"role\": \"manager\"},\n}\nDELIVERIES = {1: {\"site\": \"RYD-N\", \"qty\": 40}, 2: {\"site\": \"JED-1\", \"qty\": 30}}\n\n\ndef current_user(x_api_key: str = Header(None)):\n    user = USERS_BY_KEY.get(x_api_key)\n    if user is None:\n        raise HTTPException(status_code=401, detail=\"missing or invalid API key\")\n    return user\n\n\n@app.get(\"/me\")\ndef me(user: dict = Depends(current_user)):\n    return user\n\n\n@app.delete(\"/deliveries/{delivery_id}\", status_code=204)\ndef delete_delivery(delivery_id: int, user: dict = Depends(current_user)):\n    if user[\"role\"] != \"manager\":\n        raise HTTPException(status_code=403, detail=\"not allowed\")\n    if delivery_id not in DELIVERIES:\n        raise HTTPException(status_code=404, detail=\"delivery not found\")\n    del DELIVERIES[delivery_id]\n    return Response(status_code=204)\n\n\ncall(app, \"GET\", \"/me\", headers={\"X-API-Key\": \"key-sara\"})\ncall(app, \"DELETE\", \"/deliveries/1\", headers={\"X-API-Key\": \"key-sara\"})\n",
        "hints": [
            "`/me` is the example, as it is.",
            "The delete route takes `delivery_id: int, user: dict = Depends(current_user)`. Check the role (403), then existence (404), then `del DELIVERIES[delivery_id]` and `return Response(status_code=204)`.",
        ],
    },
]
