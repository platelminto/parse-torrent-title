#!/usr/bin/env python
import sys


if sys.version_info.major == 3:
    import importlib

    re = importlib.import_module("re")

elif sys.version_info.major == 2:
    import pkgutil
    # Regex in python 2 is very slow so we check if the faster 'regex' library is available.
    faster_regex = pkgutil.find_loader("regex")
    if faster_regex is not None:
        re = faster_regex.load_module("regex")
    else:
        re = pkgutil.find_loader("re").load_module("re")

from .parse import PTN

__author__ = "Giorgio Momigliano"
__email__ = "gmomigliano@protonmail.com"
__version__ = "2.8.2"
__license__ = "MIT"


def parse(name, standardise=True, coherent_types=False):
    return PTN().parse(name, standardise, coherent_types)
