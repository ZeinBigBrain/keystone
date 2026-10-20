"""
Keystone code harness.

Runs in its own process (started by runner.py). Reads a JSON job from stdin:
    {"code": "...", "tests": "...", "mode": "run" | "submit"}
Runs the learner's code with stdout captured, then (in submit mode) runs every
test_* function defined in the tests string. Prints one JSON result line,
prefixed with a marker so runner.py can find it even if the learner's code
printed something odd.

Tests can use:
    OUTPUT      - everything the learner's code printed, as a string
    LINES       - OUTPUT split into lines, trailing blank line removed
    CODE        - the learner's source code with comments removed, so text
                  checks aren't fooled by words in a comment
    RAW_CODE    - the learner's source code exactly as typed
    ns          - the learner's namespace (dict)
    check(cond, msg)  - fail with msg if cond is falsy
    need(name)  - get a name from the learner's code, or fail clearly
    capture(fn, *args) - call fn, return (return_value, printed_text)
    loop_return_problem(fn_name) - "" or a message if a return inside a loop
                  in that function means it always stops on the first pass

When a check fails with a message that mentions "returned", the harness looks
at the value from the last capture() call and adds a plain-English tip for the
usual beginner slips: returning None (no return, or print instead of return),
returning the text "True" instead of True, or a number wrapped in quotes.
Errors in the learner's code also get a short tip for the common cases
(lowercase true/false, UnboundLocalError, IndentationError and so on).
"""
import io
import json
import os
import sys
import traceback
import contextlib

MARKER = "@@KEYSTONE_RESULT@@"
MAX_OUTPUT = 20000


def _strip_comments(code):
    """Remove # comments (but not # inside strings). Falls back to the
    original text if the code can't be tokenized."""
    import tokenize
    try:
        toks = [t for t in tokenize.generate_tokens(io.StringIO(code).readline)
                if t.type != tokenize.COMMENT]
        return tokenize.untokenize(toks)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return code


class TestFailure(Exception):
    pass


def _fake_input(prompt=""):
    raise RuntimeError(
        "input() isn't supported in the exercises. "
        "Use the values given in the starter code instead."
    )


_MISSING = object()


def _error_tip(exc):
    """A short, beginner-friendly note for the errors people hit most."""
    name = type(exc).__name__
    msg = str(exc)
    if isinstance(exc, UnboundLocalError) or "referenced before assignment" in msg \
            or "cannot access local variable" in msg:
        return ("Tip: the function changes a variable (for example with +=) that it never "
                "created itself. A variable made outside a function isn't yours to change "
                "inside it. Create it inside the function, above the loop, e.g. total = 0.")
    if isinstance(exc, ModuleNotFoundError) and getattr(exc, "name", ""):
        top = exc.name.split(".")[0]
        if top in ("numpy", "pandas", "matplotlib", "scipy", "openpyxl"):
            return ("Tip: %s isn't installed for the Python that runs Keystone. Open the first lesson "
                    "of Python for engineering and click Install." % top)
        if top in ("fastapi", "uvicorn", "httpx", "requests", "starlette", "pydantic"):
            return ("Tip: %s isn't installed for the Python that runs Keystone. Open the lesson "
                    "\"Installing FastAPI\" in Back-end development and click Install." % top)
    if isinstance(exc, NameError):
        missing = getattr(exc, "name", None)
        if missing is None and "'" in msg:
            missing = msg.split("'")[1]
        if missing in ("true", "false", "none", "TRUE", "FALSE", "null"):
            return ("Tip: Python writes these with a capital first letter: True, False and None.")
        return ("Tip: check the spelling (capitals count) and that the name is created before "
                "this line runs. Names created inside a function don't exist outside it.")
    if name == "TypeError" and "NoneType" in msg:
        return ("Tip: one of the values here is None. A function with no return statement "
                "hands back None, so check the function you called.")
    if name == "TypeError" and "concatenate" in msg:
        return ("Tip: + can't join text and a number. Use an f-string, e.g. f\"Total: {total}\".")
    if name == "TypeError" and "not callable" in msg:
        return ("Tip: something that isn't a function has brackets after it. Did you reuse a "
                "function's name for a variable?")
    return ""


