import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Deploying",
    "summary": "Configuration and secrets, logging, health checks, where to host, and keeping it running.",
}

T = 20

LESSONS = [
    {
        "id": "config",
        "title": "Configuration",
        "kind": "code",
        "timeout": T,
        "body": """
Everything that differs between your laptop and the server is **configuration**, and it comes from environment variables. Gather it in one place, at start-up:

```python
import os

def load_settings():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return {
        "database_url": url,
        "debug": os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes"),
    }
```

Two habits worth copying:

- **Fail fast and loudly** when something required is missing. A clear error at start-up beats a confusing crash on the first request at 2 a.m.
- **Convert types once**, here, so the rest of the code gets an int or a bool, not text.

## Your task

Write `load_settings()` returning a dict with:

| Key | From | Rules |
|---|---|---|
| `database_url` | `DATABASE_URL` | required: raise `RuntimeError` (mentioning `DATABASE_URL`) if missing or empty |
| `debug` | `DEBUG` | `True` for `1`, `true` or `yes` (any case), otherwise `False`; default `False` |
| `port` | `PORT` | an int, default `8000` |
| `allowed_hosts` | `ALLOWED_HOSTS` | comma-separated, as a list with spaces trimmed; default `["localhost"]` |
""",
        "starter": "import os\n\n\ndef load_settings():\n    pass\n\n\nos.environ[\"DATABASE_URL\"] = \"sqlite:///dev.db\"\nprint(load_settings())\n",
        "tests": '''
import os

KEYS = ("DATABASE_URL", "DEBUG", "PORT", "ALLOWED_HOSTS")

def run_with(**env):
    saved = {k: os.environ.get(k) for k in KEYS}
    for k in KEYS:
        os.environ.pop(k, None)
    os.environ.update(env)
    try:
        return need("load_settings")()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def test_defaults():
    "Defaults when only DATABASE_URL is set"
    s = run_with(DATABASE_URL="sqlite:///x.db")
    check(s == {"database_url": "sqlite:///x.db", "debug": False, "port": 8000, "allowed_hosts": ["localhost"]}, "Got %r." % (s,))

def test_values():
    "Reads and converts every setting"
    s = run_with(DATABASE_URL="postgresql://db/site", DEBUG="TRUE", PORT="9000", ALLOWED_HOSTS="api.site.com, site.com")
    check(s.get("debug") is True and s.get("port") == 9000, "DEBUG=TRUE should give True, and PORT=9000 the int 9000. Got %r." % (s,))
    check(s.get("allowed_hosts") == ["api.site.com", "site.com"], "ALLOWED_HOSTS should split on commas and trim spaces. Got %r." % (s.get("allowed_hosts"),))
    check(run_with(DATABASE_URL="x", DEBUG="no")["debug"] is False, "DEBUG=no should give False.")

def test_required():
    "Missing DATABASE_URL fails clearly"
    for env in ({}, {"DATABASE_URL": ""}):
        try:
            run_with(**env)
        except RuntimeError as e:
            check("DATABASE_URL" in str(e), "Mention DATABASE_URL in the error message.")
            continue
        check(False, "Without DATABASE_URL, load_settings should raise RuntimeError.")
''',
        "solution": "import os\n\n\ndef load_settings():\n    url = os.environ.get(\"DATABASE_URL\")\n    if not url:\n        raise RuntimeError(\"DATABASE_URL is not set\")\n    hosts = os.environ.get(\"ALLOWED_HOSTS\", \"localhost\")\n    return {\n        \"database_url\": url,\n        \"debug\": os.environ.get(\"DEBUG\", \"false\").lower() in (\"1\", \"true\", \"yes\"),\n        \"port\": int(os.environ.get(\"PORT\", \"8000\")),\n        \"allowed_hosts\": [h.strip() for h in hosts.split(\",\") if h.strip()],\n    }\n\n\nos.environ[\"DATABASE_URL\"] = \"sqlite:///dev.db\"\nprint(load_settings())\n",
        "hints": [
            "Start from the example and add `port` with `int(os.environ.get(\"PORT\", \"8000\"))`.",
            "`[h.strip() for h in hosts.split(\",\") if h.strip()]`, where `hosts` defaults to `\"localhost\"`.",
        ],
    },
    {
        "id": "secrets",
        "title": "Secrets",
        "kind": "read",
        "body": """
Database passwords, API keys and token-signing keys are **secrets**. A leaked one can expose every user's data, so they get special treatment.

## Rules

1. **Never in code, never in Git.** Not even "just for now" in a private repo. Git remembers forever, and private repos get shared, cloned and leaked.
2. **Never in a Docker image.** Anyone with the image can read them.
3. **Never in logs or error messages.** Logs get copied around much more freely than databases.
4. **Different secrets for each environment.** Your laptop, the test server and production each have their own, so a leak of one doesn't open the others.
5. **If one leaks, rotate it** (replace it with a new one) straight away, then work out how it happened.

## Where they live instead

- **Locally:** a `.env` file in the project folder, listed in `.gitignore`. Libraries like `python-dotenv` load it into the environment at start-up. Commit a `.env.example` with the variable names and fake values, so others know what to set.
- **On a server or platform:** the host's settings page or a **secret manager** (AWS Secrets Manager, Azure Key Vault, Doppler and so on), which hand them to your app as environment variables.

Your code doesn't change between the two: it just reads `os.environ`.
""",
    },
    {
        "id": "logging",
        "title": "Logging",
        "kind": "code",
        "timeout": T,
        "body": """
On a server, `print` isn't enough. You need to know **when** something happened, **how serious** it was, and **where** in the code. The `logging` module gives you all three:

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("site_api")

log.info("delivery recorded: id=%s qty=%s", 25, 40)
log.warning("supplier %s slow to respond", 3)
log.error("could not reach the database")
```

| Level | For |
|---|---|
| `DEBUG` | detail you only want while hunting a bug |
| `INFO` | normal events worth a record |
| `WARNING` | something odd, but the app carried on |
| `ERROR` | something failed |

Notice the `%s` placeholders with the values passed separately. The logging module only builds the message text if that level is actually switched on.

## Your task

Write `record_delivery(site, qty)` using the `log` logger:

- if `qty` is 0 or less, log an **ERROR** `rejected delivery: qty must be positive` and raise `ValueError`
- otherwise log an **INFO** `delivery recorded: site=<site> qty=<qty>`
- and if `qty` is over 1000, **also** log a **WARNING** `unusually large delivery: site=<site> qty=<qty>`
""",
        "starter": "import logging\n\nlogging.basicConfig(level=logging.INFO, format=\"%(levelname)s %(name)s: %(message)s\")\nlog = logging.getLogger(\"site_api\")\n\n\ndef record_delivery(site, qty):\n    pass\n\n\nrecord_delivery(\"RYD-N\", 40)\nrecord_delivery(\"RYD-N\", 5000)\n",
        "tests": '''
import logging

class Grab(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
    def emit(self, record):
        self.records.append((record.levelname, record.getMessage()))

def run(*args):
    g = Grab()
    lg = logging.getLogger("site_api")
    lg.addHandler(g)
    lg.setLevel(logging.DEBUG)
    err = None
    try:
        need("record_delivery")(*args)
    except ValueError as e:
        err = e
    finally:
        lg.removeHandler(g)
    return g.records, err

def test_normal():
    "INFO for a normal delivery"
    recs, err = run("JED-1", 30)
    check(err is None, "A normal delivery shouldn't raise.")
    check(recs == [("INFO", "delivery recorded: site=JED-1 qty=30")], "Logged %r." % recs)

def test_large():
    "INFO and a WARNING for a large one"
    recs, _ = run("RYD-S", 1500)
    check(("INFO", "delivery recorded: site=RYD-S qty=1500") in recs, "Still log the INFO line for large deliveries. Logged %r." % recs)
    check(("WARNING", "unusually large delivery: site=RYD-S qty=1500") in recs, "Log a WARNING for qty over 1000. Logged %r." % recs)
    recs, _ = run("RYD-S", 1000)
    check(not any(l == "WARNING" for l, _ in recs), "Exactly 1000 isn't over 1000, so no warning.")

def test_bad():
    "ERROR and ValueError for qty of 0 or less"
    recs, err = run("RYD-N", 0)
    check(isinstance(err, ValueError), "qty 0 should raise ValueError.")
    check(recs == [("ERROR", "rejected delivery: qty must be positive")], "Logged %r." % recs)
''',
        "solution": "import logging\n\nlogging.basicConfig(level=logging.INFO, format=\"%(levelname)s %(name)s: %(message)s\")\nlog = logging.getLogger(\"site_api\")\n\n\ndef record_delivery(site, qty):\n    if qty <= 0:\n        log.error(\"rejected delivery: qty must be positive\")\n        raise ValueError(\"qty must be positive\")\n    log.info(\"delivery recorded: site=%s qty=%s\", site, qty)\n    if qty > 1000:\n        log.warning(\"unusually large delivery: site=%s qty=%s\", site, qty)\n\n\nrecord_delivery(\"RYD-N\", 40)\nrecord_delivery(\"RYD-N\", 5000)\n",
        "hints": [
            "A guard first: `if qty <= 0:` log the error and raise.",
            "`log.info(\"delivery recorded: site=%s qty=%s\", site, qty)`, then `if qty > 1000:` a `log.warning(...)` in the same style.",
        ],
    },
    {
        "id": "logging-quiz",
        "title": "What not to log",
        "kind": "quiz",
        "body": "Logs are copied, shipped to other services and read by lots of people. Think about what goes in them.",
        "question": "Which of these should never be written to a log?",
        "options": [
            "The id of the delivery that was created",
            "How long a request took",
            "The API key from the request's header",
            "The status code returned",
        ],
        "answer": 2,
        "explain": "An API key in a log works just as well for whoever reads the log. Log *that* a request was authenticated, and as whom, never the credential itself. The same goes for passwords, tokens and session ids.",
    },
    {
        "id": "health",
        "title": "Health checks",
        "kind": "code",
        "timeout": T,
        "prelude": S.FASTAPI_TOOLS,
        "body": """
Hosting platforms, load balancers and monitoring tools need to know: is the app actually working? The convention is a `/health` endpoint that checks the app's own dependencies and answers quickly:

- **200** when everything's fine.
- **503 Service Unavailable** when something it needs is down. The platform can then stop sending it traffic, or restart it.

```python
from fastapi.responses import JSONResponse

@app.get("/health")
def health():
    try:
        check_db()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded"})
    return {"status": "ok"}
```

`JSONResponse` lets you return JSON with a status other than the route's default.

## Your task

Write `GET /health` that calls `check_db()` (given) and returns:

- **200** with `{"status": "ok", "database": "ok"}` when it works
- **503** with `{"status": "degraded", "database": "unreachable"}` when it raises any exception
""",
        "starter": "import sqlite3\n\nfrom fastapi import FastAPI\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\nconn = sqlite3.connect(\":memory:\", check_same_thread=False)\n\n\ndef check_db():\n    conn.execute(\"SELECT 1\")\n\n\n# GET /health here\n\n\ncall(app, \"GET\", \"/health\")\n",
        "tests": '''
from fastapi.testclient import TestClient

def test_ok():
    "200 when the database answers"
    r = TestClient(need("app")).get("/health")
    check(r.status_code == 200 and r.json() == {"status": "ok", "database": "ok"}, "GET /health gave %s %s." % (r.status_code, r.text))

def test_down():
    "503 when it doesn't"
    real = ns["check_db"]
    def broken():
        raise RuntimeError("database is down")
    ns["check_db"] = broken
    try:
        r = TestClient(need("app")).get("/health")
    finally:
        ns["check_db"] = real
    check(r.status_code == 503 and r.json() == {"status": "degraded", "database": "unreachable"},
          "With the database down, GET /health gave %s %s." % (r.status_code, r.text))
''',
        "solution": "import sqlite3\n\nfrom fastapi import FastAPI\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\nconn = sqlite3.connect(\":memory:\", check_same_thread=False)\n\n\ndef check_db():\n    conn.execute(\"SELECT 1\")\n\n\n@app.get(\"/health\")\ndef health():\n    try:\n        check_db()\n    except Exception:\n        return JSONResponse(status_code=503, content={\"status\": \"degraded\", \"database\": \"unreachable\"})\n    return {\"status\": \"ok\", \"database\": \"ok\"}\n\n\ncall(app, \"GET\", \"/health\")\n",
        "hints": [
            "The example, with the extra `database` key in both answers.",
        ],
    },
    {
        "id": "hosting",
        "title": "Where to host it",
        "kind": "read",
        "body": """
Once it runs in a container, an API can run almost anywhere. The options, from least to most work:

## Platforms (PaaS)

Services like **Render**, **Railway**, **Fly.io** or **Heroku**. Connect your GitHub repo or push an image, set environment variables in their dashboard, and they build, run, restart and give you HTTPS. Most offer managed PostgreSQL too. The best place to start: you think about your app, not servers. Costs rise as you grow.

## Containers on a cloud provider

**AWS** (ECS, App Runner), **Azure** (Container Apps, App Service) or **Google Cloud** (Cloud Run). More settings and more control, with pricing that scales from tiny to enormous. Common in companies that already use that cloud.

## Your own virtual server (VPS)

A Linux machine from **DigitalOcean**, **Hetzner**, **Linode** or a cloud provider. Cheapest for steady traffic and you control everything, which also means you do everything: security updates, firewall, HTTPS certificates, backups, restarts.

## Serverless functions

**AWS Lambda**, **Azure Functions**, **Google Cloud Functions**: code runs only when a request arrives, and you pay per request. Excellent for spiky or light traffic. Less suited to apps that keep a connection open or need to start up fast every time.

## Choosing

For a first real deployment: a platform, a managed database, and environment variables for configuration. Move to something else when you have a concrete reason (cost, control, company policy), not before.
""",
    },
    {
        "id": "keeping-running",
        "title": "Keeping it running",
        "kind": "read",
        "body": """
Deploying is the start, not the end. An app in production needs a few things around it.

## Restarts

Processes crash. Something must notice and restart them: the platform does this for you; with Docker, `docker run --restart unless-stopped`; on a bare server, `systemd`. Pair it with the health check, so an app that's running but broken also gets replaced.

## More than one copy

Run at least two copies behind a **load balancer**, so one can crash or be updated without any downtime. This works as long as the app keeps no important state in memory: everything lives in the database. (That's one more reason the dicts in the early lessons had to go.)

## Monitoring and alerts

You want to hear about problems before your users do:

- **Logs** collected in one searchable place.
- **Metrics:** request rate, error rate, response time.
- **Alerts** when error rates or response times cross a line.
- **Uptime checks** that call `/health` from outside every minute.

## Backups

Back up the database automatically, keep copies somewhere separate, and actually **test restoring one**. A backup you've never restored is a hope, not a backup.

## Updates

Dependencies get security fixes. Update them regularly, run the tests, deploy. Small frequent updates are far less risky than a giant one every two years.
""",
    },
    {
        "id": "deploy-quiz",
        "title": "Production readiness",
        "kind": "quiz",
        "body": "One question across this chapter.",
        "question": "Your API runs as two containers behind a load balancer. Where should a user's uploaded delivery records be kept?",
        "options": [
            "In a Python dict in the app's memory",
            "In a file inside the container",
            "In the shared database (and uploaded files in shared storage)",
            "In the logs",
        ],
        "answer": 2,
        "explain": "Each container has its own memory and filesystem, and both vanish when the container is replaced. With two copies, a record saved in one container's memory would be missing when the next request lands on the other. Shared state belongs in the database.",
    },
]
