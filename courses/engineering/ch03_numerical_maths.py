CHAPTER = {
    "title": "Numerical maths",
    "summary": "Ranges of points, formulas over arrays, matrices and linear systems, floating point, and units.",
}

T = 30

LESSONS = [
    {
        "id": "linspace",
        "title": "Points along a length",
        "kind": "code",
        "timeout": T,
        "body": """
Engineering calcs constantly need "points along a beam" or "values over a range". Two ways to make them:

```python
np.linspace(0, 6, 7)     # [0. 1. 2. 3. 4. 5. 6.]   7 points from 0 to 6, both ends included
np.arange(0, 6, 1.5)     # [0.  1.5 3.  4.5]        start, stop, step; stop NOT included
```

- `linspace(start, stop, n)` gives you **n points**, ends included. Use it when you know how many points you want.
- `arange(start, stop, step)` works like `range()`. With a decimal step it can come out one point short or long because of float rounding, so `linspace` is the safer choice for decimals.

For points every `s` metres along a length `L`, the number of points is `L / s + 1` (don't forget the `+ 1` for the starting point).

## Your task

Store `x`: points every **0.5 m** along a **6 m** beam, from 0 to 6 inclusive. Use `linspace`.
""",
        "starter": "import numpy as np\n\n# x = points every 0.5 m from 0 to 6\n",
        "tests": '''
import numpy as np

def test_points():
    "13 points from 0 to 6"
    x = need("x")
    check(isinstance(x, np.ndarray), "x should be an array.")
    check(len(x) == 13 and np.allclose(x, np.arange(13) * 0.5), "x has %d points: %r. Every 0.5 m from 0 to 6 is 13 points." % (len(x), x))
    check("linspace" in CODE, "Use np.linspace.")
''',
        "solution": "import numpy as np\n\nx = np.linspace(0, 6, 13)\nprint(x)\n",
        "hints": [
            "6 / 0.5 + 1 = 13 points.",
            "`x = np.linspace(0, 6, 13)`",
        ],
    },
    {
        "id": "arange-quiz",
        "title": "The arange trap",
        "kind": "quiz",
        "body": "Worth knowing before it bites.",
        "question": "How many values does `np.arange(0, 1, 0.1)` give, and is 1.0 one of them?",
        "options": [
            "11 values, including 1.0",
            "10 values, 0.0 up to 0.9, without 1.0",
            "9 values",
            "It raises an error for a decimal step",
        ],
        "answer": 1,
        "explain": "Like `range()`, `arange` stops *before* the stop value, giving 0.0, 0.1, ... 0.9. With some decimal steps, rounding can even sneak an extra value in. If you need the end point, `np.linspace(0, 1, 11)` is exact about it.",
    },
    {
        "id": "formula-arrays",
        "title": "Formulas over arrays",
        "kind": "code",
        "timeout": T,
        "body": """
Write a formula with an array where the variable goes, and you get the answer at every point at once. The bending moment along a simply supported beam with a uniform load:

```python
w, L = 10.0, 6.0                    # kN/m, m
x = np.linspace(0, L, 61)           # every 0.1 m
M = w * x * (L - x) / 2             # kN m, at every point
print(M.max())                      # 45.0, at midspan
print(x[M.argmax()])                # 3.0
```

Using `argmax` on one array to index another, like the last line, is a pattern you'll use a lot: "where does the biggest value happen?"

## Your task

Write `shear_diagram(w, L, n)` that returns a tuple `(x, V)`: `n` points along the beam, and the shear force at each one, using `V = w * (L / 2 - x)`.
""",
        "starter": "import numpy as np\n\n\ndef shear_diagram(w, L, n):\n    # x: n points from 0 to L\n    # V: w * (L / 2 - x) at every point\n    pass\n\n\nx, V = shear_diagram(10.0, 6.0, 7)\nprint(x)\nprint(V)   # should go from 30 down to -30\n",
        "tests": '''
import numpy as np

def test_values():
    "x and V for several beams"
    f = need("shear_diagram")
    for w, L, n in [(10.0, 6.0, 7), (4.5, 8.0, 81)]:
        v, _ = capture(f, w, L, n)
        check(isinstance(v, tuple) and len(v) == 2, "Return two arrays as a tuple: return x, V.")
        x, V = v
        check(len(x) == n and np.isclose(x[0], 0) and np.isclose(x[-1], L), "x should be %d points from 0 to %r." % (n, L))
        check(np.allclose(V, w * (L / 2 - x)), "V doesn't match w * (L / 2 - x) for w=%r, L=%r." % (w, L))
''',
        "solution": "import numpy as np\n\n\ndef shear_diagram(w, L, n):\n    x = np.linspace(0, L, n)\n    V = w * (L / 2 - x)\n    return x, V\n\n\nx, V = shear_diagram(10.0, 6.0, 7)\nprint(x)\nprint(V)\n",
        "hints": [
            "`x = np.linspace(0, L, n)` then `V = w * (L / 2 - x)`.",
            "`return x, V`",
        ],
    },
    {
        "id": "matrices",
        "title": "Matrices",
        "kind": "code",
        "timeout": T,
        "body": """
A 2D array is also a **matrix**. Two operators to know:

- `A @ B` is matrix multiplication (rows times columns, the maths kind).
- `A * B` is element-by-element, which is something else entirely.

```python
A = np.array([[2, 1],
              [1, 3]])
x = np.array([1, 2])
print(A @ x)     # [4 7]: (2*1 + 1*2, 1*1 + 3*2)
print(A.T)       # the transpose: rows become columns
```

## Your task

A stiffness matrix `K` and a displacement vector `u` are given. Work out the force vector `F = K u` and store it as `F`.
""",
        "starter": "import numpy as np\n\nK = np.array([\n    [ 4.0, -2.0,  0.0],\n    [-2.0,  4.0, -2.0],\n    [ 0.0, -2.0,  2.0],\n])\nu = np.array([1.0, 2.5, 3.0])\n\n# F = ...\n",
        "tests": '''
import numpy as np

def test_F():
    "F = K @ u"
    K = np.array([[4.0, -2.0, 0.0], [-2.0, 4.0, -2.0], [0.0, -2.0, 2.0]]); u = np.array([1.0, 2.5, 3.0])
    F = need("F")
    if isinstance(F, np.ndarray) and F.shape == (3, 3):
        check(False, "F came out as a 3 x 3 matrix. That's K * u (element by element). Use K @ u.")
    check(np.allclose(F, K @ u), "F is %r, expected %r." % (F, K @ u))
''',
        "solution": "import numpy as np\n\nK = np.array([\n    [ 4.0, -2.0,  0.0],\n    [-2.0,  4.0, -2.0],\n    [ 0.0, -2.0,  2.0],\n])\nu = np.array([1.0, 2.5, 3.0])\n\nF = K @ u\nprint(F)\n",
        "hints": [
            "`F = K @ u`",
        ],
    },
    {
        "id": "solve",
        "title": "Solving linear systems",
        "kind": "code",
        "timeout": T,
        "body": """
Much of structural analysis comes down to solving `K u = F` for `u`. By hand that's tedious. NumPy does it in one call:

```python
# 2x + y = 5
#  x + 3y = 10
A = np.array([[2.0, 1.0],
              [1.0, 3.0]])
b = np.array([5.0, 10.0])
x = np.linalg.solve(A, b)
print(x)              # [1. 3.]
print(A @ x)          # [ 5. 10.]  always worth checking
```

The left-hand matrix goes first, the right-hand vector second. Multiplying back (`A @ x`) is a cheap check that you set it up right.

> Never solve by inverting (`np.linalg.inv(A) @ b`). It's slower and less accurate. `solve` is the right tool.

## Your task

Using the same `K` as last lesson, find the displacements `u` caused by the forces `F = [0, 0, 10]`. Store the answer in `u`.
""",
        "starter": "import numpy as np\n\nK = np.array([\n    [ 4.0, -2.0,  0.0],\n    [-2.0,  4.0, -2.0],\n    [ 0.0, -2.0,  2.0],\n])\nF = np.array([0.0, 0.0, 10.0])\n\n# u = ...\n\n# check: K @ u should give F back\n",
        "tests": '''
import numpy as np

def test_u():
    "u solves K u = F"
    K = np.array([[4.0, -2.0, 0.0], [-2.0, 4.0, -2.0], [0.0, -2.0, 2.0]]); F = np.array([0.0, 0.0, 10.0])
    u = need("u")
    check(np.allclose(K @ u, F), "K @ u gives %r, not F. Use np.linalg.solve(K, F)." % (K @ u,))
    check("solve(" in CODE, "Use np.linalg.solve.")
''',
        "solution": "import numpy as np\n\nK = np.array([\n    [ 4.0, -2.0,  0.0],\n    [-2.0,  4.0, -2.0],\n    [ 0.0, -2.0,  2.0],\n])\nF = np.array([0.0, 0.0, 10.0])\n\nu = np.linalg.solve(K, F)\nprint(u)\nprint(K @ u)\n",
        "hints": [
            "`u = np.linalg.solve(K, F)`",
        ],
    },
    {
        "id": "floats",
        "title": "Comparing floats",
        "kind": "code",
        "timeout": T,
        "body": """
You saw in the Python course that `0.1 + 0.2` isn't exactly `0.3`. In calculations this matters whenever you test with `==`:

```python
total = 0.1 + 0.2
print(total == 0.3)            # False
print(np.isclose(total, 0.3))  # True
```

`np.isclose(a, b)` asks "are these equal to within a tiny tolerance?". It works on whole arrays too, and `np.allclose(a, b)` asks it of every element at once. You can set the tolerance yourself: `np.isclose(a, b, atol=0.01)` allows a difference of up to 0.01.

## Your task

A node is in equilibrium when its forces add up to zero. Write `in_equilibrium(forces)` that returns `True` when the forces in the array sum to zero, allowing an absolute tolerance of `1e-6`, and `False` otherwise.

Return a plain `bool`: wrap the answer in `bool(...)`.
""",
        "starter": "import numpy as np\n\n\ndef in_equilibrium(forces):\n    pass\n\n\nprint(in_equilibrium(np.array([0.1, 0.2, -0.3])))   # should print True\n",
        "tests": '''
import numpy as np

def test_values():
    "True within tolerance, False otherwise"
    f = need("in_equilibrium")
    for arr, want in [([0.1, 0.2, -0.3], True), ([10.0, -10.0], True), ([5.0, -4.9], False), ([1e-7, 0.0], True), ([0.001], False)]:
        v, _ = capture(f, np.array(arr))
        check(v is want, "in_equilibrium(%r) returned %r, expected %r." % (arr, v, want))
''',
        "solution": "import numpy as np\n\n\ndef in_equilibrium(forces):\n    return bool(np.isclose(forces.sum(), 0.0, atol=1e-6))\n\n\nprint(in_equilibrium(np.array([0.1, 0.2, -0.3])))\n",
        "hints": [
            "`forces.sum()` is the total. Compare it with 0.0 using `np.isclose(..., atol=1e-6)`.",
            "`return bool(np.isclose(forces.sum(), 0.0, atol=1e-6))`",
        ],
    },
    {
        "id": "units",
        "title": "Keeping units straight",
        "kind": "read",
        "body": """
Python has no idea what units your numbers are in. `6` could be metres, millimetres or days. The most common bug in engineering scripts isn't a Python error at all: it's a factor of 1000.

## A routine that works

1. **Convert everything to one consistent set as soon as it comes in.** N and mm (so stresses come out in N/mm2 = MPa) is popular for member design. kN and m works well for analysis.
2. **Do all the maths in that set.**
3. **Convert to whatever the report wants only at the very end.**

## Put the unit in the name

```python
span_m = 6.0
load_kn_m = 12.5
E_mpa = 210_000
I_mm4 = 8.36e7
```

`load_kn_m * span_m ** 2 / 8` is obviously kN m. `w * L ** 2 / 8` could be anything. (The underscore in `210_000` is just a visual separator. Python ignores it.)

## Conversions worth knowing by heart

| From | To | Multiply by |
|---|---|---|
| kN | N | 1,000 |
| m | mm | 1,000 |
| kN/m | N/mm | 1 (they're the same!) |
| kN m | N mm | 1,000,000 |
| GPa | MPa (N/mm2) | 1,000 |
| cm4 | mm4 | 10,000 |

When a result looks off by a round factor of 10, 1,000 or a million, go straight to the units.

There's also a package called `pint` that attaches units to numbers and converts them for you. It's worth a look once you're comfortable, but the habits above work everywhere.
""",
    },
    {
        "id": "maths-task",
        "title": "Chapter task: midspan deflection",
        "kind": "code",
        "timeout": T,
        "body": """
A real hand calc, with mixed units coming in.

The midspan deflection of a simply supported beam under a uniform load is:

```
delta = 5 w L^4 / (384 E I)
```

## Your task

Write `deflection_mm(w_kn_m, L_m, E_gpa, I_cm4)` that returns the deflection in **mm**.

The inputs arrive in the units in their names. Convert each one to N and mm first, using the table from the last lesson, then use the formula.

As a check: `deflection_mm(10, 6, 210, 8360)` is about 9.61 mm.
""",
        "starter": "def deflection_mm(w_kn_m, L_m, E_gpa, I_cm4):\n    # 1. convert to N and mm\n    w = w_kn_m        # kN/m is already N/mm\n    L = ...           # m to mm\n    E = ...           # GPa to N/mm2\n    I = ...           # cm4 to mm4\n    # 2. the formula\n    pass\n\n\nprint(deflection_mm(10, 6, 210, 8360))   # about 9.61\n",
        "tests": '''
import math

def test_values():
    "Right deflection in mm"
    f = need("deflection_mm")
    for args in [(10, 6, 210, 8360), (25, 8, 210, 23130), (3, 4, 11, 12000)]:
        w, L, E, I = args
        want = 5 * w * (L * 1000) ** 4 / (384 * E * 1000 * I * 1e4)
        v, _ = capture(f, *args)
        check(v is not None and math.isclose(v, want, rel_tol=1e-6),
              "deflection_mm%r returned %r, expected %.3f. If you're out by a round factor, check the unit conversions." % (args, v, want))
''',
        "solution": "def deflection_mm(w_kn_m, L_m, E_gpa, I_cm4):\n    w = w_kn_m\n    L = L_m * 1000\n    E = E_gpa * 1000\n    I = I_cm4 * 10_000\n    return 5 * w * L ** 4 / (384 * E * I)\n\n\nprint(deflection_mm(10, 6, 210, 8360))\n",
        "hints": [
            "`L = L_m * 1000`, `E = E_gpa * 1000`, `I = I_cm4 * 10_000`.",
            "`return 5 * w * L ** 4 / (384 * E * I)`",
        ],
    },
]
