# -*- coding: utf-8 -*-
#
# skrub documentation build configuration file, created by
# sphinx-quickstart on Tue Mar 13 14:34:47 2018.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import shutil
from datetime import datetime
import sys

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
sys.path.insert(0, os.path.abspath("sphinxext"))
from github_link import make_linkcode_resolve


# -- Copy files for docs --------------------------------------------------
#
# We avoid duplicating the information, but we do not use symlinks to be
# able to build the docs on Windows
shutil.copyfile("../RELEASE_PROCESS.rst", "RELEASE_PROCESS.rst")
shutil.copyfile("../CHANGES.rst", "CHANGES.rst")
shutil.copyfile("../CONTRIBUTING.rst", "CONTRIBUTING.rst")

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # builtin
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinx.ext.linkcode",
    "sphinx.ext.autodoc.typehints",
    # contrib
    "numpydoc",
    "sphinx_issues",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
]

try:
    import sphinxext.opengraph  # noqa

    extensions.append("sphinxext.opengraph")
except ImportError:
    print("ERROR: sphinxext.opengraph import failed")

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "skrub"
copyright = f"2018-2023, the dirty_cat developers, 2023-{datetime.now().year}, the skrub developers"
author = "skrub contributors"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version_file = os.path.join("..", "skrub", "VERSION.txt")
with open(version_file) as fh:
    version = fh.read().strip()
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for autodoc / autosummary ----------------------------------------
# generate autosummary even if no references
autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

autodoc_default_flags = ["members", "inherited-members"]


# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "logo": {
        "image_relative": "_static/skrub.svg",
        "image_light": "_static/skrub.svg",
        "image_dark": "_static/skrub.svg",
    },
    #"external_links": [
    #    {
    #        "url": "https://pydata.org",
    #        "name": "PyData",
    #    },
    #],
    "header_links_before_dropdown": 4,
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/skrub_data",
            "icon": "fa-brands fa-twitter",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/skrub-data/skrub/",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/skrub",
            "icon": "fa-custom fa-pypi",
        },
    ],
    # alternative way to set twitter and github header icons
    # "github_url": "https://github.com/pydata/pydata-sphinx-theme",
    # "twitter_url": "https://twitter.com/PyData",
    "use_edit_page_button": True,
    "show_toc_level": 1,
    "navbar_align": "left",  # [left, content, right] For testing that the navbar items align properly
    #"navbar_center": ["version-switcher", "navbar-nav"],
    "navbar_center": ["navbar-nav"],
    "announcement": "https://raw.githubusercontent.com/skrub-data/skrub/main/doc/announcement.html",
    # "show_nav_level": 2,
    # "navbar_start": ["navbar-logo"],
    # "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # "navbar_persistent": ["search-button"],
    # "primary_sidebar_end": ["custom-template.html", "sidebar-ethical-ads.html"],
    # "article_footer_items": ["prev-next.html", "test.html", "test.html"],
    # "content_footer_items": ["prev-next.html", "test.html", "test.html"],
    # "footer_start": ["test.html", "test.html"],
    # "secondary_sidebar_items": ["page-toc.html"],  # Remove the source buttons
    #"switcher": {
    #    "json_url": json_url,
    #    "version_match": version_match,
    #},
}

# Needed for the edit button
html_context = {
    "github_user": "skrub_data",
    "github_repo": "skrub",
    "github_version": "main",
    "doc_path": "docs",
    "carousel": [
        dict(
            title="Assembling",
            text="Joining multiple tables on non-normalized columns.",  # noqa E501
            url="auto_examples/01_dirty_categories.html",
            img="",
            alt="",
        ),
        dict(
            title="Encoding",
            text="Fast and scalable methods for encoding \"dirty\" categorical variables to numerical arrays suitable for machine learning.",  # noqa E501
            url="auto_examples/01_dirty_categories.html",
            img="",
            alt="",
        ),
        dict(
            title="Cleaning",
            text="Altering the data directly by cleaning dirty instances with techniques such as deduplication.",  # noqa E501
            url="auto_examples/01_dirty_categories.html",
            img="",
            alt="",
        ),
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/custom.css",
    "css/quickstart.css",
    "https://scikit-learn.org/stable/_static/css/theme.css",
]

html_js_files = [
    'js/quickstart.min.js',
]


# Project logo, to place at the top of the sidebar.
html_logo = "_static/skrub.svg"


# Modify the title to get good social-media links
html_title = "skrub"


# -- Options for HTMLHelp output ----------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "skrubdoc"


# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "skrub.tex",
        "skrub Documentation",
        "skrub developers",
        "manual",
    ),
]


# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "skrub", "skrub Documentation", [author], 1)]


# -- Options for Texinfo output -----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "skrub",
        "skrub Documentation",
        author,
        "skrub",
        "Prepping tables for machine learning.",
        "Data Science",
    ),
]


# Configuration for intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "matplotlib": ("https://matplotlib.org", None),
    "sklearn": ("https://scikit-learn.org/stable", None),
    "skimage": ("http://scikit-image.org/docs/stable", None),
    "mayavi": ("http://docs.enthought.com/mayavi/mayavi", None),
    "statsmodels": ("http://www.statsmodels.org/stable", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/stable", None),
    "seaborn": ("http://seaborn.pydata.org", None),
}


# -- sphinx-gallery configuration ---------------------------------------------
from sphinx_gallery.sorting import FileNameSortKey  # noqa

if 'dev' in release:
    binder_branch = 'main'
else:
    binder_branch = release

sphinx_gallery_conf = {
    "doc_module": "skrub",
    "backreferences_dir": os.path.join("generated"),
    "reference_url": {
        # The module we locally document (so, skrub) uses None
        "skrub": None,
        # We don't specify the other modules as we use the intershpinx ext.
        # See https://sphinx-gallery.github.io/stable/configuration.html#link-to-documentation  # noqa
    },
    "filename_pattern": ".*",
    "examples_dirs": "../examples",
    "gallery_dirs": "auto_examples",
    "within_subsection_order": FileNameSortKey,
    "download_all_examples": False,
    "binder": {
        "org": "skrub-data",
        "repo": "skrub",
        "binderhub_url": "https://mybinder.org",
        "branch": binder_branch,
        "dependencies": "./binder/requirements.txt",
        "use_jupyter_lab": True,
    },
}

# -- sphinx.ext.opengraph configuration ---------------------------------------
ogp_site_url = "https://skrub-data.github.io/stable/"
ogp_image = "https://skrub-data.github.io/stable/_static/skrub.svg"
ogp_use_first_image = True
ogp_site_name = "skrub"

# -- numpydoc configuration ---------------------------------------------------

# Produce `plot::` directives for examples that contain `import matplotlib` or
# `from matplotlib import`.
numpydoc_use_plots = True

# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
numpydoc_class_members_toctree = False

numpydoc_xref_param_type = True
numpydoc_xref_aliases = {
    # Python
    "file-like": ":term:`file-like <python:file object>`",
    "iterator": ":term:`iterator <python:iterator>`",
    "path-like": ":term:`path-like`",
    "Path": ":class:`python:pathlib.Path`",
    "bool": ":class:`python:bool`",
    # Matplotlib
    "colormap": ":doc:`colormap <matplotlib:tutorials/colors/colormaps>`",
    "color": ":doc:`color <matplotlib:api/colors_api>`",
    "Axes": "matplotlib.axes.Axes",
    "Figure": "matplotlib.figure.Figure",
    "Axes3D": "mpl_toolkits.mplot3d.axes3d.Axes3D",
    "ColorbarBase": "matplotlib.colorbar.ColorbarBase",
    # sklearn
    "LeaveOneOut": "sklearn.model_selection.LeaveOneOut",
    "Transformer": "sklearn.base.TransformerMixin",
    # joblib
    "joblib.Parallel": "joblib.Parallel",
    "joblib.delayed": "joblib.delayed",
}

# -- sphinx.ext.autodoc configuration -----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autodoc_typehints = "none"

# -- sphinx_favicon configuration ---------------------------------------------
favicons = {"rel": "icon", "href": "_static/skrub.svg", "type": "image/svg+xml"}

# -- github links -------------------------------------------------------------

# we use the issues path for PRs since the issues URL will forward
issues_github_path = "skrub-data/skrub"

# The following is used by sphinx.ext.linkcode to provide links to GitHub
linkcode_resolve = make_linkcode_resolve(
    "skrub",
    "https://github.com/skrub-data/skrub/blob/{revision}/{package}/{path}#L{lineno}",
)

# -- Sphinx-Copybutton configuration -----------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
