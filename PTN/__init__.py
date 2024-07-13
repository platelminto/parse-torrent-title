#!/usr/bin/env python

from .parse import PTN

__author__ = "Giorgio Momigliano"
__email__ = "gmomigliano@protonmail.com"
__version__ = "2.8.2"
__license__ = "MIT"

# Singleton instance of PTN
_ptn_instance = PTN()


def parse(name: str, standardise: bool = True, coherent_types: bool = False) -> dict:
    """
    Parse the torrent title into its components.

    :param name: The torrent name to parse.
    :param standardise: Whether to standardise the parsed values.
    :param coherent_types: Whether to ensure coherent types in the parsed results.
    :return: A dictionary of parsed components.
    """
    return _ptn_instance.parse(name, standardise, coherent_types)
