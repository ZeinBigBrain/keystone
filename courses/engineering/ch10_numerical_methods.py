CHAPTER = {
    "title": "Numerical methods",
    "summary": "Integrating measured data and functions, and finding roots: the answers hand methods struggle with.",
}

T = 40

LESSONS = [
    {
        "id": "trapezoid",
        "title": "Integrating measured data",
        "kind": "code",
        "timeout": T,
        "body": """
Area under a curve comes up constantly: total load from a pressure distribution, energy from a force-displacement test, volume from cross-section areas along a cutting.

When you only have **measured points**, the trapezoidal rule joins them with straight lines and adds up the trapezoids:

```python
from scipy.integrate import trapezoid

x = np.array([0, 1, 2, 3, 4])          # m
p = np.array([0, 4, 6, 7, 7.5])        # kPa
area = trapezoid(p, x)                 # kN/m: y values first, then x
```

Note the order: **y first, then x**. Swap them and you get a different (wrong) number with no error.

## Your task

A wind pressure survey up the face of a building gave the readings in the starter. Store `force_kn_per_m`: the total force per metre width, the area under pressure (kPa) against height (m).
""",
        "starter": "import numpy as np\nfrom scipy.integrate import trapezoid\n\nheight_m = np.array([0, 5, 10, 15, 20, 25, 30])\npressure_kpa = np.array([0.62, 0.71, 0.80, 0.87, 0.92, 0.97, 1.01])\n\n# force_kn_per_m = ...\n",
        "tests": '''
import numpy as np

def test_area():
    "Area under the pressure profile"
    h = np.array([0, 5, 10, 15, 20, 25, 30]); p = np.array([0.62, 0.71, 0.80, 0.87, 0.92, 0.97, 1.01])
    want = float(((p[1:] + p[:-1]) / 2 * np.diff(h)).sum())
    got = need("force_kn_per_m")
    check(np.isclose(got, want), "force_kn_per_m is %r, expected about %.3f. The order is trapezoid(pressure, height)." % (got, want))
''',
        "solution": "import numpy as np\nfrom scipy.integrate import trapezoid\n\nheight_m = np.array([0, 5, 10, 15, 20, 25, 30])\npressure_kpa = np.array([0.62, 0.71, 0.80, 0.87, 0.92, 0.97, 1.01])\n\nforce_kn_per_m = trapezoid(pressure_kpa, height_m)\nprint(force_kn_per_m)\n",
        "hints": [
            "`trapezoid(pressure_kpa, height_m)`: y values first.",
        ],
    },
    {
        "id": "quad",
        "title": "Integrating a function",
        "kind": "code",
        "timeout": T,
        "body": """
When you have a **formula** rather than points, `quad` integrates it accurately:

```python
from scipy.integrate import quad

def load(x):
    return 12 * np.sin(np.pi * x / 6)     # kN/m along a 6 m beam

total, err = quad(load, 0, 6)              # function, lower limit, upper limit
print(total)                               # 45.84 kN
```

You pass the function itself (no brackets after `load`) and the limits. `quad` returns **two** numbers: the answer and an estimate of its error. Unpack them, or you'll be carrying a tuple around.

## Your task

A triangular-ish load on a 5 m beam follows `w(x) = 8 * x * (5 - x) / 5` kN/m. Store `total_kn`: its integral from 0 to 5. Store the error estimate as `err`.
""",
        "starter": "import numpy as np\nfrom scipy.integrate import quad\n\n\ndef w(x):\n    return 8 * x * (5 - x) / 5\n\n\n# total_kn, err = ...\n",
        "tests": '''
import numpy as np

def test_total():
    "Integral of w from 0 to 5"
    t = need("total_kn")
    check(not isinstance(t, tuple), "total_kn is a tuple. quad returns (value, error), so unpack it: total_kn, err = quad(...).")
    check(np.isclose(t, 8 * (5 * 25 / 2 - 125 / 3) / 5), "total_kn is %r, expected about 33.33." % (t,))
    check(need("err") < 1e-6, "err should be quad's (tiny) error estimate.")
''',
        "solution": "import numpy as np\nfrom scipy.integrate import quad\n\n\ndef w(x):\n    return 8 * x * (5 - x) / 5\n\n\ntotal_kn, err = quad(w, 0, 5)\nprint(total_kn, err)\n",
        "hints": [
            "`total_kn, err = quad(w, 0, 5)`. Pass `w` without brackets.",
        ],
    },
    {
        "id": "quad-quiz",
        "title": "Passing a function",
        "kind": "quiz",
        "body": "A small detail that matters a lot.",
        "question": "What's wrong with `quad(w(x), 0, 5)`?",
        "options": [
            "Nothing",
            "`w(x)` calls the function straight away and passes its result; `quad` needs the function itself, `w`",
            "The limits must be floats",
            "quad only works with lambda functions",
        ],
        "answer": 1,
        "explain": "`quad` wants something it can call itself, many times, at points it chooses. `w` is the function; `w(x)` is one value (and here `x` probably isn't even defined). The same goes for `curve_fit`, `brentq`, and `sorted(key=...)`.",
    },
    {
        "id": "brentq",
        "title": "Finding a root",
        "kind": "code",
        "timeout": T,
        "body": """
Lots of design questions are "find the value that makes this equal that": the depth where forces balance, the span where deflection hits its limit. Rearrange it so one side is zero, and you're looking for a **root**: where `f(x) = 0`.

`brentq` finds one, given a **bracket**: two x values where `f` has opposite signs. A smooth function that's negative at one end and positive at the other must cross zero in between.

```python
from scipy.optimize import brentq

def f(d):                       # how far off balance at depth d
    return 0.5 * d ** 2 - 8

d = brentq(f, 0, 10)            # f(0) = -8, f(10) = 42: opposite signs
print(d)                        # 4.0
```

If both ends have the **same** sign, `brentq` stops with `ValueError: f(a) and f(b) must have different signs`. Evaluate `f` at a few points (or plot it) to find a bracket that works.

## Your task

A simplified model gives a cantilever's tip deflection as `delta(L) = 0.0004 * L ** 3`. The numbers are made up, but the shape (deflection growing with the cube of the span) is real. Find the value of `L` between 1 and 100 where the deflection equals **50**. Store it in `L_limit`.

Write `f(L)` so that it's zero at the answer: deflection minus 50.
""",
        "starter": "from scipy.optimize import brentq\n\n\ndef delta(L):\n    return 0.0004 * L ** 3\n\n\ndef f(L):\n    # zero when delta(L) is 50\n    pass\n\n\n# L_limit = brentq(f, ..., ...)\n",
        "tests": '''
import numpy as np

def test_root():
    "Span where deflection is 50"
    L = need("L_limit")
    check(np.isclose(0.0004 * L ** 3, 50, rtol=1e-6), "At L_limit = %r the deflection is %r, not 50." % (L, 0.0004 * L ** 3))
    check("brentq(" in CODE, "Use brentq.")
''',
        "solution": "from scipy.optimize import brentq\n\n\ndef delta(L):\n    return 0.0004 * L ** 3\n\n\ndef f(L):\n    return delta(L) - 50\n\n\nL_limit = brentq(f, 1, 100)\nprint(L_limit)\n",
        "hints": [
            "`return delta(L) - 50`",
            "`L_limit = brentq(f, 1, 100)`. f(1) is negative and f(100) is positive, so that's a valid bracket.",
        ],
    },
    {
        "id": "numerical-task",
        "title": "Chapter task: the longest span that passes",
        "kind": "code",
        "timeout": T,
        "body": """
Root finding on a real check. Deflection limits are usually span/360: the longer the span, the larger the allowed deflection, but the actual deflection grows much faster.

## Your task

Write `max_span_m(w_kn_m, E_mpa, I_mm4)` that returns the longest simply supported span (in **metres**, rounded to 3 decimal places) for which the midspan deflection `5 w L^4 / (384 E I)` equals exactly `L / 360`.

Work in N and mm inside the function (`w` in kN/m is already N/mm). Search for the span in mm between 100 and 50,000.

As a check: `max_span_m(10, 210_000, 8.36e7)` is about 6.866.
""",
        "starter": "from scipy.optimize import brentq\n\n\ndef max_span_m(w_kn_m, E_mpa, I_mm4):\n    def f(L_mm):\n        # actual deflection minus the allowed one\n        pass\n\n    pass\n\n\nprint(max_span_m(10, 210_000, 8.36e7))\n",
        "tests": '''
import numpy as np

def ref(w, E, I):
    # 5 w L^4 / (384 E I) = L / 360  ->  L^3 = 384 E I / (1800 w)
    return round((384 * E * I / (1800 * w)) ** (1 / 3) / 1000, 3)

def test_values():
    "Longest passing span"
    f = need("max_span_m")
    for args in [(10, 210000, 8.36e7), (25, 210000, 2.313e8), (4, 11000, 3.6e8)]:
        v, _ = capture(f, *args)
        check(v is not None and abs(v - ref(*args)) <= 0.0011, "max_span_m%r returned %r, expected %r." % (args, v, ref(*args)))
''',
        "solution": "from scipy.optimize import brentq\n\n\ndef max_span_m(w_kn_m, E_mpa, I_mm4):\n    def f(L_mm):\n        actual = 5 * w_kn_m * L_mm ** 4 / (384 * E_mpa * I_mm4)\n        allowed = L_mm / 360\n        return actual - allowed\n\n    L_mm = brentq(f, 100, 50_000)\n    return round(L_mm / 1000, 3)\n\n\nprint(max_span_m(10, 210_000, 8.36e7))\n",
        "hints": [
            "Inside `f`: `actual = 5 * w_kn_m * L_mm ** 4 / (384 * E_mpa * I_mm4)` and `allowed = L_mm / 360`, then `return actual - allowed`.",
            "`L_mm = brentq(f, 100, 50_000)`, then `return round(L_mm / 1000, 3)`.",
        ],
    },
    {
        "id": "check-numerics",
        "title": "Trusting a numerical answer",
        "kind": "read",
        "body": """
Numerical methods give an answer to many decimal places, which makes it look more certain than it is. Before a number goes in a report, give it the same checks you'd give a colleague's hand calc.

## Order of magnitude

Estimate it roughly first. A floor load of 5 kPa over 40 m2 is about 200 kN. If the code says 200,000, it's units, not engineering.

## A case you know the answer to

Run the same code on a problem with a textbook answer. Integrate a uniform load and you should get `w L`. Find the root of `x**2 - 4` and you should get 2. If the simple case is wrong, the real one is too.

## Look at it

Plot the function before you integrate or root-find it. Spikes, gaps, or more than one crossing all change what the method will do.

## Check the fit or the bracket

- After `curve_fit`, plot the fitted curve over the data.
- After `brentq`, put the answer back into `f` and confirm it's close to zero.
- After `np.linalg.solve`, check `A @ x` against `b`.

## Sensitivity

Nudge an input by a few percent and rerun. If the answer jumps wildly, the problem is sensitive (or the method is struggling), and that's worth knowing before anyone relies on it.
""",
    },
]
