"""Sphinx configuration for TWEO backend documentation."""

import os
import sys

# Allow autodoc to import the backend package without installing it.
sys.path.insert(0, os.path.abspath("../backend"))

# ── Project metadata ──────────────────────────────────────────────────────────

project = "TWEO"
copyright = "2025, Adrien Fort"
author = "Adrien Fort"
release = "0.1.0"

# ── Extensions ────────────────────────────────────────────────────────────────

extensions = [
    "sphinx.ext.autodoc",   # pull docstrings from source
    "sphinx.ext.napoleon",  # parse Google-style docstrings
    "sphinx.ext.viewcode",  # add [source] links to rendered docs
]

# ── autodoc ───────────────────────────────────────────────────────────────────

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "show-inheritance": True,
    "inherited-members": False,
    # Without this, __all__-exported re-imports in __init__.py are documented
    # in both the package and the submodule, causing duplicate-object warnings.
    # With this, autodoc falls back to __module__ checks and skips re-exports.
    "ignore-module-all": True,
}

# Show type hints in the description body, not duplicated in the signature.
autodoc_typehints = "description"
autodoc_member_order = "bysource"

# ── Napoleon (Google docstrings) ──────────────────────────────────────────────

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_rtype = False  # type shown inline by autodoc_typehints

# ── HTML output ───────────────────────────────────────────────────────────────

html_theme = "furo"
html_title = "TWEO"