def _syntax_tip(e):
    msg = (e.msg or "").lower()
    if isinstance(e, IndentationError) or "indent" in msg:
        return ("Tip: lines in the same block must start at the same column. Lines inside a "
                "def, if, for or while go one level (4 spaces) further in than the line with "
                "the colon. Lines after the block go back out.")
    if "expected ':'" in msg or "invalid syntax" in msg:
        text = (e.text or "").strip()
        if text.startswith(("def ", "if ", "elif ", "else", "for ", "while ", "class ", "try", "except")) \
                and not text.rstrip().endswith(":"):
            return "Tip: lines starting with def, if, elif, else, for, while and class end with a colon."
    if "never closed" in msg or "was never closed" in msg or "unexpected eof" in msg:
        return "Tip: a bracket or quote is opened but never closed. Count them on this line and the one above."
    return ""


def _return_tip(value, printed):
    """Explain a suspicious return value. Empty string if nothing stands out."""
    if value is _MISSING:
        return ""
    if value is None:
        if printed.strip():
            return ("Tip: the function printed %r but returned None. print() only shows a value "
                    "on screen. Use return to hand it back." % printed.strip()[:60])
        return ("Tip: the function returned None. Either there's no return, or the return is "
                "indented somewhere that never runs.")
    if isinstance(value, str):
        bare = value.strip().rstrip(".!").strip()
        if bare.lower() in ("true", "false"):
            return ("Tip: you returned the text %r. Return the bool %s itself, with no quotes "
                    "and a capital first letter." % (value, bare.capitalize()))
        try:
            float(bare)
            return ("Tip: you returned the text %r, not a number. Return the number itself, "
                    "without quotes or an f-string around it." % value)
        except ValueError:
            pass
    return ""


def _loop_return_problem(code, fn_name):
    """Spot the two classic early-exit slips inside a loop:
    a bare return directly in the loop body, or an if/else where both
    branches return (so the loop never gets past its first value)."""
    import ast
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ""
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == fn_name]
    for fn in funcs:
        for loop in ast.walk(fn):
            if not isinstance(loop, (ast.For, ast.While)):
                continue
            for stmt in loop.body:
                if isinstance(stmt, ast.Return):
                    return ("Your return is inside the loop, so the function stops the first "
                            "time round. Move it back out so it lines up with the %s line."
                            % ("for" if isinstance(loop, ast.For) else "while"))
                if isinstance(stmt, ast.If) and stmt.orelse \
                        and isinstance(stmt.body[-1], ast.Return) \
                        and isinstance(stmt.orelse[-1], ast.Return):
                    return ("Both your if and your else return, and they're inside the loop, so "
                            "the loop only ever checks its first value. Keep the early return in "
                            "the if, drop the else, and put the other return after the loop.")
    return ""


def _user_traceback(exc):
    """Keep only the traceback frames that belong to the learner's code."""
    tb = traceback.extract_tb(exc.__traceback__)
    lines = []
    for frame in tb:
        if frame.filename == "<your code>":
            text = "  line %d, in %s" % (frame.lineno, frame.name)
            if frame.line:
                text += "\n    " + frame.line.strip()
            lines.append(text)
    name = type(exc).__name__
    msg = str(exc)
    head = "Traceback (your code):\n" + "\n".join(lines) if lines else ""
    tail = "%s: %s" % (name, msg) if msg else name
    tip = _error_tip(exc)
    return (head + "\n" + tail + ("\n\n" + tip if tip else "")).strip()


def _add_user_site():
    """The runner starts Python with -I (isolated), which also hides packages
    installed with pip --user. Put that folder back on the path so NumPy,
    pandas and friends are found however they were installed."""
    try:
        import site
        p = site.getusersitepackages()
        if p and os.path.isdir(p) and p not in sys.path:
            sys.path.append(p)
    except Exception:
        pass


def _write_files(files):
    """Lesson data files (CSV and so on) go into the sandbox before the run."""
    for name, text in (files or {}).items():
        name = os.path.basename(name)
        with open(name, "w", encoding="utf-8", newline="") as f:
            f.write(text)


# ---------------------------------------------------------------- SQL ----

