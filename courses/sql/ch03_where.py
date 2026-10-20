import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.sql"), encoding="utf-8") as _f:
    SITE = _f.read()

CHAPTER = {
    "title": "Filtering with WHERE",
    "summary": "Keeping only the rows you want: comparisons, text, AND and OR, IN, BETWEEN, LIKE and NULL.",
}

LESSONS = [
    {
        "id": "where-numbers",
        "title": "WHERE with numbers",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`WHERE` keeps only the rows that pass a test. It goes after `FROM`:

```sql
SELECT name, rating
FROM suppliers
WHERE rating >= 4;
```

The comparisons are the ones you know from Python, with two differences: equals is a single `=`, and "not equal" can be written `<>` as well as `!=`.

| SQL | Means |
|---|---|
| `=` | equal to |
| `<>` or `!=` | not equal to |
| `<` `>` `<=` `>=` | as in Python |

## Your task

Show the `name` and `unit_price` of every material that costs **more than** 100.
""",
        "starter": "SELECT name, unit_price\nFROM materials\n-- add a WHERE line here\n",
        "tests": '''
def test_rows():
    "Only materials over 100"
    check_rows("SELECT name, unit_price FROM materials WHERE unit_price > 100", hint="Check > versus >=.")
''',
        "solution": "SELECT name, unit_price\nFROM materials\nWHERE unit_price > 100;\n",
        "hints": [
            "`WHERE unit_price > 100` on its own line, after `FROM materials`.",
        ],
    },
    {
        "id": "where-text",
        "title": "WHERE with text",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
To compare with text, put the text in **single quotes**:

```sql
SELECT name, role
FROM staff
WHERE site = 'JED-1';
```

Text comparisons are exact. `'Jed-1'` and `'JED-1 '` (with a space) don't match `'JED-1'`.

> **Common slips:**
> - No quotes: `WHERE city = Riyadh`. SQL thinks `Riyadh` is a column name and fails.
> - Double quotes: `WHERE city = "Riyadh"`. SQLite often lets this go, but other databases won't. Use single quotes.

## Your task

Show the `name` of every supplier based in `Riyadh`.
""",
        "starter": "-- names of suppliers whose city is Riyadh\n",
        "tests": '''
def test_rows():
    "Only Riyadh suppliers"
    check_rows("SELECT name FROM suppliers WHERE city = 'Riyadh'")

def test_quotes():
    "Uses single quotes for the text"
    check("'Riyadh'" in SQL, "Put Riyadh in single quotes: 'Riyadh'.")
''',
        "solution": "SELECT name\nFROM suppliers\nWHERE city = 'Riyadh';\n",
        "hints": [
            "`WHERE city = 'Riyadh'`",
        ],
    },
    {
        "id": "quotes-quiz",
        "title": "Spot the error",
        "kind": "quiz",
        "body": "Read the error message the way Python taught you: what does it say is missing?",
        "question": "This fails with `no such column: Riyadh`. Why?\n\n```sql\nSELECT name FROM suppliers WHERE city = Riyadh;\n```",
        "options": [
            "The suppliers table has no city column",
            "Without quotes, Riyadh is read as a column name",
            "WHERE must come before FROM",
            "Text comparisons need `==`",
        ],
        "answer": 1,
        "explain": "Unquoted words in SQL are names of things: tables, columns, functions. So SQL looks for a column called `Riyadh` and can't find one. `'Riyadh'` in single quotes is a text value.",
    },
    {
        "id": "and",
        "title": "AND",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`AND` joins two tests. A row is kept only if it passes **both**:

```sql
SELECT name, years
FROM staff
WHERE site = 'RYD-N' AND years > 5;
```

## Your task

Show the `id`, `delivery_date` and `quantity` of every delivery to site `RYD-N` with a quantity of **20 or more**.
""",
        "starter": "SELECT id, delivery_date, quantity\nFROM deliveries\n-- WHERE ... AND ...\n",
        "tests": '''
def test_rows():
    "RYD-N deliveries of 20 or more"
    check_rows("SELECT id, delivery_date, quantity FROM deliveries WHERE site = 'RYD-N' AND quantity >= 20",
               hint="Both conditions must hold: the site, and quantity >= 20.")
''',
        "solution": "SELECT id, delivery_date, quantity\nFROM deliveries\nWHERE site = 'RYD-N' AND quantity >= 20;\n",
        "hints": [
            "`WHERE site = 'RYD-N' AND quantity >= 20`",
        ],
    },
    {
        "id": "or",
        "title": "OR",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`OR` keeps a row if it passes **at least one** of the tests:

```sql
SELECT name, city
FROM suppliers
WHERE city = 'Jeddah' OR city = 'Dammam';
```

> **Common slip:** `WHERE city = 'Jeddah' OR 'Dammam'`. Each side of `OR` has to be a complete test, so the column name has to be repeated.

## Your task

Show the `name` and `category` of every material in the `steel` **or** `masonry` category.
""",
        "starter": "-- materials in the steel or masonry category\n",
        "tests": '''
def test_rows():
    "Steel and masonry materials"
    check_rows("SELECT name, category FROM materials WHERE category = 'steel' OR category = 'masonry'",
               hint="Write the full test on each side of OR: category = '...' OR category = '...'.")
''',
        "solution": "SELECT name, category\nFROM materials\nWHERE category = 'steel' OR category = 'masonry';\n",
        "hints": [
            "`WHERE category = 'steel' OR category = 'masonry'`",
        ],
    },
    {
        "id": "and-or-quiz",
        "title": "AND before OR",
        "kind": "quiz",
        "body": """
When a WHERE mixes `AND` and `OR`, SQL does the `AND` first, the same way `*` comes before `+` in maths.

So `a OR b AND c` means `a OR (b AND c)`.
""",
        "question": "Which materials does this keep?\n\n```sql\nWHERE category = 'aggregate' OR category = 'binder' AND unit_price < 50\n```",
        "options": [
            "Aggregates and binders that cost under 50",
            "All aggregates, plus binders that cost under 50",
            "Everything under 50",
            "Nothing, it's an error",
        ],
        "answer": 1,
        "explain": "The `AND` binds first: `category = 'binder' AND unit_price < 50`. That result is then OR-ed with `category = 'aggregate'`, so every aggregate gets in whatever its price. Brackets fix it, which is the next lesson.",
    },
    {
        "id": "brackets",
        "title": "Brackets",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
Brackets make SQL do part of the test first, exactly as in maths:

```sql
SELECT name, city, rating
FROM suppliers
WHERE (city = 'Riyadh' OR city = 'Jeddah') AND rating >= 4;
```

Any time a WHERE has both `AND` and `OR`, add brackets. Even when they aren't strictly needed, they show the reader what you meant.

## Your task

Show the `name`, `category` and `unit_price` of materials that are in the `aggregate` **or** `binder` category **and** cost under 50.
""",
        "starter": "SELECT name, category, unit_price\nFROM materials\nWHERE category = 'aggregate' OR category = 'binder' AND unit_price < 50;\n",
        "tests": '''
def test_rows():
    "Aggregates or binders, under 50"
    check_rows("SELECT name, category, unit_price FROM materials WHERE (category = 'aggregate' OR category = 'binder') AND unit_price < 50",
               hint="Gravel costs 52, so it shouldn't appear. Put brackets round the OR part.")
''',
        "solution": "SELECT name, category, unit_price\nFROM materials\nWHERE (category = 'aggregate' OR category = 'binder') AND unit_price < 50;\n",
        "hints": [
            "Run the starter first. Gravel shows up even though it costs 52. Why?",
            "Wrap the two category tests in brackets: `(category = 'aggregate' OR category = 'binder') AND unit_price < 50`.",
        ],
    },
    {
        "id": "in",
        "title": "IN",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
A long chain of `OR`s on the same column is easier to write with `IN` and a list in brackets:

```sql
SELECT name, role
FROM staff
WHERE role IN ('planner', 'surveyor', 'foreman');
```

`NOT IN` keeps everything that **isn't** in the list. And `NOT` in front of any test flips it: `WHERE NOT city = 'Riyadh'`.

## Your task

Show the `name` and `category` of every material that is **not** in the `finishes` or `formwork` categories. Use `NOT IN`.
""",
        "starter": "-- materials whose category is NOT IN ('finishes', 'formwork')\n",
        "tests": '''
def test_rows():
    "Everything except finishes and formwork"
    check_rows("SELECT name, category FROM materials WHERE category NOT IN ('finishes', 'formwork')")

def test_in():
    "Uses NOT IN"
    check("NOT IN" in SQL.upper(), "Use NOT IN with a bracketed list.")
''',
        "solution": "SELECT name, category\nFROM materials\nWHERE category NOT IN ('finishes', 'formwork');\n",
        "hints": [
            "`WHERE category NOT IN ('finishes', 'formwork')`",
        ],
    },
    {
        "id": "between",
        "title": "BETWEEN",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`BETWEEN low AND high` is a range test that **includes both ends**:

```sql
SELECT name, years
FROM staff
WHERE years BETWEEN 5 AND 10;     -- 5 and 10 both count
```

It works on dates too, because dates stored as `'YYYY-MM-DD'` text sort in date order:

```sql
WHERE delivery_date BETWEEN '2026-10-01' AND '2026-10-03'
```

## Your task

Show the `id`, `delivery_date` and `site` of every delivery from 5 to 10 October 2026, both days included.
""",
        "starter": "SELECT id, delivery_date, site\nFROM deliveries\n-- WHERE delivery_date BETWEEN ...\n",
        "tests": '''
def test_rows():
    "Deliveries from the 5th to the 10th, inclusive"
    check_rows("SELECT id, delivery_date, site FROM deliveries WHERE delivery_date BETWEEN '2026-10-05' AND '2026-10-10'",
               hint="Dates go in quotes, in the form '2026-10-05'.")
''',
        "solution": "SELECT id, delivery_date, site\nFROM deliveries\nWHERE delivery_date BETWEEN '2026-10-05' AND '2026-10-10';\n",
        "hints": [
            "`WHERE delivery_date BETWEEN '2026-10-05' AND '2026-10-10'`",
        ],
    },
    {
        "id": "like",
        "title": "Pattern matching with LIKE",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
`LIKE` matches text against a pattern. Two wildcards:

- `%` stands for any number of characters, including none.
- `_` stands for exactly one character.

```sql
WHERE name LIKE 'G%'        -- starts with G
WHERE name LIKE '%Co'       -- ends with Co
WHERE name LIKE '%Steel%'   -- contains Steel anywhere
```

In SQLite, `LIKE` ignores upper and lower case for ordinary letters, so `'%steel%'` finds `Gulf Steel Trading` too.

## Your task

Show the `name` and `role` of everyone whose role **contains** the word `surveyor` anywhere.
""",
        "starter": "-- staff whose role contains 'surveyor'\n",
        "tests": '''
def test_rows():
    "Everyone whose role contains surveyor"
    check_rows("SELECT name, role FROM staff WHERE role LIKE '%surveyor%'",
               hint="A quantity surveyor counts too, so you need % on both sides.")
''',
        "solution": "SELECT name, role\nFROM staff\nWHERE role LIKE '%surveyor%';\n",
        "hints": [
            "Put `%` before and after the word, because it might be at the start, middle or end.",
            "`WHERE role LIKE '%surveyor%'`",
        ],
    },
    {
        "id": "null-quiz",
        "title": "NULL: the empty value",
        "kind": "quiz",
        "body": """
`NULL` means "no value here": not zero, not empty text, just unknown. Glass has no price yet, and two suppliers have no rating.

NULL is strange in one way: **any** comparison with it gives "unknown", which WHERE treats as a fail. Even `NULL = NULL` isn't true.

To test for it, use the special words `IS NULL` and `IS NOT NULL`:

```sql
WHERE rating IS NULL
```
""",
        "question": "How many rows does this return?\n\n```sql\nSELECT name FROM materials WHERE unit_price = NULL;\n```",
        "options": ["1 (glass)", "0", "8 (every priced material)", "An error"],
        "answer": 1,
        "explain": "`unit_price = NULL` is never true, not even for glass, because comparing anything with NULL gives unknown. There's no error, which is what makes it dangerous: you just get an empty result. `WHERE unit_price IS NULL` returns glass.",
    },
    {
        "id": "is-null",
        "title": "IS NULL",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
```sql
SELECT name FROM suppliers WHERE rating IS NULL;       -- not rated yet
SELECT name FROM suppliers WHERE rating IS NOT NULL;   -- rated
```

> **Common slip:** `WHERE rating < 4` doesn't include the unrated suppliers either. NULL fails every comparison, so if you want them, you have to ask: `WHERE rating < 4 OR rating IS NULL`.

## Your task

Show the `name` and `city` of every supplier that **has not** been rated yet.
""",
        "starter": "-- suppliers with no rating\n",
        "tests": '''
def test_rows():
    "Only unrated suppliers"
    check_rows("SELECT name, city FROM suppliers WHERE rating IS NULL", hint="Use IS NULL, not = NULL.")
''',
        "solution": "SELECT name, city\nFROM suppliers\nWHERE rating IS NULL;\n",
        "hints": [
            "`WHERE rating IS NULL`",
        ],
    },
    {
        "id": "where-task",
        "title": "Chapter task: putting tests together",
        "kind": "code",
        "lang": "sql",
        "setup": SITE,
        "body": """
One query that uses several of this chapter's tools.

## Your task

The South Pavilion site manager wants the `id`, `delivery_date`, `material_id` and `quantity` of every delivery to site `RYD-S`:

- from 1 to 15 October 2026, both days included,
- with a quantity **over** 5,
- for any material **except** material ids 5 and 8.
""",
        "starter": "",
        "tests": '''
def test_rows():
    "The right deliveries"
    check_rows("""SELECT id, delivery_date, material_id, quantity FROM deliveries
                  WHERE site = 'RYD-S'
                    AND delivery_date BETWEEN '2026-10-01' AND '2026-10-15'
                    AND quantity > 5
                    AND material_id NOT IN (5, 8)""",
               hint="Four tests, all joined with AND.")
''',
        "solution": "SELECT id, delivery_date, material_id, quantity\nFROM deliveries\nWHERE site = 'RYD-S'\n  AND delivery_date BETWEEN '2026-10-01' AND '2026-10-15'\n  AND quantity > 5\n  AND material_id NOT IN (5, 8);\n",
        "hints": [
            "Four conditions joined with `AND`: the site, a `BETWEEN` for the dates, `quantity > 5`, and a `NOT IN`.",
            "Putting each condition on its own line, starting with `AND`, makes long WHERE clauses easy to check.",
        ],
    },
]
