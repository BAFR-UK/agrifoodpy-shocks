import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "agrifoodpy-shocks"
author = "BAFR"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

templates_path = []
exclude_patterns = []

autosummary_generate = True
autodoc_member_order = "bysource"

html_theme = "sphinx_rtd_theme"
html_static_path = []
