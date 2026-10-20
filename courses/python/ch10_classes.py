CHAPTER = {
    "title": "Classes and objects",
    "summary": "Bundling data with the functions that use it: classes, methods, __str__ and inheritance.",
}

LESSONS = [
    {
        "id": "why-classes",
        "title": "Why classes exist",
        "kind": "read",
        "body": """
So far, data and the functions that work on it have lived separately. You pass a dict into a function, it returns something. That works, but as programs grow you end up passing the same bundle of values around everywhere, and it gets hard to remember which functions go with which data.

A **class** lets you define your own type that holds its data and its functions together.

```python
class Tank:
    def __init__(self, capacity):
        self.capacity = capacity
        self.level = 0

    def fill(self, litres):
        self.level += litres

t = Tank(1000)      # make a Tank object
t.fill(250)
print(t.level)      # 250
```

A few terms:

- The **class** (`Tank`) is the blueprint.
- An **object** or **instance** (`t`) is one thing built from it. You can make as many as you like, each with its own data.
- **Attributes** (`capacity`, `level`) are the data stored on an object.
- **Methods** (`fill`) are functions that belong to the class.

## About self

`__init__` runs automatically when you create an object. It's where you set up its starting attributes.

Every method's first parameter is `self`, which is the object the method was called on. When you write `t.fill(250)`, Python actually calls `Tank.fill(t, 250)`, so inside the method `self` is `t`. You never pass `self` yourself.

Class names use CapitalisedWords by convention (`Tank`, `SiteDiary`), unlike the snake_case used for variables and functions.

You've been using objects all along, by the way. Every string and list is one, and `.upper()` and `.append()` are methods.
""",
    },
    {
        "id": "class-beam",
        "title": "Your first class",
        "kind": "code",
        "body": """
Start small: a class that stores two values and has one method that works something out from them.

```python
class Slab:
    def __init__(self, area_m2, kn_per_m2):
        self.area_m2 = area_m2          # store each value on the object
        self.kn_per_m2 = kn_per_m2

    def total_load(self):
        return self.area_m2 * self.kn_per_m2

s = Slab(20, 5)
print(s.total_load())    # 100
print(s.area_m2)         # 20
```

Inside a method, everything belonging to the object is reached through `self`. The parameters of `__init__` only exist while `__init__` runs, which is why each one is copied onto `self` straight away.

> **Common slips:**
> - Forgetting `self` as the first parameter: `def total_load():` gives a `TypeError` when you call it.
> - Writing `area_m2` instead of `self.area_m2` inside a method. Outside `__init__` there's no plain `area_m2`, so you get a `NameError`.
> - Calling a method without brackets. `s.total_load` is the method itself. `s.total_load()` runs it.

## Your task

Write a class `Beam`:

- `Beam(span_m, udl_kn_m)` stores both values as `self.span_m` and `self.udl_kn_m`.
- `max_moment()` returns the maximum bending moment for a simply supported beam: load times span squared, divided by 8.

So `Beam(6, 10).max_moment()` returns `45.0`.
""",
        "starter": "class Beam:\n    def __init__(self, span_m, udl_kn_m):\n        # store both values on self\n        pass\n\n    def max_moment(self):\n        # return udl * span squared / 8, using the values on self\n        pass\n\n\nb = Beam(6, 10)\nprint(b.max_moment())   # should print 45.0\n",
        "tests": '''
def test_init():
    "Stores span_m and udl_kn_m"
    b = need("Beam")(6, 10)
    check(getattr(b, "span_m", None) == 6, "Beam(6, 10).span_m should be 6. Store it with self.span_m = span_m.")
    check(getattr(b, "udl_kn_m", None) == 10, "Beam(6, 10).udl_kn_m should be 10.")

def test_moment():
    "max_moment returns wL squared over 8"
    B = need("Beam")
    for args, want in [((6, 10), 45.0), ((4, 12.5), 25.0), ((8, 0), 0)]:
        v, _ = capture(B(*args).max_moment)
        check(v is not None and abs(v - want) < 1e-9, "Beam%r.max_moment() returned %r, expected %r." % (args, v, want))
''',
        "solution": "class Beam:\n    def __init__(self, span_m, udl_kn_m):\n        self.span_m = span_m\n        self.udl_kn_m = udl_kn_m\n\n    def max_moment(self):\n        return self.udl_kn_m * self.span_m ** 2 / 8\n\n\nb = Beam(6, 10)\nprint(b.max_moment())\n",
        "hints": [
            "In `__init__`: `self.span_m = span_m` and `self.udl_kn_m = udl_kn_m`.",
            "`return self.udl_kn_m * self.span_m ** 2 / 8`",
        ],
    },
    {
        "id": "first-class",
        "title": "A class that changes",
        "kind": "code",
        "body": """
Methods can also *change* an object's attributes. Each object keeps its own values, so filling one tank doesn't touch another. Remember:

- `__init__(self, ...)` sets the starting attributes using `self.something = ...`
- every method takes `self` first
- methods read and change attributes through `self`

## Your task

Write a class `Tank`:

- `Tank(capacity)` creates a tank with that capacity and a `level` of `0`.
- `fill(litres)` adds water, but the level can never go above the capacity. Any extra just overflows and is lost.
- `is_full()` returns `True` when the level equals the capacity.
""",
        "starter": "class Tank:\n    def __init__(self, capacity):\n        pass\n\n    def fill(self, litres):\n        pass\n\n    def is_full(self):\n        pass\n\n\nt = Tank(1000)\nt.fill(600)\nt.fill(600)\nprint(t.level, t.is_full())\n",
        "tests": '''
def test_init():
    "A new tank has the given capacity and level 0"
    t = need("Tank")(500)
    check(getattr(t, "capacity", None) == 500, "Tank(500).capacity should be 500.")
    check(getattr(t, "level", None) == 0, "A new tank's level should be 0.")

def test_fill():
    "fill adds water but stops at capacity"
    t = need("Tank")(1000)
    t.fill(300)
    check(t.level == 300, "After fill(300) the level is %r." % t.level)
    t.fill(900)
    check(t.level == 1000, "Overfilling should stop at 1000, got %r." % t.level)

def test_full():
    "is_full is True only at capacity"
    T = need("Tank")
    t = T(100)
    check(t.is_full() is False, "An empty tank isn't full.")
    t.fill(99)
    check(t.is_full() is False, "99 of 100 isn't full.")
    t.fill(1)
    check(t.is_full() is True, "100 of 100 is full.")

def test_separate():
    "Two tanks don't share their water"
    T = need("Tank")
    a, b = T(100), T(100)
    a.fill(50)
    check(b.level == 0, "Filling one tank changed another. Use self.level, not a shared variable.")
''',
        "solution": "class Tank:\n    def __init__(self, capacity):\n        self.capacity = capacity\n        self.level = 0\n\n    def fill(self, litres):\n        self.level = min(self.level + litres, self.capacity)\n\n    def is_full(self):\n        return self.level == self.capacity\n\n\nt = Tank(1000)\nt.fill(600)\nt.fill(600)\nprint(t.level, t.is_full())\n",
        "hints": [
            "In `__init__`: `self.capacity = capacity` and `self.level = 0`.",
            "In `fill`, `min()` of the new level and the capacity keeps it from going over.",
        ],
    },
    {
        "id": "methods",
        "title": "Methods that compute",
        "kind": "code",
        "body": """
Methods can return values worked out from an object's attributes, and they can call each other through `self`:

```python
class Order:
    def __init__(self, qty, unit_price):
        self.qty = qty
        self.unit_price = unit_price

    def subtotal(self):
        return self.qty * self.unit_price

    def total(self, vat=0.15):
        return self.subtotal() * (1 + vat)
```

## Your task

Write a class `Rectangle`:

- `Rectangle(width, height)` stores both.
- `area()` returns width times height.
- `perimeter()` returns the distance all the way round.
- `is_square()` returns `True` if the sides are equal.
- `scale(factor)` multiplies both sides by `factor`, changing the rectangle in place. It doesn't need to return anything.
""",
        "starter": "class Rectangle:\n    def __init__(self, width, height):\n        pass\n\n    # add area, perimeter, is_square and scale here\n",
        "tests": '''
def test_basic():
    "area and perimeter"
    r = need("Rectangle")(3, 4)
    check(r.area() == 12, "Rectangle(3, 4).area() returned %r." % r.area())
    check(r.perimeter() == 14, "Rectangle(3, 4).perimeter() returned %r." % r.perimeter())

def test_square():
    "is_square"
    R = need("Rectangle")
    check(R(5, 5).is_square() is True, "5 by 5 is a square.")
    check(R(5, 6).is_square() is False, "5 by 6 isn't.")

def test_scale():
    "scale changes the rectangle itself"
    r = need("Rectangle")(2, 3)
    r.scale(2)
    check(r.area() == 24, "After scale(2), a 2 by 3 rectangle should have area 24, got %r." % r.area())
    check(r.perimeter() == 20, "After scale(2), perimeter should be 20, got %r." % r.perimeter())
''',
        "solution": "class Rectangle:\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n\n    def area(self):\n        return self.width * self.height\n\n    def perimeter(self):\n        return 2 * (self.width + self.height)\n\n    def is_square(self):\n        return self.width == self.height\n\n    def scale(self, factor):\n        self.width *= factor\n        self.height *= factor\n",
        "hints": [
            "Start with `__init__(self, width, height)` storing `self.width` and `self.height`.",
            "`scale` changes the attributes: `self.width *= factor`, same for height.",
        ],
    },
    {
        "id": "dunder-str",
        "title": "Printing objects nicely",
        "kind": "code",
        "body": """
Print an object you've made and you get something unhelpful like `<__main__.Point object at 0x7f...>`.

Define a `__str__` method that returns a string, and Python uses it whenever the object is printed or passed to `str()`:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

print(Point(3, 4))   # (3, 4)
```

Methods with double underscores on both sides are called **dunder** (or magic) methods. Python calls them for you in particular situations. `__init__` is one you already know.

## Your task

Complete the `Point` class:

- `__str__` returns the point as `"(x, y)"`, like above.
- `distance_to(other)` returns the straight-line distance to another `Point`. That's the square root of (difference in x squared plus difference in y squared). `n ** 0.5` gives a square root.
""",
        "starter": "class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\n\na = Point(0, 0)\nb = Point(3, 4)\nprint(a, b)\nprint(a.distance_to(b))\n",
        "tests": '''
def test_str():
    "str(Point(3, 4)) is '(3, 4)'"
    P = need("Point")
    check(str(P(3, 4)) == "(3, 4)", "str(Point(3, 4)) gave %r." % str(P(3, 4)))
    check(str(P(-1, 2.5)) == "(-1, 2.5)", "str(Point(-1, 2.5)) gave %r." % str(P(-1, 2.5)))

def test_distance():
    "distance_to works"
    P = need("Point")
    check(abs(P(0, 0).distance_to(P(3, 4)) - 5) < 1e-9, "Distance from (0, 0) to (3, 4) should be 5.")
    check(abs(P(1, 1).distance_to(P(4, 5)) - 5) < 1e-9, "Distance from (1, 1) to (4, 5) should be 5.")
    check(P(2, 2).distance_to(P(2, 2)) == 0, "Distance to the same spot should be 0.")
''',
        "solution": 'class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\n    def __str__(self):\n        return f"({self.x}, {self.y})"\n\n    def distance_to(self, other):\n        dx = self.x - other.x\n        dy = self.y - other.y\n        return (dx ** 2 + dy ** 2) ** 0.5\n\n\na = Point(0, 0)\nb = Point(3, 4)\nprint(a, b)\nprint(a.distance_to(b))\n',
        "hints": [
            "`other` is another Point, so you can read `other.x` and `other.y`.",
            "`return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5`",
        ],
    },
    {
        "id": "inheritance",
        "title": "Inheritance",
        "kind": "code",
        "body": """
A class can be based on another. The new class (the **child**) gets everything from the original (the **parent**) and can add to it or replace parts of it.

```python
class Vehicle:
    def __init__(self, name):
        self.name = name

    def describe(self):
        return f"{self.name} with {self.wheels()} wheels"

    def wheels(self):
        return 4

class Bike(Vehicle):
    def wheels(self):        # replaces the parent's version
        return 2

print(Bike("BMX").describe())   # BMX with 2 wheels
```

`Bike` never defined `__init__` or `describe`, so it uses `Vehicle`'s. When `describe` calls `self.wheels()`, Python uses the child's version, because `self` is a `Bike`.

If a child needs its own `__init__`, it can still run the parent's with `super().__init__(...)`. That's what you need when the child takes different values from the parent:

```python
class Truck(Vehicle):
    def __init__(self, name, payload_t):
        super().__init__(name)        # let Vehicle store the name
        self.payload_t = payload_t    # then store the extra value

    def wheels(self):
        return 6
```

## Your task

`Shape` is written for you. Write two child classes:

- `Circle(radius)` with an `area()` that returns pi times radius squared (use `3.14159`).
- `Square(side)` with an `area()` that returns side squared.

Both must call `super().__init__(...)` with the name `"circle"` or `"square"`, so the inherited `describe()` method works.
""",
        "starter": 'class Shape:\n    def __init__(self, name):\n        self.name = name\n\n    def area(self):\n        return 0\n\n    def describe(self):\n        return f"A {self.name} with area {self.area():.2f}"\n\n\nclass Circle(Shape):\n    def __init__(self, radius):\n        # 1. call super().__init__ with the name \"circle\"\n        # 2. store the radius on self\n        pass\n\n    # write area() here\n\n\n# write Square here, the same way\n\n\nprint(Circle(1).describe())\nprint(Square(3).describe())\n',
        "tests": '''
def test_circle():
    "Circle works and inherits describe()"
    C = need("Circle")
    c = C(2)
    check(abs(c.area() - 12.56636) < 1e-6, "Circle(2).area() returned %r." % c.area())
    check(c.describe() == "A circle with area 12.57", "Circle(2).describe() returned %r." % c.describe())

def test_square():
    "Square works and inherits describe()"
    s = need("Square")(3)
    check(s.area() == 9, "Square(3).area() returned %r." % s.area())
    check(s.describe() == "A square with area 9.00", "Square(3).describe() returned %r." % s.describe())

def test_inherits():
    "Both are subclasses of Shape"
    S = need("Shape")
    check(issubclass(need("Circle"), S) and issubclass(need("Square"), S), "Write them as class Circle(Shape) and class Square(Shape).")
    check("describe" not in need("Circle").__dict__ and "describe" not in need("Square").__dict__,
          "Don't rewrite describe(). Let them inherit it from Shape.")
''',
        "solution": 'class Shape:\n    def __init__(self, name):\n        self.name = name\n\n    def area(self):\n        return 0\n\n    def describe(self):\n        return f"A {self.name} with area {self.area():.2f}"\n\n\nclass Circle(Shape):\n    def __init__(self, radius):\n        super().__init__("circle")\n        self.radius = radius\n\n    def area(self):\n        return 3.14159 * self.radius ** 2\n\n\nclass Square(Shape):\n    def __init__(self, side):\n        super().__init__("square")\n        self.side = side\n\n    def area(self):\n        return self.side ** 2\n\n\nprint(Circle(1).describe())\nprint(Square(3).describe())\n',
        "hints": [
            "`class Circle(Shape):` then an `__init__(self, radius)` that calls `super().__init__(\"circle\")` and stores the radius.",
            "Then an `area(self)` method using `self.radius`. Square is the same shape of code.",
        ],
    },
    {
        "id": "class-vs-instance",
        "title": "Class or instance?",
        "kind": "quiz",
        "body": """
Attributes set on `self` belong to one object. Attributes written directly in the class body belong to the class and are shared by every object.

```python
class Ticket:
    prefix = "TK"          # class attribute, shared

    def __init__(self, n):
        self.n = n         # instance attribute, one per object
```

Shared class attributes are fine for constants. Using a mutable one (like a list) by accident is a classic bug.
""",
        "question": "What does this print?\n\n```python\nclass Bin:\n    items = []\n    def add(self, x):\n        self.items.append(x)\n\na = Bin()\nb = Bin()\na.add(\"bolt\")\nprint(b.items)\n```",
        "options": ['`[]`', '`["bolt"]`', "An `AttributeError`", "`None`"],
        "answer": 1,
        "explain": "`items` was created once, in the class body, so every `Bin` shares that one list. Adding through `a` shows up in `b` too. The fix is to create the list per object in `__init__`: `self.items = []`.",
    },
]
