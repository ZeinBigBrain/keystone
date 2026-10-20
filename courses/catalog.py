"""
The learning path, in order.

Each track's lessons live in courses/<folder>/ as chNN_*.py files.
A track without a "folder" can instead give an "outline" (a list of
{"title", "topics"}) and shows in the menu as "Planned".
"""

TRACKS = [
    {
        "id": "py",
        "title": "Python fundamentals",
        "blurb": "The base everything else sits on. From your first print() to writing your own classes.",
        "folder": "python",
    },
    {
        "id": "sql",
        "title": "SQL and databases",
        "blurb": "Store data properly and ask questions of it. Uses SQLite, which comes with Python.",
        "prereq": "Python fundamentals, chapters 1 to 7 (the last chapter also uses functions and loops)",
        "folder": "sql",
    },
    {
        "id": "eng",
        "title": "Python for engineering",
        "blurb": "Numbers, data and plots. NumPy, pandas, matplotlib and SciPy for real calculation work.",
        "prereq": "Python fundamentals (SQL helps for the pandas chapters, but isn't required)",
        "folder": "engineering",
    },
    {
        "id": "be",
        "title": "Back-end development",
        "blurb": "How servers, APIs and deployments work, built up from scratch in Python.",
        "prereq": "Python fundamentals and SQL",
        "folder": "backend",
    },
]
