CHAPTER = {
    "title": "Automating calculations",
    "summary": "Hand calcs as functions, running them over whole tables, parameter sweeps, Excel output, and a small calc tool.",
}

T = 60

BEAMS_CSV = """beam,span_m,w_kn_m,Mrd_knm
B1,4.5,12.0,45.0
B2,6.0,8.5,36.0
B3,7.2,15.0,120.0
B4,3.8,20.0,40.0
B5,5.5,11.0,38.0
B6,6.6,9.0,52.0
"""

CHECK_FN = '''def beam_check(span_m, w_kn_m, Mrd_knm):
    M_ed = w_kn_m * span_m ** 2 / 8
    utilisation = round(M_ed / Mrd_knm, 3)
    status = "PASS" if utilisation <= 1.0 else "FAIL"
    return {"M_ed": M_ed, "utilisation": utilisation, "status": status}
'''

LESSONS = [
    {
        "id": "calc-function",
        "title": "A hand calc as a function",
        "kind": "code",
        "timeout": T,
        "body": """
The first step in automating any calculation is to turn the hand calc into a function: inputs as parameters, results as a return value. Then it can run once or ten thousand times.

```python
def column_check(N_ed_kn, area_mm2, fy_mpa):
    N_rd = area_mm2 * fy_mpa / 1000          # kN
    utilisation = round(N_ed_kn / N_rd, 3)
    status = "PASS" if utilisation <= 1.0 else "FAIL"
    return {"N_rd": N_rd, "utilisation": utilisation, "status": status}
```

Two things worth copying:

- Returning a **dictionary** keeps every result labelled, so nobody has to remember that item 2 of a tuple was the utilisation.
- `"PASS" if ... else "FAIL"` is a one-line `if`/`else` that gives back a value. It's called a **conditional expression**.

## Your task

Write `beam_check(span_m, w_kn_m, Mrd_knm)` for a simply supported beam that returns a dictionary with:

- `M_ed`: the design moment, `w L^2 / 8`
- `utilisation`: `M_ed / Mrd_knm`, rounded to 3 decimal places
- `status`: `"PASS"` if the utilisation is 1.0 or less, otherwise `"FAIL"`
""",
        "starter": "def beam_check(span_m, w_kn_m, Mrd_knm):\n    # M_ed = ...\n    # utilisation = ...\n    # status = ...\n    # return {...}\n    pass\n\n\nprint(beam_check(6.0, 8.5, 36.0))\n",
        "tests": '''
def test_values():
    "Right results for passing and failing beams"
    f = need("beam_check")
    for args in [(6.0, 8.5, 36.0), (4.5, 12.0, 45.0), (4.0, 10.0, 20.0)]:
        v, _ = capture(f, *args)
        s, w, m = args
        me = w * s ** 2 / 8
        want = {"M_ed": me, "utilisation": round(me / m, 3), "status": "PASS" if round(me / m, 3) <= 1 else "FAIL"}
        check(isinstance(v, dict), "Return a dictionary.")
        check(set(v) == set(want), "The keys should be M_ed, utilisation and status. Got %r." % list(v))
        for k in want:
            check(v[k] == want[k] or (k == "M_ed" and abs(v[k] - want[k]) < 1e-9), "beam_check%r gave %s = %r, expected %r." % (args, k, v[k], want[k]))
''',
        "solution": "def beam_check(span_m, w_kn_m, Mrd_knm):\n    M_ed = w_kn_m * span_m ** 2 / 8\n    utilisation = round(M_ed / Mrd_knm, 3)\n    status = \"PASS\" if utilisation <= 1.0 else \"FAIL\"\n    return {\"M_ed\": M_ed, \"utilisation\": utilisation, \"status\": status}\n\n\nprint(beam_check(6.0, 8.5, 36.0))\n",
        "hints": [
            "Same shape as `column_check`: three lines of working, then a dictionary.",
            "`status = \"PASS\" if utilisation <= 1.0 else \"FAIL\"`",
        ],
    },
    {
        "id": "batch-vector",
        "title": "Checking a whole table",
        "kind": "code",
        "timeout": T,
        "files": {"beams.csv": BEAMS_CSV},
        "body": """
With the inputs in a DataFrame, the fastest way to run the calc for every row is to write it with **columns** instead of single numbers, exactly as in the pandas chapter:

```python
df["M_ed"] = df["w_kn_m"] * df["span_m"] ** 2 / 8
```

The one piece that doesn't translate directly is the `if`. For that, `np.where(condition, value_if_true, value_if_false)` works on a whole column at once:

```python
df["status"] = np.where(df["utilisation"] <= 1.0, "PASS", "FAIL")
```

## Your task

Read `beams.csv` into `df` and add three columns: `M_ed`, `utilisation` (rounded to 3 places with `.round(3)`) and `status`. Then store `n_fail`: how many beams fail.
""",
        "starter": "import numpy as np\nimport pandas as pd\n\ndf = pd.read_csv(\"beams.csv\")\n\n# df[\"M_ed\"] = ...\n# df[\"utilisation\"] = ...\n# df[\"status\"] = np.where(...)\n# n_fail = ...\n",
        "tests": '''
import numpy as np

def test_columns():
    "M_ed, utilisation and status columns"
    df = need("df")
    for c in ("M_ed", "utilisation", "status"):
        check(c in df.columns, "Add a column called %s." % c)
    me = df["w_kn_m"] * df["span_m"] ** 2 / 8
    check(np.allclose(df["M_ed"], me), "M_ed should be w L^2 / 8.")
    check(np.allclose(df["utilisation"], (me / df["Mrd_knm"]).round(3)), "utilisation should be M_ed / Mrd_knm, rounded to 3 places.")
    check(df["status"].tolist() == ["PASS", "FAIL", "PASS", "PASS", "FAIL", "PASS"], "status is %r." % df["status"].tolist())

def test_count():
    "n_fail"
    check(need("n_fail") == 2, "n_fail should be 2, got %r." % ns.get("n_fail"))
    check("for " not in CODE, "Work with whole columns rather than a loop.")
''',
        "solution": "import numpy as np\nimport pandas as pd\n\ndf = pd.read_csv(\"beams.csv\")\n\ndf[\"M_ed\"] = df[\"w_kn_m\"] * df[\"span_m\"] ** 2 / 8\ndf[\"utilisation\"] = (df[\"M_ed\"] / df[\"Mrd_knm\"]).round(3)\ndf[\"status\"] = np.where(df[\"utilisation\"] <= 1.0, \"PASS\", \"FAIL\")\nn_fail = (df[\"status\"] == \"FAIL\").sum()\nprint(df)\n",
        "hints": [
            "`df[\"utilisation\"] = (df[\"M_ed\"] / df[\"Mrd_knm\"]).round(3)`",
            "`n_fail = (df[\"status\"] == \"FAIL\").sum()`",
        ],
    },
    {
        "id": "loop-quiz",
        "title": "Loop or columns?",
        "kind": "quiz",
        "body": "Both give the right answer. Which to reach for first?",
        "question": "You need to run a simple formula over 200,000 rows of a DataFrame. Which is the better first choice?",
        "options": [
            "A `for` loop over `df.iterrows()`, filling in each row",
            "Whole-column maths (and `np.where` for any if), as in the last lesson",
            "Copying the data into Excel",
            "It makes no difference",
        ],
        "answer": 1,
        "explain": "Column maths runs inside NumPy's compiled code and is often hundreds of times faster than a Python loop over rows. Loop over rows only when the calculation really can't be written with columns, which is the next lesson.",
    },
    {
        "id": "batch-function",
        "title": "Running a function over rows",
        "kind": "code",
        "timeout": T,
        "files": {"beams.csv": BEAMS_CSV},
        "body": """
Sometimes the calc is already a function with `if`s inside it, like `beam_check`, and rewriting it with columns isn't worth it. Then call the function once per row.

`zip` walks along several columns together, giving one value from each per step:

```python
results = [beam_check(s, w, m) for s, w, m in zip(df["span_m"], df["w_kn_m"], df["Mrd_knm"])]
out = pd.DataFrame(results)              # a list of dicts becomes a table
df = pd.concat([df, out], axis=1)        # stick the new columns on the side
```

`pd.DataFrame(list_of_dicts)` is handy: every dict becomes a row, and the keys become the column names.

## Your task

`beam_check` is written for you. Use it on every row of `beams.csv` and store `checked`: the original columns plus `M_ed`, `utilisation` and `status`, in that order.
""",
        "starter": "import pandas as pd\n\n\n" + CHECK_FN + "\n\ndf = pd.read_csv(\"beams.csv\")\n\n# results = [beam_check(...) for ... in zip(...)]\n# checked = pd.concat([df, pd.DataFrame(results)], axis=1)\n",
        "tests": '''
def test_checked():
    "Original columns plus the three results"
    c = need("checked")
    check(list(c.columns) == ["beam", "span_m", "w_kn_m", "Mrd_knm", "M_ed", "utilisation", "status"], "Columns are %r." % list(c.columns))
    check(c["status"].tolist() == ["PASS", "FAIL", "PASS", "PASS", "FAIL", "PASS"], "status is %r." % c["status"].tolist())
''',
        "solution": "import pandas as pd\n\n\n" + CHECK_FN + "\n\ndf = pd.read_csv(\"beams.csv\")\n\nresults = [beam_check(s, w, m) for s, w, m in zip(df[\"span_m\"], df[\"w_kn_m\"], df[\"Mrd_knm\"])]\nchecked = pd.concat([df, pd.DataFrame(results)], axis=1)\nprint(checked)\n",
        "hints": [
            "The two commented lines are nearly complete. Fill in `beam_check(s, w, m) for s, w, m in zip(df[\"span_m\"], df[\"w_kn_m\"], df[\"Mrd_knm\"])`.",
        ],
    },
    {
        "id": "sweep",
        "title": "Parameter sweeps",
        "kind": "code",
        "timeout": T,
        "body": """
"How long can this beam go?" "How does the utilisation change with load?" Instead of solving for one answer, run the calc over a **range** of inputs and look at the whole picture:

```python
spans = np.linspace(3, 10, 701)                  # every 10 mm
util = 9.0 * spans ** 2 / 8 / 52.0               # one utilisation per span
ok = spans[util <= 1.0]                          # spans that pass
print(ok.max())                                  # the longest one
```

A sweep is also the obvious thing to plot: utilisation against span, with a line at 1.0, tells a client more than any single number.

## Your task

Write `longest_passing_span(w_kn_m, Mrd_knm)` that sweeps spans from 1 to 15 m in steps of 0.01 m (`np.linspace(1, 15, 1401)`) and returns the longest span (rounded to 2 places) whose utilisation `w L^2 / 8 / Mrd` is at most 1.0.
""",
        "starter": "import numpy as np\n\n\ndef longest_passing_span(w_kn_m, Mrd_knm):\n    spans = np.linspace(1, 15, 1401)\n    # util = ...\n    # return the biggest span where util <= 1.0\n    pass\n\n\nprint(longest_passing_span(9.0, 52.0))   # about 6.79\n",
        "tests": '''
import numpy as np

def test_values():
    "Longest passing span from the sweep"
    f = need("longest_passing_span")
    for w, m in [(9.0, 52.0), (12.0, 45.0), (20.0, 40.0)]:
        spans = np.linspace(1, 15, 1401)
        want = round(float(spans[w * spans ** 2 / 8 / m <= 1.0].max()), 2)
        v, _ = capture(f, w, m)
        check(v is not None and abs(v - want) < 1e-9, "longest_passing_span(%r, %r) returned %r, expected %r." % (w, m, v, want))
''',
        "solution": "import numpy as np\n\n\ndef longest_passing_span(w_kn_m, Mrd_knm):\n    spans = np.linspace(1, 15, 1401)\n    util = w_kn_m * spans ** 2 / 8 / Mrd_knm\n    return round(float(spans[util <= 1.0].max()), 2)\n\n\nprint(longest_passing_span(9.0, 52.0))\n",
        "hints": [
            "`util = w_kn_m * spans ** 2 / 8 / Mrd_knm`",
            "`return round(float(spans[util <= 1.0].max()), 2)`",
        ],
    },
    {
        "id": "excel-output",
        "title": "Results to Excel",
        "kind": "code",
        "timeout": T,
        "files": {"beams.csv": BEAMS_CSV},
        "body": """
Most calc results end up in front of people who'll open them in Excel. A good layout: one sheet with every result, and a short summary sheet on top.

A summary is just a small DataFrame you build yourself:

```python
summary = pd.DataFrame({
    "item": ["checked", "passed", "failed"],
    "value": [len(df), (df["status"] == "PASS").sum(), (df["status"] == "FAIL").sum()],
})
with pd.ExcelWriter("beam_checks.xlsx") as writer:
    summary.to_excel(writer, sheet_name="summary", index=False)
    df.to_excel(writer, sheet_name="results", index=False)
```

Sheets appear in the order you write them, so write the summary first.

## Your task

The starter checks every beam. Write `beam_checks.xlsx` with a `summary` sheet (items `checked`, `passed` and `failed`, as above) followed by a `results` sheet holding `df`.
""",
        "starter": "import numpy as np\nimport pandas as pd\n\ndf = pd.read_csv(\"beams.csv\")\ndf[\"M_ed\"] = df[\"w_kn_m\"] * df[\"span_m\"] ** 2 / 8\ndf[\"utilisation\"] = (df[\"M_ed\"] / df[\"Mrd_knm\"]).round(3)\ndf[\"status\"] = np.where(df[\"utilisation\"] <= 1.0, \"PASS\", \"FAIL\")\n\n# summary = ...\n# write both sheets\n",
        "tests": '''
import pandas as pd
import os

def test_workbook():
    "summary sheet first, then results"
    check(os.path.exists("beam_checks.xlsx"), "I can't find beam_checks.xlsx.")
    xl = pd.ExcelFile("beam_checks.xlsx")
    names = xl.sheet_names
    s = pd.read_excel(xl, sheet_name="summary") if "summary" in names else None
    r = pd.read_excel(xl, sheet_name="results") if "results" in names else None
    xl.close()
    os.remove("beam_checks.xlsx")
    check(names == ["summary", "results"], "Sheets are %r, expected summary then results." % names)
    check(dict(zip(s["item"], s["value"])) == {"checked": 6, "passed": 4, "failed": 2}, "The summary sheet shows %r." % dict(zip(s["item"], s["value"])))
    check(len(r) == 6 and "status" in r.columns, "The results sheet should hold all 6 checked beams.")
''',
        "solution": "import numpy as np\nimport pandas as pd\n\ndf = pd.read_csv(\"beams.csv\")\ndf[\"M_ed\"] = df[\"w_kn_m\"] * df[\"span_m\"] ** 2 / 8\ndf[\"utilisation\"] = (df[\"M_ed\"] / df[\"Mrd_knm\"]).round(3)\ndf[\"status\"] = np.where(df[\"utilisation\"] <= 1.0, \"PASS\", \"FAIL\")\n\nsummary = pd.DataFrame({\n    \"item\": [\"checked\", \"passed\", \"failed\"],\n    \"value\": [len(df), (df[\"status\"] == \"PASS\").sum(), (df[\"status\"] == \"FAIL\").sum()],\n})\nwith pd.ExcelWriter(\"beam_checks.xlsx\") as writer:\n    summary.to_excel(writer, sheet_name=\"summary\", index=False)\n    df.to_excel(writer, sheet_name=\"results\", index=False)\n",
        "hints": [
            "Copy the example: it's the whole task.",
        ],
    },
    {
        "id": "calc-tool",
        "title": "Mini project: a beam check tool",
        "kind": "code",
        "timeout": T,
        "files": {"beams.csv": BEAMS_CSV},
        "body": """
Everything from the track in one tool you could hand to a colleague: CSV in, Excel and a plot out.

## Your task

Write `run_checks(in_csv, out_xlsx, out_png)` that:

1. reads the beams file (columns `beam`, `span_m`, `w_kn_m`, `Mrd_knm`),
2. adds `M_ed`, `utilisation` (3 places) and `status`,
3. writes `out_xlsx` with a `summary` sheet (`checked`, `passed`, `failed`) then a `results` sheet,
4. saves a bar chart to `out_png`: utilisation for each beam, a dashed horizontal line at 1.0, y label containing `Utilisation`,
5. returns a dictionary: `{"checked": ..., "passed": ..., "failed": ..., "worst": <name of the beam with the highest utilisation>}`.

Build it one step at a time with **Run**, printing as you go.
""",
        "starter": "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n\ndef run_checks(in_csv, out_xlsx, out_png):\n    df = pd.read_csv(in_csv)\n    # 2. results columns\n    # 3. Excel\n    # 4. plot\n    # 5. return the summary dict\n    pass\n\n\nprint(run_checks(\"beams.csv\", \"beam_checks.xlsx\", \"utilisation.png\"))\n",
        "tests": '''
import pandas as pd
import os

def test_tool():
    "Writes the workbook and plot, and returns the summary"
    for f in ("ks_t.xlsx", "ks_t.png"):
        if os.path.exists(f):
            os.remove(f)
    v, _ = capture(need("run_checks"), "beams.csv", "ks_t.xlsx", "ks_t.png")
    check(v == {"checked": 6, "passed": 4, "failed": 2, "worst": "B5"}, "run_checks returned %r." % (v,))
    check(os.path.exists("ks_t.xlsx"), "Write the Excel file to out_xlsx.")
    xl = pd.ExcelFile("ks_t.xlsx"); names = xl.sheet_names; xl.close()
    check(names == ["summary", "results"], "Sheets are %r, expected summary then results." % names)
    check(os.path.exists("ks_t.png"), "Save the plot to out_png.")
    os.remove("ks_t.xlsx"); os.remove("ks_t.png")

def test_plot():
    "The plot has bars, a line at 1.0 and a label"
    import matplotlib.pyplot as plt
    plt.close("all")
    capture(need("run_checks"), "beams.csv", "ks_t2.xlsx", "ks_t2.png")
    figs = [plt.figure(n) for n in plt.get_fignums()]
    check(figs, "Make the chart with plt.subplots() and leave it open (don't call plt.close).")
    ax = figs[-1].axes[0]
    check(len(ax.patches) == 6, "Draw one bar per beam with ax.bar(...).")
    check(any(l.get_linestyle() == "--" and all(abs(y - 1.0) < 1e-9 for y in l.get_ydata()) for l in ax.get_lines()), "Add a dashed line at 1.0: ax.axhline(1.0, linestyle=\\"--\\").")
    check("Utilisation" in ax.get_ylabel(), "Label the y axis Utilisation.")
    for f in ("ks_t2.xlsx", "ks_t2.png"):
        if os.path.exists(f):
            os.remove(f)
''',
        "solution": "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n\ndef run_checks(in_csv, out_xlsx, out_png):\n    df = pd.read_csv(in_csv)\n    df[\"M_ed\"] = df[\"w_kn_m\"] * df[\"span_m\"] ** 2 / 8\n    df[\"utilisation\"] = (df[\"M_ed\"] / df[\"Mrd_knm\"]).round(3)\n    df[\"status\"] = np.where(df[\"utilisation\"] <= 1.0, \"PASS\", \"FAIL\")\n\n    passed = int((df[\"status\"] == \"PASS\").sum())\n    failed = int((df[\"status\"] == \"FAIL\").sum())\n    summary = pd.DataFrame({\"item\": [\"checked\", \"passed\", \"failed\"], \"value\": [len(df), passed, failed]})\n    with pd.ExcelWriter(out_xlsx) as writer:\n        summary.to_excel(writer, sheet_name=\"summary\", index=False)\n        df.to_excel(writer, sheet_name=\"results\", index=False)\n\n    fig, ax = plt.subplots(figsize=(6, 4))\n    ax.bar(df[\"beam\"], df[\"utilisation\"])\n    ax.axhline(1.0, color=\"red\", linestyle=\"--\")\n    ax.set_ylabel(\"Utilisation (-)\")\n    fig.savefig(out_png, bbox_inches=\"tight\")\n\n    worst = df.loc[df[\"utilisation\"].idxmax(), \"beam\"]\n    return {\"checked\": len(df), \"passed\": passed, \"failed\": failed, \"worst\": worst}\n\n\nprint(run_checks(\"beams.csv\", \"beam_checks.xlsx\", \"utilisation.png\"))\n",
        "hints": [
            "Steps 2 and 3 are the last two lessons, inside the function.",
            "For the plot: `ax.bar(df[\"beam\"], df[\"utilisation\"])` and `ax.axhline(1.0, linestyle=\"--\")`.",
            "`worst = df.loc[df[\"utilisation\"].idxmax(), \"beam\"]`. Wrap the counts in `int(...)` so the dict holds plain numbers.",
        ],
    },
    {
        "id": "eng-next",
        "title": "Where to go from here",
        "kind": "read",
        "body": """
That's the engineering track. You can load messy data, clean it, summarise it, fit it, solve with it, plot it and write it up, all in a script you can rerun next month in seconds.

## Make it stick

Pick one calculation you do repeatedly at work, and automate it this week:

- a check you run in a spreadsheet for every new member,
- a report you rebuild by hand from an export,
- a test result you plot and fit every time.

Start small: inputs at the top, one function for the calc, a CSV or Excel file out. Add the plot and the summary sheet later.

## Worth exploring next

- **Jupyter notebooks** for exploring data interactively.
- **SciPy** has much more: `scipy.optimize.minimize` for optimisation, `scipy.signal` for filtering sensor data, `scipy.stats` for statistical tests.
- **openpyxl** directly, for formatted Excel output (colours, number formats, frozen headers).
- Structural packages built on all this, such as `anastruct` for 2D frame analysis.

## Next track

**Back-end development** covers the command line, Git, HTTP and APIs: how to turn a calc tool like this one into a small service other people can use from a browser.
""",
    },
]
