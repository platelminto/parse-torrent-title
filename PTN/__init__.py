#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .parse import PTN

__author__ = 'Giorgio Momigliano'
__email__ = 'gmomigliano@protonmail.com'
__version__ = '2.0'
__license__ = 'MIT'

ptn = PTN()


def parse(name, standardise=True):
    return ptn.parse(name, standardise)
