CHAPTER = {
    "title": "Cleaning data",
    "summary": "Missing values, duplicates, fixing column types, and catching values that can't be right.",
}

T = 40

CUBES_CSV = """sample,pour,age_days,strength_mpa
S01,P1,7,24.5
S02,P1,7,
S03,P1,28,41.2
S04,P2,7,22.8
S05,P2,28,39.5
S05,P2,28,39.5
S06,P2,28,
S07,P3,7,25.1
S08,P3,28,43.0
S08,P3,28,43.0
"""

LOADS_TEXT_CSV = """member,load
B1, 12.5 kN
B2,13kN
B3,n/a
B4,9.75 kN
B5,
B6,11 kN
"""

TESTS_CSV = """Cube test results
sample,pour,age_days,strength
-,-,days,MPa
S01,P1,7,24.5 MPa
S02,P1,7,missing
S03,P1,28,41.2
S04,P2,7,22.8
S05,P2,28,39.5
S05,P2,28,39.5
S06,P2,28,412
S07,P3,7,25.1
S08,P3,28,43.0
S09,P3,28,-3
"""

LESSONS = [
    {
        "id": "missing",
        "title": "Missing values",
        "kind": "code",
        "timeout": T,
        "files": {"cubes.csv": CUBES_CSV},
        "body": """
An empty cell in a CSV becomes `NaN` in pandas: "not a number", pandas' way of saying "no value here" (like SQL's `NULL`).

```python
df.isna().sum()                 # how many missing in each column
df[df["strength_mpa"].isna()]   # the rows where it's missing
df.dropna(subset=["strength_mpa"])        # drop rows missing that column
df["strength_mpa"].fillna(0)              # fill gaps with a value (careful!)
```

Most calculations skip `NaN` quietly: `.mean()` averages only the values that are there. That's usually what you want, but it means a column that's half empty can still give a confident-looking average. Always count the gaps first.

**Dropping or filling?** For test results, dropping a missing reading is honest. Filling it with 0 would drag every average down, and filling it with the average invents data. Only fill when you know what the right value is.

## Your task

`cubes.csv` holds concrete cube test results. Read it, then store:

- `n_missing`: how many `strength_mpa` values are missing
- `tested`: the table with those rows dropped
""",
        "starter": "import pandas as pd\n\ndf = pd.read_csv(\"cubes.csv\")\nprint(df)\n\n# n_missing = ...\n# tested = ...\n",
        "tests": '''
def test_values():
    "Counted and dropped the gaps"
    check(need("n_missing") == 2, "n_missing should be 2, got %r. Try df[\\"strength_mpa\\"].isna().sum()." % ns.get("n_missing"))
    t = need("tested")
    check(len(t) == 8 and t["strength_mpa"].notna().all(), "tested should have the 8 rows that have a strength.")
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"cubes.csv\")\nprint(df)\n\nn_missing = df[\"strength_mpa\"].isna().sum()\ntested = df.dropna(subset=[\"strength_mpa\"])\nprint(n_missing, len(tested))\n",
        "hints": [
            "`df[\"strength_mpa\"].isna().sum()`",
            "`df.dropna(subset=[\"strength_mpa\"])`",
        ],
    },
    {
        "id": "nan-quiz",
        "title": "Averages with gaps",
        "kind": "quiz",
        "body": "One question about what the last lesson warned of.",
        "question": "A column holds `[40, NaN, 44]`. What does `.mean()` return?",
        "options": ["`28.0`", "`42.0`", "`NaN`", "An error"],
        "answer": 1,
        "explain": "pandas skips `NaN` and averages the two values that exist: (40 + 44) / 2 = 42. If you'd filled the gap with 0 first, you'd get 28, which is wrong in a way that's easy to miss.",
    },
    {
        "id": "duplicates",
        "title": "Duplicate rows",
        "kind": "code",
        "timeout": T,
        "files": {"cubes.csv": CUBES_CSV},
        "body": """
Data that's been copied, merged or re-exported often has rows repeated. Left in, they count twice in every total and average.

```python
df.duplicated().sum()                       # how many rows repeat an earlier one exactly
df.drop_duplicates()                        # keep the first copy of each
df.drop_duplicates(subset=["sample"])       # same sample id = same row, whatever else differs
```

Which columns define "the same"? That's a judgement about your data. Here, each sample is tested once, so the sample id alone should be unique.

## Your task

Read `cubes.csv`, then store:

- `n_dupes`: how many rows are exact repeats of an earlier row
- `unique`: the table with duplicate **sample ids** removed, keeping the first of each
""",
        "starter": "import pandas as pd\n\ndf = pd.read_csv(\"cubes.csv\")\n\n# n_dupes = ...\n# unique = ...\n",
        "tests": '''
def test_values():
    "Counted and removed duplicates"
    check(need("n_dupes") == 2, "n_dupes should be 2, got %r." % ns.get("n_dupes"))
    u = need("unique")
    check(len(u) == 8 and u["sample"].is_unique, "unique should have 8 rows, each sample once. Use drop_duplicates(subset=[\\"sample\\"]).")
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"cubes.csv\")\n\nn_dupes = df.duplicated().sum()\nunique = df.drop_duplicates(subset=[\"sample\"])\nprint(n_dupes, len(unique))\n",
        "hints": [
            "`df.duplicated().sum()` counts them.",
            "`df.drop_duplicates(subset=[\"sample\"])`",
        ],
    },
    {
        "id": "fix-types",
        "title": "Numbers stored as text",
        "kind": "code",
        "timeout": T,
        "files": {"member_loads.csv": LOADS_TEXT_CSV},
        "body": """
Someone typed units into the numbers: `" 12.5 kN"`, `"13kN"`, `"n/a"`. Now the column is text, and you can't do maths with it.

Two tools fix most of these:

```python
s = df["load"]
s = s.str.replace("kN", "")     # .str gives text tools for a whole column
s = s.str.strip()               # remove spaces at both ends
df["load_kn"] = pd.to_numeric(s, errors="coerce")
```

`pd.to_numeric(..., errors="coerce")` converts what it can and turns anything it can't (like `"n/a"`) into `NaN`, instead of stopping with an error. Then you deal with the `NaN`s as in the first lesson.

Do the text clean-up **before** `to_numeric`, otherwise `"13kN"` would be coerced to `NaN` too and you'd lose a real value.

## Your task

Read `member_loads.csv` and add a numeric column `load_kn` made from the messy `load` column. Values that can't be read should become `NaN`.
""",
        "starter": "import pandas as pd\n\ndf = pd.read_csv(\"member_loads.csv\")\nprint(df)\n\n# clean the text, then convert into df[\"load_kn\"]\n",
        "tests": '''
import pandas as pd
import math

def test_values():
    "load_kn holds numbers, with NaN where unreadable"
    df = need("df")
    check("load_kn" in df.columns, "Add a column called load_kn.")
    v = df["load_kn"].tolist()
    want = [12.5, 13.0, None, 9.75, None, 11.0]
    for got, w, m in zip(v, want, df["member"]):
        if w is None:
            check(got is None or (isinstance(got, float) and math.isnan(got)), "%s should be NaN, got %r." % (m, got))
        else:
            check(got == w, "%s should be %r, got %r. Clean out the text before converting." % (m, w, got))
''',
        "solution": "import pandas as pd\n\ndf = pd.read_csv(\"member_loads.csv\")\nprint(df)\n\ncleaned = df[\"load\"].str.replace(\"kN\", \"\").str.strip()\ndf[\"load_kn\"] = pd.to_numeric(cleaned, errors=\"coerce\")\nprint(df)\n",
        "hints": [
            "`df[\"load\"].str.replace(\"kN\", \"\").str.strip()` gets rid of the unit and spaces.",
            "Then `pd.to_numeric(cleaned, errors=\"coerce\")`.",
        ],
    },
    {
        "id": "sanity",
        "title": "Values that can't be right",
        "kind": "code",
        "timeout": T,
        "body": """
A cube strength of 412 MPa, or of -3 MPa, isn't a measurement. It's a typing slip or a broken sensor. Statistics won't spot these for you, but engineering sense will: decide what range is **physically possible**, and flag anything outside it.

```python
ok = df["strength_mpa"].between(5, 120)     # inclusive range check
suspect = df[~ok]                            # ~ flips True and False
clean = df[ok]
```

`.between(low, high)` includes both ends. The `~` means "not", so `df[~ok]` is the rows that failed.

Flag first, look at what got flagged, and only then drop. Silently deleting data you don't like is how real problems get hidden.

## Your task

Write `split_plausible(df, column, low, high)` that returns a tuple of two DataFrames: `(good, suspect)`. `good` holds rows where `column` is between `low` and `high` inclusive, and `suspect` holds the rest.
""",
        "starter": "import pandas as pd\n\n\ndef split_plausible(df, column, low, high):\n    pass\n\n\ncubes = pd.DataFrame({\"sample\": [\"S1\", \"S2\", \"S3\", \"S4\"], \"strength_mpa\": [41.2, 412.0, 39.5, -3.0]})\ngood, suspect = split_plausible(cubes, \"strength_mpa\", 5, 120)\nprint(good)\nprint(suspect)\n",
        "tests": '''
import pandas as pd

def test_split():
    "Splits into good and suspect"
    cubes = pd.DataFrame({"sample": ["S1", "S2", "S3", "S4", "S5"], "strength_mpa": [41.2, 412.0, 39.5, -3.0, 120.0]})
    v, _ = capture(need("split_plausible"), cubes, "strength_mpa", 5, 120)
    check(isinstance(v, tuple) and len(v) == 2, "Return two DataFrames: return good, suspect.")
    good, suspect = v
    check(good["sample"].tolist() == ["S1", "S3", "S5"], "good holds %r, expected S1, S3, S5 (both ends count as good)." % good["sample"].tolist())
    check(suspect["sample"].tolist() == ["S2", "S4"], "suspect holds %r, expected S2 and S4." % suspect["sample"].tolist())
''',
        "solution": "import pandas as pd\n\n\ndef split_plausible(df, column, low, high):\n    ok = df[column].between(low, high)\n    return df[ok], df[~ok]\n\n\ncubes = pd.DataFrame({\"sample\": [\"S1\", \"S2\", \"S3\", \"S4\"], \"strength_mpa\": [41.2, 412.0, 39.5, -3.0]})\ngood, suspect = split_plausible(cubes, \"strength_mpa\", 5, 120)\nprint(good)\nprint(suspect)\n",
        "hints": [
            "`ok = df[column].between(low, high)`",
            "`return df[ok], df[~ok]`",
        ],
    },
    {
        "id": "cleaning-checklist",
        "title": "A cleaning checklist",
        "kind": "read",
        "body": """
Run through this every time a new dataset arrives, before any analysis.

1. **Look at it.** `df.head()`, `df.shape`, `df.dtypes`. Are the columns the ones you expected? Are numbers numbers?
2. **Headers and junk lines.** Notes at the top, a units row, totals at the bottom? Use `skiprows` and `skipfooter`, or slice them off.
3. **Types.** Text in a number column usually means units or notes typed into cells. Strip them, then `pd.to_numeric(..., errors="coerce")`.
4. **Missing values.** `df.isna().sum()`. Decide per column: drop, fill with a known value, or leave and let calculations skip them.
5. **Duplicates.** Decide which columns define "the same row", then `drop_duplicates(subset=...)`.
6. **Plausible ranges.** For each important column, what values are physically possible? Flag the rest, look at them, then decide.
7. **Write down what you did.** A short comment per step in the script is enough. When someone asks why the report shows 46 samples and the file had 50, you'll have the answer.

## Keep the raw data untouched

Never edit the original file. Read it, clean it in code, and write the cleaned version to a **new** file. Then if a step turns out to be wrong, you fix the code and rerun, and nothing has been lost.
""",
    },
    {
        "id": "cleaning-task",
        "title": "Chapter task: cleaning cube results",
        "kind": "code",
        "timeout": T,
        "files": {"cube_tests.csv": TESTS_CSV},
        "body": """
Every step from this chapter on one messy file. Here's the top of `cube_tests.csv`:

```
Cube test results
sample,pour,age_days,strength
-,-,days,MPa
S01,P1,7,24.5 MPa
S02,P1,7,missing
...
```

## Your task

Write `clean_cubes(path)` that returns a clean DataFrame:

1. skip the title line and the units row,
2. turn `strength` into numbers (strip any `MPa` and spaces; unreadable values become `NaN`),
3. drop rows with no strength,
4. drop repeated sample ids, keeping the first,
5. keep only strengths between 5 and 120 MPa inclusive.

Return the columns `sample`, `pour`, `age_days` and `strength`, in that order.
""",
        "starter": "import pandas as pd\n\n\ndef clean_cubes(path):\n    df = pd.read_csv(path, skiprows=[0, 2])\n    # 2. strength to numbers\n    # 3. drop missing\n    # 4. drop duplicate samples\n    # 5. plausible range\n    return df\n\n\nprint(clean_cubes(\"cube_tests.csv\"))\n",
        "tests": '''
import pandas as pd

def test_clean():
    "A clean table of valid results"
    v, _ = capture(need("clean_cubes"), "cube_tests.csv")
    check(isinstance(v, pd.DataFrame), "Return the DataFrame.")
    check(list(v.columns) == ["sample", "pour", "age_days", "strength"], "Columns are %r." % list(v.columns))
    check(pd.api.types.is_numeric_dtype(v["strength"]), "strength should be numeric.")
    check(v["sample"].tolist() == ["S01", "S03", "S04", "S05", "S07", "S08"],
          "Samples kept: %r. Expected S01, S03, S04, S05, S07, S08." % v["sample"].tolist())
    check(v["strength"].tolist()[0] == 24.5, "S01 should keep its value of 24.5 once 'MPa' is removed.")
''',
        "solution": "import pandas as pd\n\n\ndef clean_cubes(path):\n    df = pd.read_csv(path, skiprows=[0, 2])\n    cleaned = df[\"strength\"].astype(str).str.replace(\"MPa\", \"\").str.strip()\n    df[\"strength\"] = pd.to_numeric(cleaned, errors=\"coerce\")\n    df = df.dropna(subset=[\"strength\"])\n    df = df.drop_duplicates(subset=[\"sample\"])\n    df = df[df[\"strength\"].between(5, 120)]\n    return df[[\"sample\", \"pour\", \"age_days\", \"strength\"]]\n\n\nprint(clean_cubes(\"cube_tests.csv\"))\n",
        "hints": [
            "Step 2 is the `fix-types` lesson: `.str.replace(\"MPa\", \"\").str.strip()` then `pd.to_numeric(..., errors=\"coerce\")`. If pandas read some values as numbers already, add `.astype(str)` first.",
            "Steps 3 to 5: `df.dropna(subset=[\"strength\"])`, `df.drop_duplicates(subset=[\"sample\"])`, `df[df[\"strength\"].between(5, 120)]`. Reassign `df` each time.",
        ],
    },
]
