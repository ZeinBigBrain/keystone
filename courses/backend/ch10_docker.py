import importlib.util as _u
import os as _o

_s = _u.spec_from_file_location("ks_backend_shared", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_shared.py"))
S = _u.module_from_spec(_s)
_s.loader.exec_module(S)

CHAPTER = {
    "title": "Docker",
    "summary": "Images and containers, writing a Dockerfile, the commands you'll use, and docker compose with a database.",
}

DOCKERFILE_HELPERS = r'''
def instructions():
    """[(INSTRUCTION, args)] from a Dockerfile, joining continued lines."""
    out, buf = [], ""
    for line in RAW_CODE.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.endswith("\\"):
            buf += s[:-1] + " "
            continue
        s = buf + s
        buf = ""
        parts = s.split(None, 1)
        out.append((parts[0].upper(), parts[1].strip() if len(parts) > 1 else ""))
    return out

def first(instr, items=None):
    items = instructions() if items is None else items
    for i, (k, v) in enumerate(items):
        if k == instr:
            return i, v
    return -1, None
'''

YAML_HELPERS = r'''
def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
    return v

def parse_yaml(text):
    """A small YAML reader: nested mappings, '- item' lists, inline [a, b] lists.
    Enough for a compose file."""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        lines.append((len(raw) - len(raw.lstrip(" ")), raw.strip()))
    pos = [0]

    def block(indent):
        if pos[0] < len(lines) and lines[pos[0]][1].startswith("- "):
            items = []
            while pos[0] < len(lines) and lines[pos[0]][0] == indent and lines[pos[0]][1].startswith("- "):
                items.append(_scalar(lines[pos[0]][1][2:]))
                pos[0] += 1
            return items
        mapping = {}
        while pos[0] < len(lines) and lines[pos[0]][0] == indent:
            text_ = lines[pos[0]][1]
            if ":" not in text_:
                raise ValueError("expected 'key: value' in: " + text_)
            key, _, val = text_.partition(":")
            pos[0] += 1
            if val.strip():
                mapping[key.strip()] = _scalar(val)
            elif pos[0] < len(lines) and lines[pos[0]][0] > indent:
                mapping[key.strip()] = block(lines[pos[0]][0])
            else:
                mapping[key.strip()] = None
        return mapping

    if not lines:
        return {}
    return block(lines[0][0])

def env_dict(env):
    """environment: as a mapping or a list of KEY=value."""
    if isinstance(env, dict):
        return {k: str(v) for k, v in env.items()}
    out = {}
    for item in env or []:
        k, _, v = str(item).partition("=")
        out[k] = v
    return out
'''

LESSONS = [
    {
        "id": "docker-what",
        "title": "Images and containers",
        "kind": "read",
        "body": """
"It works on my machine" is the oldest problem in software. Your API needs a particular Python, particular packages, maybe a particular database. The server has something slightly different, and things break.

**Docker** packages an app together with everything it needs to run (the operating system files, Python, the packages, your code) into one bundle that runs the same way everywhere.

## Two words to get straight

- An **image** is the bundle: a read-only template. You **build** it once from a recipe called a `Dockerfile`.
- A **container** is a running copy of an image. You can start many containers from one image, stop them, delete them, and start fresh ones. They're cheap and fast, a bit like starting a program.

The class and object from the Python course are a good comparison: the image is the class, a container is an instance.

## Layers

An image is built in **layers**, one per instruction in the Dockerfile. Docker caches each layer, and when you rebuild, it reuses every layer up to the first one whose inputs changed. That's why the order of instructions matters, as you'll see.

## Getting it

Install **Docker Desktop** (Windows or Mac) from docker.com. On Windows it uses WSL under the hood. Check it works with `docker run hello-world`.
""",
    },
    {
        "id": "image-quiz",
        "title": "Image or container?",
        "kind": "quiz",
        "body": "Make sure the two words are clear before going on.",
        "question": "You build one image for your API, then start it three times to handle more traffic. How many images and containers are there?",
        "options": ["3 images, 3 containers", "1 image, 3 containers", "3 images, 1 container", "1 image, 1 container"],
        "answer": 1,
        "explain": "One image (the template) can run as any number of containers (the running copies). Scaling up means starting more containers from the same image.",
    },
    {
        "id": "dockerfile",
        "title": "Writing a Dockerfile",
        "kind": "code",
        "lang": "text",
        "body": """
A `Dockerfile` is the recipe, one instruction per line:

| Instruction | Does |
|---|---|
| `FROM python:3.12-slim` | start from an existing image (here, a small Linux with Python 3.12) |
| `WORKDIR /app` | the folder to work in inside the image (created if needed) |
| `COPY src dest` | copy files from your project into the image |
| `RUN command` | run a command while **building** (e.g. installing packages) |
| `EXPOSE 8000` | document which port the app listens on |
| `CMD ["prog", "arg"]` | the command to run when a **container starts** |

For a FastAPI app the recipe is almost always:

1. start from a Python image,
2. set a working folder,
3. copy `requirements.txt` in and install it,
4. copy the rest of the code in,
5. start uvicorn.

Two details matter for uvicorn in a container: `--host 0.0.0.0` (so it accepts connections from outside the container, not just from inside it) and the port.

## Your task

Write the Dockerfile for an app in `main.py` (with `app = FastAPI()` inside), following the five steps above. Use `python:3.12-slim`, work in `/app`, install with `pip install --no-cache-dir -r requirements.txt`, and run uvicorn on port `8000`. Write `CMD` in the bracketed list form.
""",
        "starter": "# Dockerfile\n",
        "tests": DOCKERFILE_HELPERS + '''
import json

def test_base():
    "Starts FROM a Python image and sets WORKDIR"
    items = instructions()
    check(items and items[0][0] == "FROM" and items[0][1].startswith("python:3.12"), "Start with: FROM python:3.12-slim")
    i, v = first("WORKDIR", items)
    check(v == "/app", "Add: WORKDIR /app")

def test_install():
    "Copies requirements.txt and installs it"
    items = instructions()
    copies = [(i, v) for i, (k, v) in enumerate(items) if k == "COPY"]
    req = [i for i, v in copies if v.split()[0] == "requirements.txt"]
    check(req, "Copy requirements.txt in on its own: COPY requirements.txt .")
    runs = [i for i, (k, v) in enumerate(items) if k == "RUN" and "pip install" in v and "requirements.txt" in v]
    check(runs and runs[0] > req[0], "After copying it, install it: RUN pip install --no-cache-dir -r requirements.txt")

def test_code_and_cmd():
    "Copies the code after installing, then runs uvicorn"
    items = instructions()
    runs = [i for i, (k, v) in enumerate(items) if k == "RUN" and "pip install" in v]
    code = [i for i, (k, v) in enumerate(items) if k == "COPY" and v.split()[0] in (".", "./")]
    check(code, "Copy the rest of the code in: COPY . .")
    check(runs and code[0] > runs[0], "Copy the code AFTER installing requirements, so code changes don't make Docker reinstall every package.")
    i, cmd = first("CMD", items)
    check(cmd is not None, "Finish with a CMD that starts uvicorn.")
    try:
        args = json.loads(cmd)
    except ValueError:
        check(False, "Write CMD in the list form, with double quotes: CMD [\\"uvicorn\\", \\"main:app\\", ...]")
    check(args[:2] == ["uvicorn", "main:app"], "CMD should start uvicorn with main:app. Got %r." % args)
    check("--host" in args and args[args.index("--host") + 1] == "0.0.0.0", "Pass --host 0.0.0.0 so the app can be reached from outside the container.")
    check("--port" in args and args[args.index("--port") + 1] == "8000", "Pass --port 8000.")
''',
        "solution": "# Dockerfile\nFROM python:3.12-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
        "hints": [
            "Six or seven lines: FROM, WORKDIR, COPY requirements.txt ., RUN pip install ..., COPY . ., (EXPOSE 8000), CMD [...].",
            "`CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]`",
        ],
    },
    {
        "id": "cache-quiz",
        "title": "Why that order?",
        "kind": "quiz",
        "body": "The order in the last lesson wasn't an accident.",
        "question": "Why copy `requirements.txt` and install it **before** `COPY . .`?",
        "options": [
            "pip can't see files copied later",
            "So a code change only rebuilds the last layers, and Docker reuses the cached package install",
            "Docker requires requirements.txt to be first",
            "It makes the image smaller",
        ],
        "answer": 1,
        "explain": "You change code constantly and requirements rarely. With requirements first, the slow `pip install` layer is cached and reused on every rebuild until requirements.txt itself changes. Copy everything first and every one-line code change reinstalls every package.",
    },
    {
        "id": "dockerignore",
        "title": ".dockerignore",
        "kind": "code",
        "lang": "text",
        "body": """
`COPY . .` copies **everything** in the folder, including things that should never go in an image: your virtual environment (big, and built for your machine), Git history, local databases, and secrets.

A `.dockerignore` file works like `.gitignore`: one pattern per line, and matching files are left out of the build.

## Your task

Write a `.dockerignore` that leaves out: the `.venv` folder, the `.git` folder, `__pycache__` folders, every `.db` file, and the `.env` file.
""",
        "starter": "# .dockerignore\n",
        "tests": '''
def test_patterns():
    "All five patterns"
    got = [l.strip().rstrip("/") for l in RAW_CODE.splitlines() if l.strip() and not l.strip().startswith("#")]
    def has(*opts):
        return any(o in got for o in opts)
    check(has(".venv"), "Leave out the virtual environment: .venv")
    check(has(".git"), "Leave out Git's history: .git")
    check(has("__pycache__", "**/__pycache__"), "Leave out __pycache__")
    check(has("*.db", "**/*.db"), "Leave out database files: *.db")
    check(has(".env"), "Leave out the secrets file: .env")
''',
        "solution": "# .dockerignore\n.venv/\n.git/\n__pycache__/\n*.db\n.env\n",
        "hints": [
            "Five lines, the same style as the .gitignore lesson.",
        ],
    },
    {
        "id": "docker-commands",
        "title": "Building and running",
        "kind": "code",
        "lang": "text",
        "body": """
The everyday commands:

| Command | Does |
|---|---|
| `docker build -t site-api .` | build an image from the Dockerfile in `.`, and tag (name) it `site-api` |
| `docker run -p 8000:8000 site-api` | start a container from it, connecting port 8000 on your machine to 8000 inside |
| `docker run -d ...` | the same, in the background (detached) |
| `docker ps` | list running containers |
| `docker logs <container>` | show a container's output |
| `docker stop <container>` | stop it |

`-p host:container` is the bit people forget. A container is sealed off by default. Without `-p`, the app runs happily inside, and `http://localhost:8000` on your machine finds nothing.

## Your task

Write the commands to: build the image from the current folder with the tag `site-api`, run it in the background with port 8000 published, then list the running containers.
""",
        "starter": "# one command per line\n",
        "tests": S.TEXT_HELPERS + '''
def test_commands():
    "build, run, ps"
    in_order([
        ("building the image", ["docker build -t site-api .", "docker build --tag site-api ."]),
        ("running it detached with port 8000", ["docker run -d -p 8000:8000 site-api", "docker run -p 8000:8000 -d site-api",
                                                "docker run --detach -p 8000:8000 site-api", "docker run -d --publish 8000:8000 site-api"]),
        ("listing containers", ["docker ps"]),
    ])
''',
        "solution": "docker build -t site-api .\ndocker run -d -p 8000:8000 site-api\ndocker ps\n",
        "hints": [
            "Don't forget the `.` at the end of the build command: it's the folder to build from.",
            "`docker run -d -p 8000:8000 site-api`",
        ],
    },
    {
        "id": "volumes-env",
        "title": "Data, ports and settings",
        "kind": "read",
        "body": """
Containers are meant to be thrown away and replaced. That has consequences.

## Data disappears with the container

Anything a container writes inside itself is lost when it's removed. For a database, that's everything. A **volume** is storage that lives outside the container and survives it:

```
docker run -v site-data:/var/lib/postgresql/data postgres:16
```

Here `site-data` is a named volume, mounted at the folder where Postgres keeps its files. Delete and recreate the container, and the data is still there.

## Settings come from the environment

The same image should run on your laptop and on the server. What differs (database address, secrets, debug mode) is passed in as environment variables, exactly as in the command line chapter:

```
docker run -e DATABASE_URL=postgresql://... -e DEBUG=false site-api
```

Never bake secrets into an image with `ENV` in the Dockerfile. Anyone with the image can read them.

## Ports, again

`-p 8000:8000` publishes a port to your machine. Containers in the same **compose** project (next lesson) can talk to each other directly by service name, without publishing anything.
""",
    },
    {
        "id": "compose",
        "title": "docker compose with a database",
        "kind": "code",
        "lang": "text",
        "body": """
An API plus a database is two containers, with settings, ports and a volume. Typing all that into `docker run` commands gets old fast. **docker compose** describes the whole set in one YAML file, `compose.yaml`, and `docker compose up` starts everything:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://site:secret@db:5432/site
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: site
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: site
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

YAML is indentation-based like Python: nested settings are indented two spaces, and lists use `- `. Notice the database host in `DATABASE_URL` is just `db`, the service's name. Compose gives the services a private network where they find each other by name.

## Your task

Write a `compose.yaml` with two services:

- `web`: built from `.`, publishing port `8080` on your machine to `8000` in the container, with `DATABASE_URL` set to `postgresql://app:pw@db:5432/app`, and depending on `db`
- `db`: the image `postgres:16`, with `POSTGRES_USER` `app`, `POSTGRES_PASSWORD` `pw`, `POSTGRES_DB` `app`, and a named volume `dbdata` mounted at `/var/lib/postgresql/data`

Declare the `dbdata` volume at the bottom.
""",
        "starter": "services:\n",
        "tests": YAML_HELPERS + '''
def doc():
    try:
        return parse_yaml(RAW_CODE)
    except ValueError as e:
        check(False, "I couldn't read the YAML: %s. Check the indentation (two spaces per level) and the colons." % e)

def test_web():
    "The web service"
    d = doc()
    services = d.get("services") or {}
    check("web" in services and "db" in services, "Define two services under services: web and db.")
    web = services["web"] or {}
    check(web.get("build") in (".", "./"), "web should have build: .")
    ports = web.get("ports") or []
    check("8080:8000" in [str(p) for p in ports], "web should publish \\"8080:8000\\" (your machine first, container second).")
    env = env_dict(web.get("environment"))
    check(env.get("DATABASE_URL") == "postgresql://app:pw@db:5432/app", "web needs DATABASE_URL: postgresql://app:pw@db:5432/app")
    dep = web.get("depends_on") or []
    check("db" in (dep if isinstance(dep, list) else list(dep)), "web should depend on db.")

def test_db():
    "The db service and its volume"
    d = doc()
    db = (d.get("services") or {}).get("db") or {}
    check(db.get("image") == "postgres:16", "db should use image: postgres:16")
    env = env_dict(db.get("environment"))
    check(env.get("POSTGRES_USER") == "app" and env.get("POSTGRES_PASSWORD") == "pw" and env.get("POSTGRES_DB") == "app",
          "db needs POSTGRES_USER app, POSTGRES_PASSWORD pw and POSTGRES_DB app. Got %r." % env)
    check("dbdata:/var/lib/postgresql/data" in [str(v) for v in (db.get("volumes") or [])], "Mount the volume: - dbdata:/var/lib/postgresql/data")
    check("dbdata" in (d.get("volumes") or {}), "Declare the volume at the bottom: volumes: then dbdata:")
''',
        "solution": "services:\n  web:\n    build: .\n    ports:\n      - \"8080:8000\"\n    environment:\n      DATABASE_URL: postgresql://app:pw@db:5432/app\n    depends_on:\n      - db\n\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_USER: app\n      POSTGRES_PASSWORD: pw\n      POSTGRES_DB: app\n    volumes:\n      - dbdata:/var/lib/postgresql/data\n\nvolumes:\n  dbdata:\n",
        "hints": [
            "Follow the example's layout exactly, changing the names and values. Indentation is two spaces per level.",
            "The ports line is `- \"8080:8000\"`: your machine's port first.",
        ],
    },
    {
        "id": "compose-quiz",
        "title": "Finding the database",
        "kind": "quiz",
        "body": "One last compose question.",
        "question": "In the compose file, why is the database host written as `db` in `DATABASE_URL`, rather than `localhost`?",
        "options": [
            "`db` is a shorter way to write localhost",
            "Inside the api container, localhost means the api container itself; compose lets services reach each other by service name",
            "PostgreSQL only accepts the name db",
            "It's a typo that compose fixes automatically",
        ],
        "answer": 1,
        "explain": "Each container has its own `localhost`. Compose puts the services on a shared network where each one's name works as a host name, so the api reaches Postgres at `db:5432`.",
    },
]
