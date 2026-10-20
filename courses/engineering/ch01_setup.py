CHAPTER = {
    "title": "Setting up your tools",
    "summary": "Installing packages, importing them, virtual environments, and how to lay out a project.",
}

T = 30  # seconds: the first import of these packages can be slow

LESSONS = [
    {
        "id": "packages",
        "title": "Packages and pip",
        "kind": "read",
        "widget": "packages",
        "body": """
Everything in the Python course came with Python itself: the **standard library**. Engineering work leans on four extra **packages** written by other people and shared for free:

| Package | For |
|---|---|
| **NumPy** | fast maths on whole arrays of numbers at once |
| **pandas** | tables of data: reading CSV and Excel files, filtering, grouping |
| **matplotlib** | plots and charts |
| **SciPy** | curve fitting, integration, root finding and more |

Packages live on the **Python Package Index** (PyPI), and **pip** is the tool that downloads and installs them. In a terminal it looks like this:

```
py -m pip install numpy pandas matplotlib scipy        (Windows)
python3 -m pip install numpy pandas matplotlib scipy   (Mac)
```

Writing `-m pip` (instead of just `pip`) makes sure the packages go into the same Python you run your programs with. It saves a lot of "but I installed it!" confusion.

## The easy way

You don't need a terminal for this track. The panel below shows what's installed on this computer, and the button installs anything missing, using the same Python that runs Keystone. It needs an internet connection once. It also adds **openpyxl**, which pandas uses to read and write Excel files.
""",
    },
    {
        "id": "imports",
        "title": "Importing with a short name",
        "kind": "code",
        "timeout": T,
        "body": """
Everyone imports these packages with the same short names. You'll see them in every tutorial and every answer online, so it's worth using them too:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

`import numpy as np` loads NumPy and lets you call it `np`. After that, `np.array(...)` means `numpy.array(...)`.

Every package has a `__version__` (two underscores each side), which is handy when something behaves differently from a tutorial.

## Your task

Import NumPy as `np` and pandas as `pd`, then print their versions on two lines: NumPy's first.
""",
        "starter": "# import numpy as np and pandas as pd\n\n\n# print np.__version__, then pd.__version__\n",
        "tests": '''
import types

def test_imports():
    "np and pd are the real packages"
    check(isinstance(ns.get("np"), types.ModuleType) and ns["np"].__name__ == "numpy", "Import NumPy with: import numpy as np")
    check(isinstance(ns.get("pd"), types.ModuleType) and ns["pd"].__name__ == "pandas", "Import pandas with: import pandas as pd")

def test_print():
    "Prints both versions"
    import numpy, pandas
    check(LINES == [numpy.__version__, pandas.__version__], "Expected two lines: %s then %s. Got:\\n%s" % (numpy.__version__, pandas.__version__, OUTPUT))
''',
        "solution": "import numpy as np\nimport pandas as pd\n\nprint(np.__version__)\nprint(pd.__version__)\n",
        "hints": [
            "`import numpy as np` on one line, `import pandas as pd` on the next.",
            "`print(np.__version__)` then `print(pd.__version__)`.",
        ],
    },
    {
        "id": "alias-quiz",
        "title": "Which name?",
        "kind": "quiz",
        "body": "A slip almost everyone makes once.",
        "question": "What happens here?\n\n```python\nimport numpy as np\nx = numpy.array([1, 2, 3])\n```",
        "options": [
            "It works, numpy and np are the same thing",
            "`NameError: name 'numpy' is not defined`",
            "It makes a list instead of an array",
            "It imports NumPy a second time",
        ],
        "answer": 1,
        "explain": "`import numpy as np` only creates the name `np`. The name `numpy` was never made, so Python doesn't know it. Use `np.array(...)`.",
    },
    {
        "id": "venvs",
        "title": "Virtual environments",
        "kind": "read",
        "body": """
Install everything into one Python and sooner or later two projects need different versions of the same package. A **virtual environment** solves that: a private folder of packages for one project.

You don't need one for this track, since Keystone handles the packages. But you'll want them for your own projects, so here's the routine.

## Creating and using one

From a terminal, inside your project folder:

```
py -m venv .venv               (creates the environment, once)
.venv\\Scripts\\activate          (Windows: switch it on)
source .venv/bin/activate      (Mac: switch it on)
python -m pip install pandas   (installs into .venv only)
deactivate                     (switch it off)
```

While it's active, your terminal prompt shows `(.venv)`, and `python` and `pip` refer to the environment's own copies.

## Recording what a project needs

```
python -m pip freeze > requirements.txt     (write the list)
python -m pip install -r requirements.txt   (rebuild it elsewhere)
```

`requirements.txt` is what you share with a colleague, or check into Git, so they can recreate exactly your setup. The `.venv` folder itself is never shared. It's big, and it only works on the machine that made it.
""",
    },
    {
        "id": "venv-quiz",
        "title": "Sharing a project",
        "kind": "quiz",
        "body": "Apply the last page.",
        "question": "A colleague needs to run your analysis script. What should you send along with the script?",
        "options": [
            "Your whole `.venv` folder",
            "A `requirements.txt` listing the packages and versions",
            "Nothing, everyone has the same packages",
            "Your Python installer",
        ],
        "answer": 1,
        "explain": "`requirements.txt` lets them build their own environment with the same packages: `python -m pip install -r requirements.txt`. A `.venv` folder only works on the machine that created it.",
    },
    {
        "id": "project-layout",
        "title": "Scripts, notebooks and folders",
        "kind": "read",
        "body": """
## Scripts or notebooks?

- A **script** is a `.py` file you run from top to bottom, like the exercises here. Best for anything you'll run again: a calc tool, a report generator.
- A **notebook** (Jupyter, or VS Code's notebook mode) runs code in separate cells and shows tables and plots inline. Great for exploring a new dataset, but easy to get into a muddle because cells can run in any order.

A common habit: explore in a notebook, then move the parts that work into a script.

## A tidy project folder

```
beam-checks/
    data/              input files you were given (never edit these by hand)
    outputs/           everything your code writes: Excel, plots, reports
    beam_checks.py     your code
    requirements.txt
    README.md          two lines on what it does and how to run it
```

Keeping inputs and outputs apart means you can delete `outputs/` and regenerate it at any time, and you never accidentally overwrite the original data.

## Paths

Build file paths with `pathlib` rather than gluing strings together. It handles the `\\` versus `/` difference between Windows and Mac for you:

```python
from pathlib import Path

data_dir = Path("data")
csv_path = data_dir / "loads.csv"      # / joins path parts
print(csv_path.name)     # loads.csv
print(csv_path.stem)     # loads
print(csv_path.suffix)   # .csv
```
""",
    },
    {
        "id": "pathlib",
        "title": "Building output paths",
        "kind": "code",
        "timeout": T,
        "body": """
A small, very common job: given an input file, work out where its output should go.

```python
from pathlib import Path

def plot_path(csv_path):
    p = Path(csv_path)
    return Path("outputs") / (p.stem + "_plot.png")

print(plot_path("data/loads.csv"))   # outputs/loads_plot.png
```

`p.stem` is the file name without its extension, so you can build a new name from it.

## Your task

Write `report_path(csv_path)` that returns a `Path` inside the `outputs` folder, named after the input file's stem with `_report.xlsx` on the end.

`report_path("data/beams_level2.csv")` should give `outputs/beams_level2_report.xlsx`.
""",
        "starter": "from pathlib import Path\n\n\ndef report_path(csv_path):\n    pass\n\n\nprint(report_path(\"data/beams_level2.csv\"))\n",
        "tests": '''
from pathlib import Path

def test_paths():
    "Builds the right output path"
    f = need("report_path")
    for src, want in [("data/beams_level2.csv", "outputs/beams_level2_report.xlsx"),
                      ("loads.csv", "outputs/loads_report.xlsx"),
                      ("data/raw/gauge-04.txt", "outputs/gauge-04_report.xlsx")]:
        v, _ = capture(f, src)
        check(v is not None and Path(v).as_posix() == want, "report_path(%r) returned %r, expected %s." % (src, v, want))

def test_is_path():
    "Returns a Path"
    v, _ = capture(need("report_path"), "a.csv")
    check(isinstance(v, Path), "Return a Path object (built with Path(...) / ...), not a string.")
''',
        "solution": "from pathlib import Path\n\n\ndef report_path(csv_path):\n    p = Path(csv_path)\n    return Path(\"outputs\") / (p.stem + \"_report.xlsx\")\n\n\nprint(report_path(\"data/beams_level2.csv\"))\n",
        "hints": [
            "Same shape as `plot_path`, with a different ending.",
            "`return Path(\"outputs\") / (Path(csv_path).stem + \"_report.xlsx\")`",
        ],
    },
]
