#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Patterns are either just a regex, or a tuple (or list of) that contains the regex
# to match, (optional) what it should be replaced with when keep_raw is False (None
# if to not replace), and (optional) a function to transform the value after everything
# (None if to do nothing).

from .extras import get_channel_audio_options

delimiters = '[\.\s\-\+_\/]'
langs = 'rus|(?:True)?fr(?:ench)?|en(?:g(?:lish)?)?|vost(' \
        '?:fr)?|ita(?:liano?)?|castellano|swedish|spanish|dk|german|nordic|exyu|chs|hindi|polish|mandarin'
producers = 'ATVP|AMZN|NF|NICK|RED|DSNP'

season_range_pattern = '(?:Complete' + delimiters + '*)?(?:' + delimiters + '*)?(?:s(?:easons?)?)?' + delimiters + \
                       '?(?:s?[0-9]{1,2}[\s]*(?:\-|(?:\s*to\s*))[\s]*s?[0-9]{1,2})(?:' + delimiters + '*Complete)?'

# Used when matching episodeName in parse.py, when actually matching episodes we use a slightly
# modified version that has a capture group on the episode number (as seen below).
episode_pattern = '(?:(?:[ex]|ep)(?:[0-9]{1,2}(?:-(?:[ex]|ep)?(?:[0-9]{1,2})))|(?:[ex]|ep)(?:[0-9]{1,2}))'

lang_list_pattern = '(?:(?:' + langs + ')' + delimiters + '*)'
subtitles_pattern = '((?:{delimiters})?subs?{delimiters}*({langs}*)|({langs}*)(?:multi{delimiters}*)?subs?)'\
    .format(delimiters=delimiters, langs=lang_list_pattern)  # 'subs' can be at beginning or end

year_pattern = '(?:19[0-9]|20[0-2])[0-9]'
month_pattern = '0[1-9]|1[0-2]'
day_pattern = '[0-2][0-9]|3[01]'

patterns = [
    ('season', delimiters + '('  # Season description can't be at the beginning, must be after this pattern
               '' + season_range_pattern + '|'  # Describes season ranges
               '(?:Complete' + delimiters + ')?s([0-9]{1,2})(?:' + episode_pattern + ')?|'  # Describes season, optionally with complete or episode
               '([0-9]{1,2})x[0-9]{2}|'  # Describes 5x02, 12x15 type descriptions
               '(?:Complete' + delimiters + ')?Season[\. -]([0-9]{1,2})'  # Describes Season.15 type descriptions
               ')(?:' + delimiters + '|$)'),
    ('episode', '[^a-z]((?:[ex]|ep)(?:[0-9]{1,2}(?:-(?:[ex]|ep)?(?:[0-9]{1,2})))|(?:[ex]|ep)([0-9]{1,2}))(?:[^0-9]|$)'),
    ('year', '([\[\(]?(' + year_pattern + ')[\]\)]?)'),
    ('month', '(?:{year}){delimiters}({month}){delimiters}(?:{day})'
     .format(delimiters=delimiters, year=year_pattern, month=month_pattern, day=day_pattern)),
    ('day', '(?:{year}){delimiters}(?:{month}){delimiters}({day})'
     .format(delimiters=delimiters, year=year_pattern, month=month_pattern, day=day_pattern)),
    ('resolution', [('([0-9]{3,4}p)', None, str.lower),
                    ('(1280x720)', '720p')]),
    ('quality', ('((?:PPV\.)?[HP]DTV|(?:HD)?CAM-?(?:Rip)?|B[DR]Rip|(?:HD-?)?TS|'
                 'HDRip|HDTVRip|DVDRip|DVDRIP|'
                 '(?:(?:' + producers + ')' + delimiters + '?)?(?:PPV )?W[EB]B(?:-?DL(?:Mux)?)?(?:Rip| DVDRip)?|BluRay|DvDScr|hdtv|telesync)')),
    ('codec', [('xvid', 'Xvid'),
               ('av1', 'AV1'),
               ('[hx]\.?264', 'H.264'),
               ('[hx]\.?265', 'H.265')]),
    ('audio', ['MP3',
               ('LiNE', 'LiNE'),
               ('Dual[\- ]Audio', 'Dual Audio')
               ] + get_channel_audio_options([
        ('DD|AC-?3', 'Dolby Digital'),
        ('DDP|E-?AC-?3|EC-3', 'Dolby Digital Plus'),
        ('DTS', 'DTS'),
        ('AAC[ \.\-]LC', 'AAC-LC'),
        ('AAC', 'AAC')
    ])
     ),
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
    ('sbs', [('Half-SBS', 'Half-SBS'),
             'SBS']),
    ('unrated', 'UNRATED'),
    ('size', '(\d+(?:\.\d+)?(?:GB|MB))'),
    ('bitDepth', ('(?:8|10)bit', None, str.lower)),
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
