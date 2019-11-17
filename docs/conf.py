# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# -- Project information -----------------------------------------------------

project = 'PyFFI'
copyright = '2012-2019, NifTools'
author = 'Amorilia'

# The full version, including alpha/beta/rc tags.
with open("../pyffi/VERSION", "rt") as f:
    release = f.read().strip()
# The short X.Y version.
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.imgmath',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None)
}

todo_include_todos = True
autosummary_generate = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'niftools_sphinx_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of an image file (within the static path) to place at the top of
# the sidebar.
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"
html_last_updated_fmt = '%b %d, %Y'

html_theme_options = {
    "navs": {
        "Home": "http://niftools.org",
        "Our Projects": "http://www.niftools.org/projects",
        "Blog": "http://www.niftools.org/blog",
        "Documentation": "",
        "Forums": "https://forum.niftools.org/",
        "About": "http://www.niftools.org/about"
    },
    "source_code": "https://github.com/niftools/pyffi",
}
