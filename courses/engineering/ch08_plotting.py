CHAPTER = {
    "title": "Plotting with matplotlib",
    "summary": "Line and scatter plots, labels with units, legends, several plots in one figure, and saving figures for reports.",
}

T = 60  # the very first matplotlib import on a computer can take a while

BEAM = '''import numpy as np
import matplotlib.pyplot as plt

w, L = 10.0, 6.0
x = np.linspace(0, L, 61)
M = w * x * (L - x) / 2
'''

LESSONS = [
    {
        "id": "first-plot",
        "title": "Your first plot",
        "kind": "code",
        "timeout": T,
        "body": """
matplotlib draws onto a **figure** (the whole image) containing one or more **axes** (each individual plot). The standard way to start:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()      # one figure with one set of axes
ax.plot(x, y)                 # a line through the points
fig.savefig("my_plot.png")    # write it to a file
```

`ax.plot(x, y)` takes two arrays (or lists) of the same length: x values and y values.

In Keystone, plots aren't shown in a window. They're saved to a file and the checks look at the figure itself. Files you save with **Run** land in the app's `data/sandbox` folder if you want to open them. In your own scripts, `plt.show()` opens a window.

## Your task

The starter works out the bending moment `M` along a beam at the points `x`. Plot `M` against `x` on axes called `ax` (in a figure called `fig`), and save it as `moment.png`.
""",
        "starter": BEAM + "\n# fig, ax = ...\n# plot M against x\n# save as moment.png\n",
        "tests": '''
import numpy as np
import os

def test_plot():
    "One line of M against x"
    ax = need("ax")
    lines = ax.get_lines()
    check(len(lines) == 1, "The axes have %d lines, expected 1." % len(lines))
    xd, yd = lines[0].get_xdata(), lines[0].get_ydata()
    check(np.allclose(xd, need("x")) and np.allclose(yd, need("M")), "The line should be ax.plot(x, M): x first, then M.")

def test_saved():
    "Saved as moment.png"
    check(os.path.exists("moment.png"), "Save the figure with fig.savefig(\\"moment.png\\").")
''',
        "solution": BEAM + "\nfig, ax = plt.subplots()\nax.plot(x, M)\nfig.savefig(\"moment.png\")\n",
        "hints": [
            "`fig, ax = plt.subplots()` then `ax.plot(x, M)`.",
            "`fig.savefig(\"moment.png\")`",
        ],
    },
    {
        "id": "labels",
        "title": "Labels, units and a title",
        "kind": "code",
        "timeout": T,
        "body": """
A plot without axis labels is a plot nobody else can read. For engineering work, every axis label carries its **unit**.

```python
ax.set_xlabel("Position along beam (m)")
ax.set_ylabel("Bending moment (kN m)")
ax.set_title("Simply supported beam, w = 10 kN/m")
ax.grid(True)
```

Put the unit in brackets at the end of the label. It's the convention in most reports and journals.

## Your task

Plot `M` against `x` again, then give the plot:

- an x label containing `(m)`
- a y label containing `(kN m)`
- any title
- a grid
""",
        "starter": BEAM + "\nfig, ax = plt.subplots()\nax.plot(x, M)\n\n# labels, title and grid here\n",
        "tests": '''
def test_labels():
    "Axis labels with units"
    ax = need("ax")
    check("(m)" in ax.get_xlabel(), "The x label should end with the unit (m). It's %r." % ax.get_xlabel())
    check("(kN m)" in ax.get_ylabel(), "The y label should include the unit (kN m). It's %r." % ax.get_ylabel())

def test_title_grid():
    "A title and a grid"
    ax = need("ax")
    check(ax.get_title().strip() != "", "Add a title with ax.set_title(...).")
    check(any(l.get_visible() for l in ax.get_xgridlines()), "Turn the grid on with ax.grid(True).")
''',
        "solution": BEAM + "\nfig, ax = plt.subplots()\nax.plot(x, M)\n\nax.set_xlabel(\"Position along beam (m)\")\nax.set_ylabel(\"Bending moment (kN m)\")\nax.set_title(\"Simply supported beam, w = 10 kN/m\")\nax.grid(True)\n",
        "hints": [
            "`ax.set_xlabel(\"Position along beam (m)\")` and `ax.set_ylabel(\"Bending moment (kN m)\")`.",
            "`ax.set_title(...)` and `ax.grid(True)`.",
        ],
    },
    {
        "id": "scatter-legend",
        "title": "Measured versus predicted",
        "kind": "code",
        "timeout": T,
        "body": """
Measured data is usually drawn as **points**, and theory as a **line**, so they're easy to tell apart. Give each one a `label`, then call `ax.legend()` to show the key:

```python
ax.scatter(load, measured, label="Measured")
ax.plot(load, predicted, label="Predicted", color="black")
ax.legend()
```

`ax.scatter` takes x and y just like `ax.plot`. Other handy options: `marker="o"`, `linestyle="--"`, `color="tab:red"`.

## Your task

Plot the measured deflections as points labelled `Measured`, and the predicted deflections as a line labelled `Predicted`, both against `load_kn`. Show a legend, and label both axes with units: kN and mm.
""",
        "starter": "import numpy as np\nimport matplotlib.pyplot as plt\n\nload_kn = np.array([0, 10, 20, 30, 40, 50])\nmeasured_mm = np.array([0.0, 1.1, 2.3, 3.2, 4.6, 5.5])\npredicted_mm = load_kn * 0.11\n\nfig, ax = plt.subplots()\n# points, line, legend, labels\n",
        "tests": '''
import numpy as np

def test_series():
    "Points for measured, a line for predicted"
    ax = need("ax")
    check(len(ax.collections) >= 1, "Draw the measured values with ax.scatter(...).")
    lines = ax.get_lines()
    check(len(lines) >= 1 and np.allclose(lines[0].get_ydata(), need("predicted_mm")), "Draw predicted_mm with ax.plot(...).")

def test_legend():
    "Legend shows Measured and Predicted"
    leg = need("ax").get_legend()
    check(leg is not None, "Call ax.legend() after plotting.")
    texts = sorted(t.get_text() for t in leg.get_texts())
    check(texts == ["Measured", "Predicted"], "The legend shows %r. Give each series a label=..." % texts)

def test_labels():
    "Axis labels with units"
    ax = need("ax")
    check("kN" in ax.get_xlabel() and "mm" in ax.get_ylabel(), "Label the axes with their units: load in kN, deflection in mm.")
''',
        "solution": "import numpy as np\nimport matplotlib.pyplot as plt\n\nload_kn = np.array([0, 10, 20, 30, 40, 50])\nmeasured_mm = np.array([0.0, 1.1, 2.3, 3.2, 4.6, 5.5])\npredicted_mm = load_kn * 0.11\n\nfig, ax = plt.subplots()\nax.scatter(load_kn, measured_mm, label=\"Measured\")\nax.plot(load_kn, predicted_mm, label=\"Predicted\", color=\"black\")\nax.legend()\nax.set_xlabel(\"Load (kN)\")\nax.set_ylabel(\"Deflection (mm)\")\n",
        "hints": [
            "`ax.scatter(load_kn, measured_mm, label=\"Measured\")` and `ax.plot(load_kn, predicted_mm, label=\"Predicted\")`.",
            "Then `ax.legend()`, and the two `set_xlabel` / `set_ylabel` lines.",
        ],
    },
    {
        "id": "ax-quiz",
        "title": "plt or ax?",
        "kind": "quiz",
        "body": """
Online you'll see two styles:

```python
plt.plot(x, y)          # "pyplot" style: draws on whatever plot is current
plt.xlabel("x (m)")

fig, ax = plt.subplots()
ax.plot(x, y)           # "axes" style: you say exactly which plot
ax.set_xlabel("x (m)")
```

Both work for a single plot.
""",
        "question": "Why does this course use `fig, ax = plt.subplots()` and `ax.` everywhere?",
        "options": [
            "pyplot style is deprecated and will stop working",
            "With several plots in one figure, `ax.` says exactly which one you're drawing on, so nothing lands in the wrong place",
            "It draws faster",
            "Only the `ax` style can save files",
        ],
        "answer": 1,
        "explain": "`plt.` commands act on the \"current\" plot, which gets confusing once a figure has several. Naming the axes removes the guesswork. Note the method names differ a little: `plt.xlabel` versus `ax.set_xlabel`.",
    },
    {
        "id": "subplots",
        "title": "Several plots in one figure",
        "kind": "code",
        "timeout": T,
        "body": """
`plt.subplots(rows, cols)` makes a grid of axes. With two rows and one column, you get two axes back, which you can unpack straight away:

```python
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))
ax1.plot(x, V)
ax1.set_ylabel("Shear (kN)")
ax2.plot(x, M)
ax2.set_ylabel("Moment (kN m)")
ax2.set_xlabel("Position (m)")     # only the bottom one needs an x label
fig.tight_layout()                 # stops labels overlapping
```

`sharex=True` gives both plots the same x axis, which is exactly what you want for shear and moment diagrams drawn one above the other.

## Your task

Draw the shear force `V` on top and the bending moment `M` underneath, sharing the x axis. Call the axes `ax1` and `ax2`. Label both y axes with units, and the bottom x axis.
""",
        "starter": BEAM + "V = w * (L / 2 - x)\n\n# fig, (ax1, ax2) = ...\n",
        "tests": '''
import numpy as np

def test_layout():
    "Two plots, one above the other"
    ax1, ax2 = need("ax1"), need("ax2")
    fig = need("fig")
    check(len(fig.axes) == 2, "The figure should have 2 axes.")
    check(ax1.get_position().y0 > ax2.get_position().y0, "ax1 should be on top. Use plt.subplots(2, 1, ...).")

def test_data():
    "V on top, M below"
    ax1, ax2 = need("ax1"), need("ax2")
    check(ax1.get_lines() and np.allclose(ax1.get_lines()[0].get_ydata(), need("V")), "Plot V on ax1.")
    check(ax2.get_lines() and np.allclose(ax2.get_lines()[0].get_ydata(), need("M")), "Plot M on ax2.")

def test_labels():
    "Labelled with units"
    ax1, ax2 = need("ax1"), need("ax2")
    check("kN" in ax1.get_ylabel() and "kN" in ax2.get_ylabel(), "Give both y axes a label with units (kN and kN m).")
    check("(m)" in ax2.get_xlabel(), "Label the bottom x axis, e.g. Position (m).")
''',
        "solution": BEAM + "V = w * (L / 2 - x)\n\nfig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))\nax1.plot(x, V)\nax1.set_ylabel(\"Shear (kN)\")\nax2.plot(x, M)\nax2.set_ylabel(\"Moment (kN m)\")\nax2.set_xlabel(\"Position (m)\")\nfig.tight_layout()\n",
        "hints": [
            "Copy the example: it's almost exactly the task.",
        ],
    },
    {
        "id": "saving",
        "title": "Figures for reports",
        "kind": "code",
        "timeout": T,
        "body": """
A figure that looks fine on screen can come out blurry or cramped in a report. Three settings fix most of it:

```python
fig, ax = plt.subplots(figsize=(6, 4))      # width, height in inches
...
fig.savefig("figure.png", dpi=200, bbox_inches="tight")
```

- `figsize`: set it to the size it'll be printed. Then text comes out at a sensible size, not shrunk.
- `dpi`: dots per inch. 150 to 300 for reports.
- `bbox_inches="tight"`: trims empty margins so labels aren't cut off.

Saving as `.pdf` or `.svg` instead of `.png` gives vector graphics that stay sharp at any zoom, which is best for documents.

## Your task

Make a figure 6 inches wide and 4 inches tall, plot `M` against `x` with labelled axes, and save it **twice**: as `moment_report.png` at 200 dpi, and as `moment_report.pdf`. Use `bbox_inches="tight"` for both.
""",
        "starter": BEAM + "\n# fig, ax = plt.subplots(figsize=...)\n",
        "tests": '''
import os

def test_size():
    "6 by 4 inches"
    w, h = need("fig").get_size_inches()
    check(abs(w - 6) < 0.01 and abs(h - 4) < 0.01, "The figure is %.1f x %.1f inches. Use figsize=(6, 4)." % (w, h))

def test_files():
    "Saved as PNG and PDF"
    check(os.path.exists("moment_report.png"), "Save moment_report.png.")
    check(os.path.exists("moment_report.pdf"), "Save moment_report.pdf as well.")
    check("dpi=200" in CODE.replace(" ", ""), "Save the PNG with dpi=200.")
    check("tight" in CODE, "Use bbox_inches=\\"tight\\".")

def test_labels():
    "Axes labelled"
    ax = need("ax")
    check(ax.get_xlabel() and ax.get_ylabel(), "Label both axes.")
''',
        "solution": BEAM + "\nfig, ax = plt.subplots(figsize=(6, 4))\nax.plot(x, M)\nax.set_xlabel(\"Position (m)\")\nax.set_ylabel(\"Bending moment (kN m)\")\nfig.savefig(\"moment_report.png\", dpi=200, bbox_inches=\"tight\")\nfig.savefig(\"moment_report.pdf\", bbox_inches=\"tight\")\n",
        "hints": [
            "`fig, ax = plt.subplots(figsize=(6, 4))`",
            "Two `fig.savefig(...)` lines with different file names. Add `dpi=200` to the PNG one.",
        ],
    },
    {
        "id": "bar",
        "title": "Bar charts from pandas",
        "kind": "code",
        "timeout": T,
        "body": """
For totals per category, a bar chart reads better than a line. With a pandas result, pass the labels and the values:

```python
totals = df.groupby("site")["qty"].sum()
fig, ax = plt.subplots()
ax.bar(totals.index, totals.values)
ax.set_ylabel("Quantity (t)")
```

`totals.index` holds the group names and `totals.values` the numbers. Use `ax.barh(...)` for horizontal bars, which suit long labels.

## Your task

Draw a bar chart of the total spend per material from the `spend` Series in the starter, with a y label containing `SAR`. Sort the bars from biggest to smallest first (`spend.sort_values(ascending=False)`).
""",
        "starter": "import pandas as pd\nimport matplotlib.pyplot as plt\n\nspend = pd.Series({\"cement\": 3607.5, \"sand\": 2115.0, \"gravel\": 2080.0, \"rebar\": 30975.0})\n\n# sort, then fig, ax = ..., ax.bar(...)\n",
        "tests": '''
def test_bars():
    "Bars sorted biggest first"
    ax = need("ax")
    heights = [p.get_height() for p in ax.patches]
    check(len(heights) == 4, "Expected 4 bars, found %d. Use ax.bar(...)." % len(heights))
    check(heights == sorted(heights, reverse=True), "Sort the bars biggest first before plotting.")
    labels = [t.get_text() for t in ax.get_xticklabels()]
    check(labels[:1] == ["rebar"], "The first bar should be rebar. Pass the material names as the x values.")
    check("SAR" in ax.get_ylabel(), "Label the y axis with the unit, SAR.")
''',
        "solution": "import pandas as pd\nimport matplotlib.pyplot as plt\n\nspend = pd.Series({\"cement\": 3607.5, \"sand\": 2115.0, \"gravel\": 2080.0, \"rebar\": 30975.0})\n\nspend = spend.sort_values(ascending=False)\nfig, ax = plt.subplots()\nax.bar(spend.index, spend.values)\nax.set_ylabel(\"Spend (SAR)\")\n",
        "hints": [
            "`spend = spend.sort_values(ascending=False)` first.",
            "`ax.bar(spend.index, spend.values)` and `ax.set_ylabel(\"Spend (SAR)\")`.",
        ],
    },
    {
        "id": "plot-task",
        "title": "Chapter task: a stress-strain plot",
        "kind": "code",
        "timeout": T,
        "body": """
A figure good enough to go straight into a lab report.

Two extras you'll want:

```python
ax.axhline(275, color="grey", linestyle="--", label="Yield (275 MPa)")   # a horizontal line across the plot
ax.annotate("Yield", xy=(0.0014, 275), xytext=(0.004, 200),
            arrowprops={"arrowstyle": "->"})                                # a label with an arrow
```

## Your task

Write `stress_strain_plot(strain, stress, fy, path)` that:

1. makes a 6 by 4 inch figure,
2. plots stress against strain as a line labelled `Test`,
3. adds a dashed horizontal line at `fy` labelled `Yield`,
4. labels the axes `Strain (-)` and `Stress (MPa)`,
5. shows a legend,
6. saves to `path` with `bbox_inches="tight"`,
7. returns the figure.
""",
        "starter": "import numpy as np\nimport matplotlib.pyplot as plt\n\n\ndef stress_strain_plot(strain, stress, fy, path):\n    pass\n\n\nstrain = np.linspace(0, 0.02, 41)\nstress = np.minimum(strain * 200_000, 275 + (strain - 0.001375).clip(0) * 2000)\nstress_strain_plot(strain, stress, 275, \"stress_strain.png\")\n",
        "tests": '''
import numpy as np
import os

def test_figure():
    "Figure with the test curve, yield line, labels and legend"
    strain = np.linspace(0, 0.02, 11); stress = np.minimum(strain * 200000, 300.0)
    fig, _ = capture(need("stress_strain_plot"), strain, stress, 300, "ks_ss_test.png")
    check(fig is not None and hasattr(fig, "axes"), "Return the figure.")
    ax = fig.axes[0]
    w, h = fig.get_size_inches()
    check(abs(w - 6) < 0.01 and abs(h - 4) < 0.01, "Use figsize=(6, 4).")
    lines = ax.get_lines()
    check(any(np.allclose(l.get_ydata(), stress) for l in lines if len(l.get_ydata()) == len(stress)), "Plot stress against strain.")
    check(any(l.get_linestyle() == "--" and np.allclose(l.get_ydata(), 300) for l in lines), "Add a dashed horizontal line at fy with ax.axhline(fy, linestyle=\\"--\\").")
    check(ax.get_xlabel() == "Strain (-)" and ax.get_ylabel() == "Stress (MPa)", "Axis labels should be exactly 'Strain (-)' and 'Stress (MPa)'.")
    leg = ax.get_legend()
    check(leg is not None and sorted(t.get_text() for t in leg.get_texts()) == ["Test", "Yield"], "Show a legend with Test and Yield.")
    check(os.path.exists("ks_ss_test.png"), "Save the figure to path.")
    os.remove("ks_ss_test.png")
''',
        "solution": "import numpy as np\nimport matplotlib.pyplot as plt\n\n\ndef stress_strain_plot(strain, stress, fy, path):\n    fig, ax = plt.subplots(figsize=(6, 4))\n    ax.plot(strain, stress, label=\"Test\")\n    ax.axhline(fy, color=\"grey\", linestyle=\"--\", label=\"Yield\")\n    ax.set_xlabel(\"Strain (-)\")\n    ax.set_ylabel(\"Stress (MPa)\")\n    ax.legend()\n    fig.savefig(path, bbox_inches=\"tight\")\n    return fig\n\n\nstrain = np.linspace(0, 0.02, 41)\nstress = np.minimum(strain * 200_000, 275 + (strain - 0.001375).clip(0) * 2000)\nstress_strain_plot(strain, stress, 275, \"stress_strain.png\")\n",
        "hints": [
            "Each numbered step is one line, in order, inside the function.",
            "`ax.axhline(fy, linestyle=\"--\", label=\"Yield\")` draws the yield line.",
        ],
    },
]
