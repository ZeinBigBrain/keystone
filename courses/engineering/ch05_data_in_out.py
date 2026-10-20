CHAPTER = {
    "title": "Getting data in and out",
    "summary": "Reading and writing CSV, messy headers and units rows, dates, and Excel files.",
}

T = 40

LOADS_CSV = """member,axial_kn,moment_knm,length_m
C1,1250,85,3.6
C2,1410,62,3.6
C3,980,120,4.2
C4,1620,45,3.6
C5,1105,98,4.2
C6,870,140,4.8
"""

GAUGE_CSV = """Strain gauge export
Logger: SG-04  Channel: 2
time,strain,temp
s,microstrain,C
0,12,24.1
10,58,24.3
20,105,24.2
30,151,24.6
40,198,24.8
50,240,25.0
60,287,25.1
"""

DELIVERIES_CSV = """date,site,material,qty
2026-10-01,RYD-N,cement,40
2026-10-02,RYD-S,cement,25
2026-10-03,RYD-N,gravel,18
2026-10-05,JED-1,rebar,2
2026-10-06,RYD-N,timber,4
2026-10-07,RYD-N,cement,35
2026-10-08,RYD-S,rebar,5
2026-10-09,RYD-N,tiles,120
2026-10-12,RYD-N,sand,10
2026-10-13,JED-1,cement,20
"""

