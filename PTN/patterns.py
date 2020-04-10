#!/usr/bin/env python
# -*- coding: utf-8 -*-

delimiters = '[\.\s\-\+_\/]'
langs = 'rus|(?:True)?fr(?:ench)?|e?n(?:g(?:lish)?)?|vost(' \
        '?:fr)?|ita(?:liano)?|castellano|spanish|dk|german|multi|nordic|exyu|chs|hindi|polish|mandarin'

season_range_pattern = '(?:Complete' + delimiters + '*)?(?:' + delimiters + '*)?(?:s(?:easons?)?)?' + delimiters + '?(?:s?[0-9]{1,2}[\s]*(' \
                       '?:\-|(?:\s*to\s*))[\s]*s?[0-9]{1,2})'

year_pattern = '(?:19[0-9]|20[0-2])[0-9]'
month_pattern = '0[1-9]|1[0-2]'
day_pattern = '[0-2][0-9]|3[01]'

patterns = [
    ('season', delimiters + '(' # Season description can't be at the beginning, must be after this pattern
               '' + season_range_pattern + '|' # Describes season ranges
               '(?:Complete' + delimiters + ')?s([0-9]{1,2})(?:e[0-9]{1,2})?(?:' + delimiters + '?Complete)?|'  # Describes season, optionally with complete or episode
               '([0-9]{1,2})x[0-9]{2}|'  # Describes 5x02, 12x15 type descriptions
               '(?:Complete' + delimiters + ')?Season[\. -]([0-9]{1,2})(?:' + delimiters + '?Complete)?'  # Describes Season.15 type descriptions
               ')(?:' + delimiters + '|$)'),
    ('episode', '((?:(?:[ex]|ep)(?:[0-9]{1,2}(?:-[0-9]{1,2}))|(?:[ex]|ep)([0-9]{1,2}))(?:[^0-9]|$))'),
    ('year', '([\[\(]?(' + year_pattern + ')[\]\)]?)'),
    ('month', '(?:' + year_pattern + ')' + delimiters + '(' + month_pattern + ')' + delimiters + '(?:' + day_pattern + ')'),
    ('day', '(?:' + year_pattern + ')' + delimiters + '(?:' + month_pattern + ')' + delimiters + '(' + day_pattern + ')'),
    ('resolution', '([0-9]{3,4}p|1280x720)'),
    ('quality', ('((?:PPV\.)?[HP]DTV|(?:HD)?CAM|B[DR]Rip|(?:HD-?)?TS|'
                 '(?:PPV )?WEB(?:-?DL(?:Mux)?)?(?: DVDRip)?|HDRip|HDTVRip|DVDRip|DVDRIP|'
                 'CamRip|W[EB]BRip|BluRay|DvDScr|hdtv|telesync)')),
    ('codec', '(xvid|[hx]\.?26[45])'),
    ('audio', ('(MP3|DD5\.?1|Dual[\- ]Audio|LiNE|DTS|DTS5\.1|'
               'AAC[ \.-]LC|AAC(?:(?:\.?2(?:\.0)?)?|(?:\.?5(?:\.1)?)?)|'
               '(?:E-?)?AC-?3(?:' + delimiters + '?5\.1)?)')),
    ('group', '(- ?([^-]+(?:-={[^-]+-?$)?))$'),
    ('region', 'R[0-9]'),
    ('extended', '(EXTENDED(:?.CUT)?)'),
    ('hardcoded', 'HC'),
    ('proper', 'PROPER'),
    ('repack', 'REPACK'),
    ('container', '(MKV|AVI|MP4)'),
    ('widescreen', 'WS'),
    ('website', '^(\[ ?([^\]]+?) ?\])'),
    ('subtitles', '((?:(?:' + langs + '|e-?)[\-\s.]*)*subs?)'),
    ('language', '(' + langs + ')(?!(?:[\-\s.]*(?:' + langs + ')*)+[\-\s.]?subs)'),
    ('sbs', '(?:Half-)?SBS'),
    ('unrated', 'UNRATED'),
    ('size', '(\d+(?:\.\d+)?(?:GB|MB))'),
    ('bit-depth', '(?:8|10)bit'),
    ('3d', '3D')
]

types = {
    'season': 'integer',
    'episode': 'integer',
    'year': 'integer',
    'month': 'integer',
    'day': 'integer',
    'extended': 'boolean',
    'hardcoded': 'boolean',
    'proper': 'boolean',
    'repack': 'boolean',
    'widescreen': 'boolean',
    'unrated': 'boolean',
    '3d': 'boolean'
}

exceptions = [
    {'parsed_title': '', 'incorrect_parse': ('year', 1983), 'actual_title': '1983'}
]