def _strip_sql_comments(sql):
    out, i, n = [], 0, len(sql)
    quote = None
    while i < n:
        c = sql[i]
        if quote:
            out.append(c)
            if c == quote:
                quote = None
            i += 1
        elif c in ("'", '"'):
            quote = c
            out.append(c)
            i += 1
        elif sql.startswith("--", i):
            while i < n and sql[i] != "\n":
                i += 1
        elif sql.startswith("/*", i):
            end = sql.find("*/", i + 2)
            i = n if end == -1 else end + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _split_sql(text):
    """Split a script into statements, respecting quotes and comments."""
    import sqlite3
    stmts, buf = [], ""
    parts = text.split(";")
    for k, part in enumerate(parts):
        buf += part + (";" if k < len(parts) - 1 else "")
        if sqlite3.complete_statement(buf):
            if _strip_sql_comments(buf).strip(" \n\t\r;"):
                stmts.append(buf.strip())
            buf = ""
    if _strip_sql_comments(buf).strip(" \n\t\r;"):
        stmts.append(buf.strip())
    return stmts


def _fresh_db(setup):
    import sqlite3
    db = sqlite3.connect(":memory:", isolation_level=None)
    db.execute("PRAGMA foreign_keys = ON")
    if setup:
        db.executescript(setup)
    return db


def _fmt_table(cols, rows, limit=50):
    def cell(v):
        if v is None:
            return "NULL"
        if isinstance(v, float):
            return ("%.4f" % v).rstrip("0").rstrip(".") if v != int(v) or abs(v) > 1e15 else "%.1f" % v
        return str(v)
    shown = [[cell(v) for v in r] for r in rows[:limit]]
    widths = [len(c) for c in cols]
    for r in shown:
        widths = [max(w, len(v)) for w, v in zip(widths, r)]
    line = lambda vals: " | ".join(v.ljust(w) for v, w in zip(vals, widths)).rstrip()
    out = [line(cols), "-+-".join("-" * w for w in widths)]
    out += [line(r) for r in shown]
    more = len(rows) - limit
    out.append("(%d row%s%s)" % (len(rows), "" if len(rows) == 1 else "s",
                                 ", first %d shown" % limit if more > 0 else ""))
    return "\n".join(out)