LESSONS = [
    {
        "id": "read-csv",
        "title": "Reading a CSV file",
        "kind": "code",
        "timeout": T,
        "files": {"loads.csv": LOADS_CSV},
        "body": """
CSV (comma-separated values) is the format almost every program can export: Excel, test rigs, analysis software, data loggers. pandas reads one in a single line:

```python
import pandas as pd

df = pd.read_csv("loads.csv")
print(df.head())       # the first 5 rows
print(df.shape)        # (rows, columns)
print(df.columns)      # the column names, taken from the first line
print(df.dtypes)       # the type pandas chose for each column
```

pandas uses the first line as column names and works out each column's type from its values. **Always look at what it read** before doing anything else. Most data problems show up right there.

There's a file called `loads.csv` ready for this lesson. It holds column loads from an analysis.

## Your task

Read `loads.csv` into `df`, then store:

- `n_rows`: how many rows it has
- `mean_axial`: the mean of the `axial_kn` column
""",
        "starter": "import pandas as pd\n\n# df = ...\n# print(df.head())\n\n# n_rows = ...\n# mean_axial = ...\n",
        "tests": '''
import pandas as pd

def test_values():
    "Read the file and summarised it"
    df = need("df")
    check(isinstance(df, pd.DataFrame) and list(df.columns) == ["member", "axial_kn", "moment_knm", "length_m"], "Read loads.csv with pd.read_csv.")
    check(need("n_rows") == 6, "n_rows should be 6, got %r. len(df) or df.shape[0] gives it." % ns.get("n_rows"))
    check(abs(need("mean_axial") - 1205.833333) < 1e-3, "mean_axial should be about 1205.83, got %r." % ns.get("mean_axial"))
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"loads.csv\")\nprint(df.head())\n\nn_rows = len(df)\nmean_axial = df[\"axial_kn\"].mean()\nprint(n_rows, mean_axial)\n",
        "hints": [
            "`df = pd.read_csv(\"loads.csv\")`",
            "`n_rows = len(df)` and `mean_axial = df[\"axial_kn\"].mean()`.",
        ],
    },
    {
        "id": "to-csv",
        "title": "Writing a CSV file",
        "kind": "code",
        "timeout": T,
        "files": {"loads.csv": LOADS_CSV},
        "body": """
Going the other way:

```python
df.to_csv("results.csv", index=False)
```

`index=False` stops pandas writing the row numbers (0, 1, 2 ...) as an extra first column. You almost always want it.

## Your task

Read `loads.csv`, add a column `eccentricity_mm` equal to `moment_knm / axial_kn * 1000`, and save the table to `loads_checked.csv` **without** the index.
""",
        "starter": "import pandas as pd\n\ndf = pd.read_csv(\"loads.csv\")\n\n# add eccentricity_mm\n\n# save to loads_checked.csv without the index\n",
        "tests": '''
import pandas as pd
import numpy as np
import os

def test_file():
    "loads_checked.csv has the new column and no index column"
    check(os.path.exists("loads_checked.csv"), "I can't find loads_checked.csv. Did you call df.to_csv(...)?")
    out = pd.read_csv("loads_checked.csv")
    check(not any(str(c).startswith("Unnamed") for c in out.columns), "The file has an extra unnamed column. Add index=False.")
    check(list(out.columns) == ["member", "axial_kn", "moment_knm", "length_m", "eccentricity_mm"], "Columns in the file: %r." % list(out.columns))
    os.remove("loads_checked.csv")   # so an old file can't pass next time
    check(np.allclose(out["eccentricity_mm"], out["moment_knm"] / out["axial_kn"] * 1000), "eccentricity_mm values are wrong.")
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"loads.csv\")\n\ndf[\"eccentricity_mm\"] = df[\"moment_knm\"] / df[\"axial_kn\"] * 1000\n\ndf.to_csv(\"loads_checked.csv\", index=False)\n",
        "hints": [
            "`df[\"eccentricity_mm\"] = df[\"moment_knm\"] / df[\"axial_kn\"] * 1000`",
            "`df.to_csv(\"loads_checked.csv\", index=False)`",
        ],
    },
    {
        "id": "skiprows",
        "title": "Skipping junk at the top",
        "kind": "code",
        "timeout": T,
        "files": {"gauge.csv": GAUGE_CSV},
        "body": """
Real exports are rarely tidy. Here's the top of `gauge.csv`, straight from a data logger:

```
Strain gauge export
Logger: SG-04  Channel: 2
time,strain,temp
s,microstrain,C
0,12,24.1
10,58,24.3
```

Two lines of notes, then the column names, then a line of **units**, then the data. `pd.read_csv("gauge.csv")` on its own fails, because it takes "Strain gauge export" as the header and then finds lines with more fields than that.

`skiprows=n` skips the first `n` lines:

```python
raw = pd.read_csv("gauge.csv", skiprows=2)
```

Now the header line is right. But look closely at what comes out.

## Your task

Read the file with `skiprows=2` into `raw` and print `raw.head()` and `raw.dtypes`. Then store `first_strain`: the value in the first row of the `strain` column (`raw.loc[0, "strain"]`).
""",
        "starter": "import pandas as pd\n\n# raw = pd.read_csv(\"gauge.csv\", skiprows=2)\n# print(raw.head())\n# print(raw.dtypes)\n\n# first_strain = ...\n",
        "tests": '''
def test_read():
    "Read with skiprows=2"
    raw = need("raw")
    check(list(raw.columns) == ["time", "strain", "temp"], "The columns should be time, strain, temp. Use skiprows=2.")
    check(need("first_strain") == "microstrain", "first_strain should be what's in row 0 of strain. Got %r." % ns.get("first_strain"))
''',
        "solution": "import pandas as pd\n\nraw = pd.read_csv(\"gauge.csv\", skiprows=2)\nprint(raw.head())\nprint(raw.dtypes)\n\nfirst_strain = raw.loc[0, \"strain\"]\nprint(first_strain)\n",
        "hints": [
            "Uncomment the three lines, then `first_strain = raw.loc[0, \"strain\"]`.",
        ],
    },
    {
        "id": "units-row-quiz",
        "title": "Why is it text?",
        "kind": "quiz",
        "body": "Look at the dtypes you printed in the last lesson.",
        "question": "With the units row read in as data, `raw[\"strain\"]` comes out as text (dtype `object` or `str`), not numbers. Why?",
        "options": [
            "pandas always reads CSV values as text",
            "The units row put the word `microstrain` in the column, and a column has one type, so everything became text",
            "Strain values are too small to be numbers",
            "skiprows changes every column to text",
        ],
        "answer": 1,
        "explain": "A column holds a single type. One text value (`microstrain`) forces the whole column to text, so `raw[\"strain\"].mean()` won't work. The fix is to skip the units row as well, which is the next lesson.",
    },
    {
        "id": "units-row",
        "title": "Dropping the units row",
        "kind": "code",
        "timeout": T,
        "files": {"gauge.csv": GAUGE_CSV},
        "body": """
`skiprows` also takes a **list of line numbers** (counting from 0) to skip. For `gauge.csv`, that's the two note lines (0 and 1) and the units line (3), keeping line 2 as the header:

```python
df = pd.read_csv("gauge.csv", skiprows=[0, 1, 3])
```

Now every column is numeric.

If the units are worth keeping, read them separately and put them in the column names:

```python
units = pd.read_csv("gauge.csv", skiprows=2, nrows=1).iloc[0]
# time: s, strain: microstrain, temp: C
```

## Your task

Write `load_gauge(path)` that reads a file laid out like `gauge.csv` and returns a DataFrame with numeric `time`, `strain` and `temp` columns.
""",
        "starter": "import pandas as pd\n\n\ndef load_gauge(path):\n    pass\n\n\ndf = load_gauge(\"gauge.csv\")\nprint(df.dtypes)\nprint(df[\"strain\"].max())   # should print 287\n",
        "tests": '''
import pandas as pd

def test_numeric():
    "All three columns are numbers"
    v, _ = capture(need("load_gauge"), "gauge.csv")
    check(isinstance(v, pd.DataFrame) and list(v.columns) == ["time", "strain", "temp"], "Return the DataFrame, with columns time, strain, temp.")
    for c in ("time", "strain", "temp"):
        check(pd.api.types.is_numeric_dtype(v[c]), "Column %s is still text. Skip the units line too: skiprows=[0, 1, 3]." % c)
    check(len(v) == 7 and v["strain"].max() == 287, "Expected 7 rows of data with a maximum strain of 287.")
''',
        "solution": "import pandas as pd\n\n\ndef load_gauge(path):\n    return pd.read_csv(path, skiprows=[0, 1, 3])\n\n\ndf = load_gauge(\"gauge.csv\")\nprint(df.dtypes)\nprint(df[\"strain\"].max())\n",
        "hints": [
            "`return pd.read_csv(path, skiprows=[0, 1, 3])`",
        ],
    },
    {
        "id": "dates",
        "title": "Dates and times",
        "kind": "code",
        "timeout": T,
        "files": {"deliveries.csv": DELIVERIES_CSV},
        "body": """
Dates in a CSV arrive as text. Ask pandas to turn them into real dates with `parse_dates`:

```python
df = pd.read_csv("deliveries.csv", parse_dates=["date"])
df["date"].dt.day_name()        # Thursday, Friday ...
df["date"].dt.month             # 10, 10, ...
df[df["date"] >= "2026-10-08"]  # compare with a date written as text
```

The `.dt` part unlocks date tools on a column, the same way `.str` unlocks text tools (next chapter).

Real dates also sort properly, subtract to give time gaps, and plot on a proper time axis.

## Your task

Read `deliveries.csv` with the `date` column parsed. Add a column `weekday` holding each delivery's day name. Then store `first_week`: the rows dated from 1 to 7 October 2026, both included.
""",
        "starter": "import pandas as pd\n\n# df = pd.read_csv(..., parse_dates=[\"date\"])\n# df[\"weekday\"] = ...\n# first_week = ...\n",
        "tests": '''
import pandas as pd

def test_dates():
    "date is a real date column, with weekday added"
    df = need("df")
    check(pd.api.types.is_datetime64_any_dtype(df["date"]), "date is still text. Use parse_dates=[\\"date\\"].")
    check(df["weekday"].tolist()[:3] == ["Thursday", "Friday", "Saturday"], "weekday should be the day names, like Thursday. Use .dt.day_name().")

def test_week():
    "first_week has 1 to 7 October"
    fw = need("first_week")
    check(len(fw) == 6, "first_week has %d rows, expected 6 (1st to 7th inclusive)." % len(fw))
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"deliveries.csv\", parse_dates=[\"date\"])\ndf[\"weekday\"] = df[\"date\"].dt.day_name()\nfirst_week = df[(df[\"date\"] >= \"2026-10-01\") & (df[\"date\"] <= \"2026-10-07\")]\nprint(first_week)\n",
        "hints": [
            "`df[\"weekday\"] = df[\"date\"].dt.day_name()`",
            "Two conditions with `&`: `(df[\"date\"] >= \"2026-10-01\") & (df[\"date\"] <= \"2026-10-07\")`.",
        ],
    },
    {
        "id": "excel",
        "title": "Excel files",
        "kind": "code",
        "timeout": T,
        "files": {"loads.csv": LOADS_CSV},
        "body": """
Excel works the same way, through the `openpyxl` package installed in the first chapter:

```python
df.to_excel("results.xlsx", sheet_name="loads", index=False)
back = pd.read_excel("results.xlsx", sheet_name="loads")
```

`read_excel` also takes `skiprows`, `header` and `usecols`, so the tricks from earlier carry over.

To write **several sheets** to one file, use an `ExcelWriter` in a `with` block:

```python
with pd.ExcelWriter("report.xlsx") as writer:
    df.to_excel(writer, sheet_name="all", index=False)
    df[df["axial_kn"] > 1200].to_excel(writer, sheet_name="heavy", index=False)
```

> Excel can't save a file while it's open in Excel. If you get a `PermissionError`, close the workbook and run again.

## Your task

Read `loads.csv` and write it to `report.xlsx` with **two sheets**: `all`, holding every row, and `long`, holding only members with `length_m` over 4. No index columns.
""",
        "starter": "import pandas as pd\n\ndf = pd.read_csv(\"loads.csv\")\n\n# write report.xlsx with sheets \"all\" and \"long\"\n",
        "tests": '''
import pandas as pd
import os

def test_file():
    "report.xlsx has both sheets with the right rows"
    check(os.path.exists("report.xlsx"), "I can't find report.xlsx.")
    sheets = pd.read_excel("report.xlsx", sheet_name=None)
    os.remove("report.xlsx")   # so an old file can't pass next time
    check(set(sheets) == {"all", "long"}, "The sheets are %r, expected all and long." % list(sheets))
    check(len(sheets["all"]) == 6, "Sheet all should have 6 rows.")
    check(sheets["long"]["member"].tolist() == ["C3", "C5", "C6"], "Sheet long should hold C3, C5 and C6 (length over 4).")
    check(list(sheets["all"].columns)[0] == "member", "There's an extra index column. Add index=False.")
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"loads.csv\")\n\nwith pd.ExcelWriter(\"report.xlsx\") as writer:\n    df.to_excel(writer, sheet_name=\"all\", index=False)\n    df[df[\"length_m\"] > 4].to_excel(writer, sheet_name=\"long\", index=False)\n",
        "hints": [
            "Copy the ExcelWriter example and change the sheet names and the filter.",
            "`df[df[\"length_m\"] > 4].to_excel(writer, sheet_name=\"long\", index=False)`",
        ],
    },
    {
        "id": "io-task",
        "title": "Chapter task: logger to report",
        "kind": "code",
        "timeout": T,
        "files": {"gauge.csv": GAUGE_CSV},
        "body": """
A small pipeline: messy logger file in, tidy Excel out.

## Your task

Write `gauge_report(in_path, out_path)` that:

1. reads a logger file laid out like `gauge.csv` (numeric columns, units row dropped),
2. adds a column `stress_mpa`: strain (in microstrain) times `1e-6` times E, with E = 200,000 MPa,
3. writes the table to `out_path` as an Excel file with one sheet called `results`, no index,
4. returns the DataFrame.
""",
        "starter": "import pandas as pd\n\nE_MPA = 200_000\n\n\ndef gauge_report(in_path, out_path):\n    pass\n\n\nprint(gauge_report(\"gauge.csv\", \"gauge_report.xlsx\"))\n",
        "tests": '''
import pandas as pd
import numpy as np
import os

def test_report():
    "Returns the table and writes the Excel file"
    if os.path.exists("ks_gauge_test.xlsx"):
        os.remove("ks_gauge_test.xlsx")
    v, _ = capture(need("gauge_report"), "gauge.csv", "ks_gauge_test.xlsx")
    check(isinstance(v, pd.DataFrame), "Return the DataFrame.")
    check(np.allclose(v["stress_mpa"], v["strain"] * 1e-6 * 200000), "stress_mpa should be strain * 1e-6 * 200000.")
    check(os.path.exists("ks_gauge_test.xlsx"), "Write the Excel file to out_path.")
    back = pd.read_excel("ks_gauge_test.xlsx", sheet_name="results")
    check(list(back.columns) == ["time", "strain", "temp", "stress_mpa"], "The results sheet has columns %r." % list(back.columns))
    os.remove("ks_gauge_test.xlsx")
''',
        "solution": "import pandas as pd\n\nE_MPA = 200_000\n\n\ndef gauge_report(in_path, out_path):\n    df = pd.read_csv(in_path, skiprows=[0, 1, 3])\n    df[\"stress_mpa\"] = df[\"strain\"] * 1e-6 * E_MPA\n    df.to_excel(out_path, sheet_name=\"results\", index=False)\n    return df\n\n\nprint(gauge_report(\"gauge.csv\", \"gauge_report.xlsx\"))\n",
        "hints": [
            "Reading is the `load_gauge` line from earlier. Then add the column.",
            "`df.to_excel(out_path, sheet_name=\"results\", index=False)` then `return df`.",
        ],
    },
]
