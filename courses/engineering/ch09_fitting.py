CHAPTER = {
    "title": "Fitting data",
    "summary": "Straight-line fits, R-squared, polynomials, fitting your own equation with SciPy, and interpolating tables.",
}

T = 40

TEST_DATA = '''import numpy as np

strain = np.array([0.0, 0.0002, 0.0004, 0.0006, 0.0008, 0.0010, 0.0012])
stress = np.array([0.0, 41.0, 79.5, 121.0, 162.0, 199.0, 241.5])   # MPa
'''

LESSONS = [
    {
        "id": "polyfit",
        "title": "Fitting a straight line",
        "kind": "code",
        "timeout": T,
        "body": """
In the elastic range, stress is proportional to strain, and the slope is Young's modulus. Test data never sits exactly on a line, so you fit the **best** straight line through it:

```python
slope, intercept = np.polyfit(x, y, 1)
```

`np.polyfit(x, y, degree)` finds the polynomial of that degree that fits the points best (in the least-squares sense). Degree 1 is a straight line, `y = slope * x + intercept`. It returns the coefficients, highest power first.

## Your task

From the strain and stress test data in the starter, store `E_mpa`: the slope of the best-fit line (Young's modulus in MPa), and `intercept`.
""",
        "starter": TEST_DATA + "\n# E_mpa, intercept = ...\n",
        "tests": '''
import numpy as np

def test_fit():
    "Slope and intercept of the best line"
    strain = np.array([0.0, 0.0002, 0.0004, 0.0006, 0.0008, 0.0010, 0.0012])
    stress = np.array([0.0, 41.0, 79.5, 121.0, 162.0, 199.0, 241.5])
    s, c = np.polyfit(strain, stress, 1)
    check(np.isclose(need("E_mpa"), s), "E_mpa is %r, expected about %.0f. Is it np.polyfit(strain, stress, 1), with strain first?" % (ns.get("E_mpa"), s))
    check(np.isclose(need("intercept"), c), "intercept is %r, expected %.3f." % (ns.get("intercept"), c))
''',
        "solution": TEST_DATA + "\nE_mpa, intercept = np.polyfit(strain, stress, 1)\nprint(E_mpa, intercept)\n",
        "hints": [
            "x is strain, y is stress: `np.polyfit(strain, stress, 1)`.",
        ],
    },
    {
        "id": "r-squared",
        "title": "How good is the fit?",
        "kind": "code",
        "timeout": T,
        "body": """
**R-squared** measures how much of the scatter in `y` the fitted line explains. 1 means a perfect fit, 0 means the line explains nothing.

```python
coeffs = np.polyfit(x, y, 1)
y_fit = np.polyval(coeffs, x)          # the line's value at each x

ss_res = ((y - y_fit) ** 2).sum()      # scatter left over after the fit
ss_tot = ((y - y.mean()) ** 2).sum()   # total scatter around the mean
r2 = 1 - ss_res / ss_tot
```

`np.polyval(coeffs, x)` evaluates the fitted polynomial, which saves writing `slope * x + intercept` by hand.

## Your task

Write `r_squared(x, y)` that fits a straight line to the arrays `x` and `y` and returns its R-squared.
""",
        "starter": "import numpy as np\n\n\ndef r_squared(x, y):\n    # 1. fit a line, 2. y_fit with np.polyval, 3. ss_res and ss_tot, 4. return 1 - ss_res / ss_tot\n    pass\n\n\nx = np.array([1.0, 2.0, 3.0, 4.0, 5.0])\nprint(r_squared(x, 2 * x + 1))                              # a perfect line: 1.0\nprint(r_squared(x, np.array([2.9, 5.2, 6.8, 9.1, 11.2])))   # close to 1\n",
        "tests": '''
import numpy as np

def ref(x, y):
    c = np.polyfit(x, y, 1); f = np.polyval(c, x)
    return 1 - ((y - f) ** 2).sum() / ((y - y.mean()) ** 2).sum()

def test_values():
    "Right R-squared"
    f = need("r_squared")
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    for y in (2 * x + 1, np.array([2.9, 5.2, 6.8, 9.1, 11.2]), np.array([3.0, 1.0, 4.0, 1.0, 5.0])):
        v, _ = capture(f, x, y)
        check(v is not None and np.isclose(v, ref(x, y)), "r_squared returned %r, expected %.4f." % (v, ref(x, y)))
''',
        "solution": "import numpy as np\n\n\ndef r_squared(x, y):\n    coeffs = np.polyfit(x, y, 1)\n    y_fit = np.polyval(coeffs, x)\n    ss_res = ((y - y_fit) ** 2).sum()\n    ss_tot = ((y - y.mean()) ** 2).sum()\n    return 1 - ss_res / ss_tot\n\n\nx = np.array([1.0, 2.0, 3.0, 4.0, 5.0])\nprint(r_squared(x, 2 * x + 1))\nprint(r_squared(x, np.array([2.9, 5.2, 6.8, 9.1, 11.2])))\n",
        "hints": [
            "The four lines from the example, inside the function, then `return r2`.",
        ],
    },
    {
        "id": "r2-quiz",
        "title": "What R-squared doesn't tell you",
        "kind": "quiz",
        "body": "A high R-squared feels reassuring. It's worth knowing its limits.",
        "question": "A straight line fitted to a stress-strain curve that goes well past yield gives R-squared = 0.93. What's the right conclusion?",
        "options": [
            "The material is 93% elastic",
            "The fit is good, so the slope is Young's modulus",
            "Plot it: a curve can score highly against a straight line, and the slope will be wrong. Fit only the elastic part",
            "R-squared above 0.9 always means the model is right",
        ],
        "answer": 2,
        "explain": "R-squared only says how much scatter a line explains, not whether a line is the right shape. A curved dataset can still score 0.9 or more. Always plot the fit over the data, and fit a model only to the range where it applies.",
    },
    {
        "id": "polynomial",
        "title": "Curves with polynomials",
        "kind": "code",
        "timeout": T,
        "body": """
`np.polyfit` fits curves too. Degree 2 is a parabola `a x^2 + b x + c`:

```python
a, b, c = np.polyfit(x, y, 2)
smooth_x = np.linspace(x.min(), x.max(), 100)
smooth_y = np.polyval([a, b, c], smooth_x)     # for plotting the curve
```

Higher degrees fit the points more closely, but beyond about 3 the curve starts chasing the noise and swings wildly between and beyond the points. Use the lowest degree that captures the real shape, and **never** trust a polynomial outside the range of your data.

## Your task

Settlement readings from a load test are in the starter. Fit a degree-2 polynomial to `settlement_mm` against `load_kn`, store the coefficients as `coeffs`, and store `predicted`: the fitted settlement at a load of **250 kN**.
""",
        "starter": "import numpy as np\n\nload_kn = np.array([0, 50, 100, 150, 200, 250, 300])\nsettlement_mm = np.array([0.0, 1.2, 2.7, 4.6, 6.9, 9.4, 12.4])\n\n# coeffs = ...\n# predicted = ...\n",
        "tests": '''
import numpy as np

def test_fit():
    "Degree-2 coefficients and the prediction at 250 kN"
    x = np.array([0, 50, 100, 150, 200, 250, 300]); y = np.array([0.0, 1.2, 2.7, 4.6, 6.9, 9.4, 12.4])
    c = np.polyfit(x, y, 2)
    got = need("coeffs")
    check(len(got) == 3 and np.allclose(got, c), "coeffs should be the 3 coefficients from np.polyfit(load_kn, settlement_mm, 2).")
    check(np.isclose(need("predicted"), np.polyval(c, 250)), "predicted should be np.polyval(coeffs, 250), about %.2f." % np.polyval(c, 250))
''',
        "solution": "import numpy as np\n\nload_kn = np.array([0, 50, 100, 150, 200, 250, 300])\nsettlement_mm = np.array([0.0, 1.2, 2.7, 4.6, 6.9, 9.4, 12.4])\n\ncoeffs = np.polyfit(load_kn, settlement_mm, 2)\npredicted = np.polyval(coeffs, 250)\nprint(coeffs, predicted)\n",
        "hints": [
            "`coeffs = np.polyfit(load_kn, settlement_mm, 2)`",
            "`predicted = np.polyval(coeffs, 250)`",
        ],
    },
    {
        "id": "curve-fit",
        "title": "Fitting your own equation",
        "kind": "code",
        "timeout": T,
        "body": """
When physics gives you the shape of the curve, fit **that** equation instead of a polynomial. Consolidation settlement, for example, often follows

```
s(t) = s_final * (1 - exp(-t / tau))
```

SciPy's `curve_fit` finds the parameters. You write the model as a Python function whose **first** argument is x, followed by the unknowns:

```python
from scipy.optimize import curve_fit

def model(t, s_final, tau):
    return s_final * (1 - np.exp(-t / tau))

params, cov = curve_fit(model, t, s, p0=[50, 30])
s_final, tau = params
```

- It returns two things: the best parameters, and their covariance (a measure of uncertainty). You'll usually just unpack the first.
- `p0` is your starting guess. For curves like this, a rough guess matters: start too far off and the fit can fail or find nonsense. Read sensible values off a plot of the data.

## Your task

Fit the consolidation model to the settlement readings in the starter. Store `s_final` and `tau`. Use `p0=[50, 30]`.
""",
        "starter": "import numpy as np\nfrom scipy.optimize import curve_fit\n\nt_days = np.array([0, 5, 10, 20, 40, 60, 90, 120])\ns_mm = np.array([0.0, 6.4, 12.1, 20.8, 32.7, 39.5, 44.6, 46.9])\n\n\ndef model(t, s_final, tau):\n    return s_final * (1 - np.exp(-t / tau))\n\n\n# params, cov = curve_fit(...)\n# s_final, tau = ...\n",
        "tests": '''
import numpy as np
from scipy.optimize import curve_fit

def test_params():
    "Fitted s_final and tau"
    t = np.array([0, 5, 10, 20, 40, 60, 90, 120]); s = np.array([0.0, 6.4, 12.1, 20.8, 32.7, 39.5, 44.6, 46.9])
    p, _ = curve_fit(lambda t, a, b: a * (1 - np.exp(-t / b)), t, s, p0=[50, 30])
    check(np.isclose(need("s_final"), p[0], rtol=1e-3), "s_final is %r, expected about %.2f mm." % (ns.get("s_final"), p[0]))
    check(np.isclose(need("tau"), p[1], rtol=1e-3), "tau is %r, expected about %.2f days." % (ns.get("tau"), p[1]))
''',
        "solution": "import numpy as np\nfrom scipy.optimize import curve_fit\n\nt_days = np.array([0, 5, 10, 20, 40, 60, 90, 120])\ns_mm = np.array([0.0, 6.4, 12.1, 20.8, 32.7, 39.5, 44.6, 46.9])\n\n\ndef model(t, s_final, tau):\n    return s_final * (1 - np.exp(-t / tau))\n\n\nparams, cov = curve_fit(model, t_days, s_mm, p0=[50, 30])\ns_final, tau = params\nprint(s_final, tau)\n",
        "hints": [
            "`params, cov = curve_fit(model, t_days, s_mm, p0=[50, 30])`",
            "`s_final, tau = params`",
        ],
    },
    {
        "id": "p0-quiz",
        "title": "Starting guesses",
        "kind": "quiz",
        "body": "One question on `p0`.",
        "question": "`curve_fit` stops with \"Optimal parameters not found\". What should you try first?",
        "options": [
            "Switch to a degree-10 polynomial",
            "Plot the data and give a better `p0`, read roughly off the plot",
            "Delete the points that don't fit",
            "Increase the timeout",
        ],
        "answer": 1,
        "explain": "`curve_fit` improves a guess step by step. If the guess is far from the answer, it can wander off and give up. A plot usually shows the rough values (where the curve levels off, how fast it gets there) well enough to start from.",
    },
    {
        "id": "interp",
        "title": "Interpolating a table",
        "kind": "code",
        "timeout": T,
        "body": """
Design codes are full of tables you read between rows: "for a ratio of 1.35, the coefficient is somewhere between the values for 1.3 and 1.4". `np.interp` does straight-line interpolation:

```python
ratio = np.array([1.0, 1.2, 1.4, 1.6, 2.0])     # must be increasing
coeff = np.array([0.062, 0.074, 0.084, 0.093, 0.104])
np.interp(1.35, ratio, coeff)                   # 0.0815
```

Arguments in order: where you want a value, the table's x column, the table's y column.

> **Common slip:** asking for a value outside the table. `np.interp` doesn't warn, it just returns the end value, so `np.interp(3.0, ratio, coeff)` quietly gives 0.104. If going off the table matters (it usually does), check the range yourself first.

## Your task

Write `table_value(x, xs, ys)` that returns the interpolated value at `x`, but raises a `ValueError` if `x` is below the smallest or above the largest value in `xs`.
""",
        "starter": "import numpy as np\n\n\ndef table_value(x, xs, ys):\n    pass\n\n\nratio = np.array([1.0, 1.2, 1.4, 1.6, 2.0])\ncoeff = np.array([0.062, 0.074, 0.084, 0.093, 0.104])\nprint(table_value(1.35, ratio, coeff))   # about 0.0815\n",
        "tests": '''
import numpy as np

def test_inside():
    "Interpolates inside the table"
    f = need("table_value")
    xs = np.array([1.0, 1.2, 1.4, 1.6, 2.0]); ys = np.array([0.062, 0.074, 0.084, 0.093, 0.104])
    for x in (1.0, 1.35, 1.9, 2.0):
        v, _ = capture(f, x, xs, ys)
        check(v is not None and np.isclose(v, np.interp(x, xs, ys)), "table_value(%r, ...) returned %r, expected %r." % (x, v, np.interp(x, xs, ys)))

def test_outside():
    "Refuses values off the table"
    f = need("table_value")
    xs = np.array([1.0, 2.0]); ys = np.array([0.1, 0.2])
    for x in (0.9, 2.5):
        try:
            f(x, xs, ys)
        except ValueError:
            continue
        check(False, "table_value(%r, ...) should raise ValueError, because %r is off the table." % (x, x))
''',
        "solution": "import numpy as np\n\n\ndef table_value(x, xs, ys):\n    if x < xs.min() or x > xs.max():\n        raise ValueError(f\"{x} is outside the table ({xs.min()} to {xs.max()})\")\n    return np.interp(x, xs, ys)\n\n\nratio = np.array([1.0, 1.2, 1.4, 1.6, 2.0])\ncoeff = np.array([0.062, 0.074, 0.084, 0.093, 0.104])\nprint(table_value(1.35, ratio, coeff))\n",
        "hints": [
            "A guard first: `if x < xs.min() or x > xs.max(): raise ValueError(...)`.",
            "Then `return np.interp(x, xs, ys)`.",
        ],
    },
    {
        "id": "fit-task",
        "title": "Chapter task: Young's modulus from a full test",
        "kind": "code",
        "timeout": T,
        "body": """
The real version of the first lesson: a tensile test that goes well past yield, where only the start of the curve is elastic.

## Your task

Write `elastic_modulus(strain, stress, limit)` that:

1. keeps only the points with stress **at or below** `limit` (a mask),
2. fits a straight line to those points,
3. returns a tuple `(E, r2)`: the slope, and the R-squared of that fit, both rounded to 3 decimal places.

Using a mask means the plastic part of the curve can't drag the slope down.
""",
        "starter": "import numpy as np\n\n\ndef elastic_modulus(strain, stress, limit):\n    pass\n\n\nstrain = np.array([0, 0.0003, 0.0006, 0.0009, 0.0012, 0.002, 0.005, 0.01, 0.02])\nstress = np.array([0, 61, 119, 182, 238, 270, 281, 290, 302])\nprint(elastic_modulus(strain, stress, 250))\n",
        "tests": '''
import numpy as np

def ref(strain, stress, limit):
    m = stress <= limit
    c = np.polyfit(strain[m], stress[m], 1); f = np.polyval(c, strain[m])
    r2 = 1 - ((stress[m] - f) ** 2).sum() / ((stress[m] - stress[m].mean()) ** 2).sum()
    return round(c[0], 3), round(r2, 3)

def test_values():
    "Fits only the elastic part"
    strain = np.array([0, 0.0003, 0.0006, 0.0009, 0.0012, 0.002, 0.005, 0.01, 0.02])
    stress = np.array([0, 61, 119, 182, 238, 270, 281, 290, 302.0])
    v, _ = capture(need("elastic_modulus"), strain, stress, 250)
    want = ref(strain, stress, 250)
    check(isinstance(v, tuple) and len(v) == 2, "Return two values: return E, r2.")
    check(np.isclose(v[0], want[0]) and np.isclose(v[1], want[1]),
          "Got %r, expected about %r. Mask with stress <= limit before fitting." % (v, want))
''',
        "solution": "import numpy as np\n\n\ndef elastic_modulus(strain, stress, limit):\n    m = stress <= limit\n    x, y = strain[m], stress[m]\n    coeffs = np.polyfit(x, y, 1)\n    y_fit = np.polyval(coeffs, x)\n    r2 = 1 - ((y - y_fit) ** 2).sum() / ((y - y.mean()) ** 2).sum()\n    return round(coeffs[0], 3), round(r2, 3)\n\n\nstrain = np.array([0, 0.0003, 0.0006, 0.0009, 0.0012, 0.002, 0.005, 0.01, 0.02])\nstress = np.array([0, 61, 119, 182, 238, 270, 281, 290, 302])\nprint(elastic_modulus(strain, stress, 250))\n",
        "hints": [
            "`m = stress <= limit`, then fit `strain[m]` against `stress[m]`.",
            "R-squared is the `r_squared` lesson again, on the masked arrays.",
        ],
    },
]