def _sql_tip(msg, db=None):
    m = msg.lower()
    if m.startswith("no such column"):
        return ("Tip: check the spelling of that column. Text values need single quotes: "
                "WHERE name = 'cement'. Without quotes, SQL reads cement as a column name.")
    if m.startswith("no such table"):
        names = ""
        if db is not None:
            try:
                names = ", ".join(r[0] for r in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
            except Exception:
                pass
        return "Tip: check the table name." + (" The tables here are: %s." % names if names else "")
    if "syntax error" in m:
        word = msg.split('"')[1] if '"' in msg else ""
        return ("Tip: SQL got confused just before %s. The usual causes: a missing or extra comma "
                "between columns, a keyword spelt wrong, or clauses in the wrong order "
                "(SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT)." % (repr(word) if word else "the end"))
    if "incomplete input" in m:
        return "Tip: something is opened but never closed. Look for a missing bracket or quote."
    if "ambiguous column" in m:
        return ("Tip: two of the joined tables have a column with this name. Put the table name "
                "(or its alias) in front of it, like m.name.")
    if "misuse of aggregate" in m:
        return ("Tip: a condition on COUNT, SUM, AVG and so on belongs in HAVING, after GROUP BY. "
                "WHERE runs before the groups exist.")
    if "not null constraint" in m:
        return "Tip: that column is NOT NULL, so every new row must give it a value."
    if "unique constraint" in m:
        return "Tip: that column must be unique, and the value you used is already in the table."
    if "foreign key constraint" in m:
        return ("Tip: the id you referred to doesn't exist in the other table (or rows still point "
                "at the one you're deleting).")
    if "check constraint" in m:
        return "Tip: the value breaks a CHECK rule on the table."
    return ""


def _run_sql(job, result):
    import sqlite3
    code = job.get("code", "")
    setup = job.get("setup", "")
    db = _fresh_db(setup)
    stmts = _split_sql(code)
    out_parts = []
    state = {"rows": None, "cols": None}
    for n, stmt in enumerate(stmts, 1):
        try:
            cur = db.execute(stmt)
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                state["rows"], state["cols"] = rows, cols
                out_parts.append(_fmt_table(cols, rows))
            elif cur.rowcount is not None and cur.rowcount >= 0:
                out_parts.append("(%d row%s changed)" % (cur.rowcount, "" if cur.rowcount == 1 else "s"))
        except sqlite3.Error as e:
            first = _strip_sql_comments(stmt).strip().splitlines()
            where = ("statement %d" % n) if len(stmts) > 1 else "your SQL"
            detail = "Error in %s: %s" % (where, e)
            if first:
                detail += "\n    " + first[0][:120]
            tip = _sql_tip(str(e), db)
            result["error"] = detail + ("\n\n" + tip if tip else "")
            break
    if not stmts:
        out_parts.append("(nothing to run yet)")
    result["output"] = "\n\n".join(out_parts)
    return db, state


def _sql_test_names(job, db, state, code):
    """Names the SQL tests can use."""
    setup = job.get("setup", "")

    def norm(rows):
        out = []
        for r in rows:
            out.append(tuple(round(v, 6) if isinstance(v, float) else v for v in r))
        return out

    def query(sql):
        return db.execute(sql).fetchall()

    def fresh(sql):
        d = _fresh_db(setup)
        try:
            cur = d.execute(sql)
            return [x[0] for x in cur.description] if cur.description else [], cur.fetchall()
        finally:
            d.close()

    def check_rows(ref_sql, ordered=False, hint=""):
        want_cols, want = fresh(ref_sql)
        if state["cols"] is None:
            raise TestFailure("Your SQL didn't return any rows to check. Write a SELECT query.")
        got_cols, got = state["cols"], state["rows"]
        if len(got_cols) != len(want_cols):
            raise TestFailure("Your query returns %d column%s (%s), but this needs %d (%s)." % (
                len(got_cols), "" if len(got_cols) == 1 else "s", ", ".join(got_cols),
                len(want_cols), ", ".join(want_cols)))
        g, w = norm(got), norm(want)
        if len(g) != len(w):
            msg = "Your query returned %d row%s, expected %d." % (len(g), "" if len(g) == 1 else "s", len(w))
            if hint:
                msg += " " + hint
            raise TestFailure(msg)
        if sorted(g, key=repr) != sorted(w, key=repr):
            extra = [r for r in g if r not in w]
            missing = [r for r in w if r not in g]
            msg = "Right number of rows, but some are different."
            if missing:
                msg += "\nExpected a row like %r" % (missing[0],)
            if extra:
                msg += "\nbut got %r" % (extra[0],)
            if hint:
                msg += "\n" + hint
            raise TestFailure(msg)
        if ordered:
            # ordered=True compares whole rows; a tuple of column positions
            # compares only those columns, so ties can come in any order.
            if ordered is True:
                same = g == w
            else:
                proj = lambda rows: [tuple(r[i] for i in ordered) for r in rows]
                same = proj(g) == proj(w)
            if not same:
                raise TestFailure("Right rows, wrong order. Check your ORDER BY (and ASC or DESC).")

    def check_columns(*names):
        got = [c.lower() for c in (state["cols"] or [])]
        want = [n.lower() for n in names]
        if got != want:
            raise TestFailure("The columns should be named %s. Yours are %s. Use AS to rename one." % (
                ", ".join(names), ", ".join(state["cols"] or []) or "nothing"))

    return {
        "ROWS": state["rows"],
        "COLUMNS": state["cols"],
        "db": db,
        "query": query,
        "fresh": fresh,
        "check_rows": check_rows,
        "check_columns": check_columns,
        "SQL": " ".join(_strip_sql_comments(code).split()),
    }


# ---------------------------------------------------------------- main ---

def main():
    job = json.loads(sys.stdin.read())
    code = job.get("code", "")
    tests = job.get("tests", "")
    mode = job.get("mode", "run")
    lang = job.get("lang", "python")

    result = {"output": "", "error": None, "tests": [], "passed": False}
    _add_user_site()
    try:
        _write_files(job.get("files"))
    except OSError as e:
        result["error"] = "Couldn't prepare the lesson's files: %s" % e
        print(MARKER + json.dumps(result))
        return

    ns = {"__name__": "__main__", "input": _fake_input}
    extra = {}

    # A lesson's prelude runs first, out of sight, in the learner's namespace.
    # HTTP lessons use it to start a small local test server (BASE_URL).
    prelude = job.get("prelude", "")
    if prelude and lang == "python":
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(prelude, "<lesson setup>", "exec"), ns)
        except BaseException as e:  # our bug, not the learner's
            result["error"] = "The lesson's setup failed: %s: %s" % (type(e).__name__, e)
            print(MARKER + json.dumps(result))
            return
        # The checks can use the prelude's public names too (BASE_URL and so on)
        extra.update({k: v for k, v in ns.items() if not k.startswith("_")})

    if lang == "sql":
        db, state = _run_sql(job, result)
        extra = _sql_test_names(job, db, state, code)
    elif lang == "text":
        result["output"] = ("This exercise isn't run as code. Submit it and the checks will "
                            "read what you've written.")
    else:
        buf = io.StringIO()
        # 1. Compile (gives a clean syntax error with the right line number)
        try:
            compiled = compile(code, "<your code>", "exec")
        except SyntaxError as e:
            detail = "SyntaxError: %s (line %s)" % (e.msg, e.lineno)
            if e.text:
                detail += "\n    " + e.text.rstrip()
            tip = _syntax_tip(e)
            if tip:
                detail += "\n\n" + tip
            result["error"] = detail
            print(MARKER + json.dumps(result))
            return

        # 2. Run the learner's code with output captured
        try:
            with contextlib.redirect_stdout(buf):
                exec(compiled, ns)
        except SystemExit:
            pass
        except BaseException as e:  # noqa: B036 - we want everything here
            result["error"] = _user_traceback(e)
        result["output"] = buf.getvalue()

    output = result["output"]
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + "\n... (output cut off)"
    result["output"] = output

    if mode != "submit":
        print(MARKER + json.dumps(result))
        return

    if result["error"]:
        result["tests"] = [{
            "name": "Your code ran without errors",
            "ok": False,
            "message": "Fix the error above first, then submit again.",
        }]
        print(MARKER + json.dumps(result))
        return

    # 3. Run the tests
    def check(cond, msg="Check failed"):
        if not cond:
            raise TestFailure(msg)

    def need(name):
        if name not in ns:
            raise TestFailure("I couldn't find `%s` in your code. Did you define it with that exact name?" % name)
        return ns[name]

    last = {"value": _MISSING, "out": ""}

    def capture(fn, *args, **kwargs):
        """Call fn and return (return_value, printed_text)."""
        b = io.StringIO()
        last["value"], last["out"] = _MISSING, ""
        with contextlib.redirect_stdout(b):
            value = fn(*args, **kwargs)
        last["value"], last["out"] = value, b.getvalue()
        return value, b.getvalue()

    lines = output.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    tns = {
        "OUTPUT": output,
        "CODE": _strip_comments(code) if lang == "python" else code,
        "RAW_CODE": code,
        "LINES": lines,
        "ns": ns,
        "check": check,
        "need": need,
        "capture": capture,
        "loop_return_problem": lambda name: _loop_return_problem(code, name),
        "TestFailure": TestFailure,
    }
    tns.update(extra)
    try:
        exec(compile(tests, "<tests>", "exec"), tns)
    except BaseException as e:  # a broken test file is our bug, not theirs
        result["tests"] = [{"name": "Loading tests", "ok": False,
                            "message": "Test file error: %r" % e}]
        print(MARKER + json.dumps(result))
        return

    test_funcs = [(k, v) for k, v in tns.items()
                  if k.startswith("test_") and callable(v)]

    all_ok = True
    for name, fn in test_funcs:
        label = (fn.__doc__ or name).strip()
        entry = {"name": label, "ok": True, "message": ""}
        last["value"], last["out"] = _MISSING, ""
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
        except TestFailure as e:
            entry["ok"] = False
            entry["message"] = str(e)
            if "returned" in entry["message"] and lang == "python":
                tip = _return_tip(last["value"], last["out"])
                if tip and "Tip:" not in entry["message"]:
                    entry["message"] += "\n" + tip
        except AssertionError as e:
            entry["ok"] = False
            entry["message"] = str(e) or "Assertion failed"
        except BaseException as e:
            entry["ok"] = False
            entry["message"] = "Your code raised an error during this check: %s: %s" % (type(e).__name__, e)
            tip = _error_tip(e) if lang == "python" else _sql_tip(str(e)) if lang == "sql" else ""
            if tip:
                entry["message"] += "\n" + tip
        if not entry["ok"]:
            all_ok = False
        result["tests"].append(entry)

    result["passed"] = all_ok and len(test_funcs) > 0
    print(MARKER + json.dumps(result, default=str))


if __name__ == "__main__":
    main()
