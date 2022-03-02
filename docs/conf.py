"""Sphinx configuration."""
project = "xltektools"
author = "Anthony Fong"
copyright = "2022, Anthony Fong"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
