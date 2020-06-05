#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .parse import PTN

__author__ = 'Giorgio Momigliano'
__email__ = 'gmomigliano@protonmail.com'
__version__ = '1.4'
__license__ = 'MIT'

ptn = PTN()


def parse(name, keep_raw=True):
    return ptn.parse(name, keep_raw)
