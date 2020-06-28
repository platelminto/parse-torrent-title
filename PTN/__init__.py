#!/usr/bin/env python

import pkgutil
import re
import sys

# Regex in python 2 is very slow so we check if the faster 'regex' library is available.
faster_regex = pkgutil.find_loader('regex')
if faster_regex is not None and sys.version_info[0] < 3:
    re = faster_regex.load_module('regex')

from .parse import PTN

__author__ = 'Giorgio Momigliano'
__email__ = 'gmomigliano@protonmail.com'
__version__ = '2.1'
__license__ = 'MIT'

ptn = PTN()


def parse(name, standardise=True):
    return ptn.parse(name, standardise)
