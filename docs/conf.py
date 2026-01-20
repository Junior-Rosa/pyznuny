from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

project = "py-znuny"
author = "Junior Rosa, Pablo Gascon"

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - for older runtimes
    tomllib = None

release = "0.0.0"
if tomllib is not None:
    try:
        with (ROOT / "pyproject.toml").open("rb") as handle:
            release = tomllib.load(handle)["project"]["version"]
    except (FileNotFoundError, KeyError, OSError, ValueError):
        pass

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 2,
}
html_static_path = []

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
