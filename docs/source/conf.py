# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'serial_toolbox'
copyright = '2024, Takuya Sasatani'
author = 't-sasatani'
release = '0.1.5'

extensions = [
    'myst_parser',
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx_click',
]

autosummary_generate = True
autodoc_inherit_docstrings = False
set_type_checking_flag = True

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'press'
#html_static_path = ['_static']