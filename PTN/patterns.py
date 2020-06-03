#!/usr/bin/env python
# -*- coding: utf-8 -*-

delimiters = '[\.\s\-\+_\/]'
langs = 'rus|(?:True)?fr(?:ench)?|en(?:g(?:lish)?)?|vost(' \
        '?:fr)?|ita(?:liano?)?|castellano|swedish|spanish|dk|german|nordic|exyu|chs|hindi|polish|mandarin'
producers = 'ATVP|AMZN|NF|NICK|RED|DSNP'

season_range_pattern = '(?:Complete' + delimiters + '*)?(?:' + delimiters + '*)?(?:s(?:easons?)?)?' + delimiters + '?(?:s?[0-9]{1,2}[\s]*(' \
                       '?:\-|(?:\s*to\s*))[\s]*s?[0-9]{1,2})(?:' + delimiters + '*Complete)?'

# Used when matching episodeName in parse.py, when actually matching episodes we use a slightly
# modified version that has a capture group on the episode number (as seen below).
episode_pattern = '(?:(?:[ex]|ep)(?:[0-9]{1,2}(?:-(?:[ex]|ep)?(?:[0-9]{1,2})))|(?:[ex]|ep)(?:[0-9]{1,2}))'

lang_list_pattern = '(?:(?:' + langs + ')' + delimiters + '*)'
subtitles_pattern = '((?:' + delimiters + ')?subs?' + delimiters + '*(' + lang_list_pattern + '*)|(' + lang_list_pattern + '*)(?:multi' + delimiters + '*)?subs?)'  # 'subs' can be at beginning or end

year_pattern = '(?:19[0-9]|20[0-2])[0-9]'
month_pattern = '0[1-9]|1[0-2]'
day_pattern = '[0-2][0-9]|3[01]'

# Patterns that should only try to be matched after the 'title delimiter', either a year
# or a season. So if we have a language in the title, and there's some basic validation
patterns_ignore_title = ['language']

patterns = [
    ('season', delimiters + '(' # Season description can't be at the beginning, must be after this pattern
               '' + season_range_pattern + '|' # Describes season ranges
               '(?:Complete' + delimiters + ')?s([0-9]{1,2})(?:' + episode_pattern + ')?|'  # Describes season, optionally with complete or episode
               '([0-9]{1,2})x[0-9]{2}|'  # Describes 5x02, 12x15 type descriptions
               '(?:Complete' + delimiters + ')?Season[\. -]([0-9]{1,2})'  # Describes Season.15 type descriptions
               ')(?:' + delimiters + '|$)'),
    ('episode', '((?:[ex]|ep)(?:[0-9]{1,2}(?:-(?:[ex]|ep)?(?:[0-9]{1,2})))|(?:[ex]|ep)([0-9]{1,2}))(?:[^0-9]|$)'),
    ('year', '([\[\(]?(' + year_pattern + ')[\]\)]?)'),
    ('month', '(?:' + year_pattern + ')' + delimiters + '(' + month_pattern + ')' + delimiters + '(?:' + day_pattern + ')'),
    ('day', '(?:' + year_pattern + ')' + delimiters + '(?:' + month_pattern + ')' + delimiters + '(' + day_pattern + ')'),
    ('resolution', '([0-9]{3,4}p|1280x720)'),
    ('quality', ('((?:PPV\.)?[HP]DTV|(?:HD)?CAM-?(?:Rip)?|B[DR]Rip|(?:HD-?)?TS|'
                 'HDRip|HDTVRip|DVDRip|DVDRIP|'
                 '(?:(?:' + producers + ')' + delimiters + '?)?(?:PPV )?W[EB]B(?:-?DL(?:Mux)?)?(?:Rip| DVDRip)?|BluRay|DvDScr|hdtv|telesync)')),
    ('codec', '(xvid|[hx]\.?26[45])'),
    ('audio', ('(MP3|DD5\.?1|Dual[\- ]Audio|LiNE|DTS|DTS5\.1|'
               'AAC[ \.-]LC|AAC(?:(?:\.?2(?:\.0)?)?|(?:\.?5(?:\.1)?)?)|'
               '(?:E-?)?AC-?3(?:' + delimiters + '*?(?:2\.0|5\.1))?)')),
    ('region', 'R[0-9]'),
    ('extended', '(EXTENDED(:?.CUT)?)'),
    ('hardcoded', 'HC'),
    ('proper', 'PROPER'),
    ('repack', 'REPACK'),
    ('container', '(MKV|AVI|MP4)'),
    ('widescreen', 'WS'),
    ('website', '^(\[ ?([^\]]+?) ?\])'),
    ('subtitles', subtitles_pattern + '|(E-?)(?:subs?)'),
    ('language', '(' + lang_list_pattern + '+)(?!' + subtitles_pattern + ')'),
    ('sbs', '(?:Half-)?SBS'),
    ('unrated', 'UNRATED'),
    ('size', '(\d+(?:\.\d+)?(?:GB|MB))'),
    ('bitDepth', '(?:8|10)bit'),
    ('3d', '3D'),
    ('internal', 'iNTERNAL'),
    ('readnfo', 'READNFO')
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
    '3d': 'boolean',
    'internal': 'boolean',
    'readnfo': 'boolean'
}

exceptions = [
    {
        'parsed_title': '',
        'incorrect_parse': ('year', 1983),
        'actual_title': '1983'
     },
    {
        'parsed_title': 'Marvel\'s Agents of S H I E L D',
        'incorrect_parse': ('title', 'Marvel\'s Agents of S H I E L D'),
        'actual_title': 'Marvel\'s Agents of S.H.I.E.L.D.'
    }
]
