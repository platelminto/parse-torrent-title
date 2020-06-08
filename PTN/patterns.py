#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Patterns are either just a regex, or a tuple (or list of) that contains the regex
# to match, (optional) what it should be replaced with when keep_raw is False (None
# if to not replace), and (optional) a string function's name to transform the value
# after everything (None if to do nothing).

from .extras import *

delimiters = '[\.\s\-\+_\/]'
langs = [('rus(?:sian)?', 'Russian'),
         ('(?:True)?fr(?:ench)?', 'French'),
         ('ita(?:liano?)?', 'Italian'),
         ('castellano|spanish', 'Spanish'),
         ('swedish', 'Swedish'),
         ('dk|danish', 'Danish'),
         ('german', 'German'),
         ('nordic', 'Nordic'),
         ('exyu', 'ExYu'),
         ('chs', 'Chinese'),
         ('hindi', 'Hindi'),
         ('polish', 'Polish'),
         ('mandarin', 'Mandarin'),
         ('kor(?:ean)?', 'Korean'),
         ('en?(?:g(?:lish)?)?', 'English')  # Must be at end, matches just an 'e'
         ]

season_range_pattern = '(?:Complete' + delimiters + '*)?(?:' + delimiters + '*)?(?:s(?:easons?)?)?' + delimiters + \
                       '?(?:s?[0-9]{1,2}[\s]*(?:\-|(?:\s*to\s*))[\s]*s?[0-9]{1,2})(?:' + delimiters + '*Complete)?'

lang_list_pattern = '(?:(?:' + link_pattern_options(langs) + ')' + delimiters + '*)'

year_pattern = '(?:19[0-9]|20[0-2])[0-9]'
month_pattern = '0[1-9]|1[0-2]'
day_pattern = '[0-2][0-9]|3[01]'

# Forces an order to go by the regexes, as we want this to be deterministic (different
# orders can generate different matchings). e.g. "doctor_who_2005..." in input.json
patterns_ordered = ['season', 'episode', 'year', 'month', 'day', 'resolution', 'quality',
                    'producer', 'codec', 'audio', 'region', 'extended', 'hardcoded', 'proper',
                    'repack', 'container', 'widescreen', 'website', 'subtitles', 'language',
                    'sbs', 'unrated', 'size', 'bitDepth', '3d', 'internal', 'readnfo']


patterns = dict()
patterns['episode'] = '(?<![a-z])(?:[ex]|ep)(?:[0-9]{1,2}(?:-(?:[ex]|ep)?(?:[0-9]{1,2}))?)(?![0-9])'
patterns['season'] = (delimiters + '('  # Season description can't be at the beginning, must be after this pattern
                     '' + season_range_pattern + '|'  # Describes season ranges
                     '(?:Complete' + delimiters + ')?s([0-9]{1,2})(?:' + patterns['episode'] + ')?|'  # Describes season, optionally with complete or episode
                     '([0-9]{1,2})x[0-9]{2}|'  # Describes 5x02, 12x15 type descriptions
                     '(?:Complete' + delimiters + ')?Season[\. -]([0-9]{1,2})'  # Describes Season.15 type descriptions
                     ')(?:' + delimiters + 'Complete)?(?:' + delimiters + '|$)')
patterns['year'] = '((' + year_pattern + '))'
patterns['month'] = '(?:{year}){delimiters}({month}){delimiters}(?:{day})' \
    .format(delimiters=delimiters, year=year_pattern, month=month_pattern, day=day_pattern)
patterns['day'] = '(?:{year}){delimiters}(?:{month}){delimiters}({day})' \
    .format(delimiters=delimiters, year=year_pattern, month=month_pattern, day=day_pattern)
patterns['resolution'] = [('([0-9]{3,4}p)', None, 'lower'),
                          ('(1280x720)', '720p')]
patterns['quality'] = [('WEB[ -]?DL(?:Rip|Mux)?|HDRip', 'WEB-DL'),
                       # Match WEB-DL's first as they can show up with others.
                       ('WEB[ -]?Cap', 'WEBCap'),
                       ('W[EB]B[ -]?(?:Rip)|WEB', 'WEBRip'),
                       ('(?:HD)?CAM(?:-?Rip)?', 'Cam'),
                       ('(?:HD)?TS|TELESYNC|PDVD|PreDVDRip', 'Telesync'),
                       ('WP|WORKPRINT', 'Workprint'),
                       ('(?:HD)?TC|TELECINE', 'Telecine'),
                       ('(?:DVD)?SCR(?:EENER)?|BDSCR', 'Screener'),
                       ('DDC', 'Digital Distribution Copy'),
                       ('DVD(?:Rip|Mux)', 'DVD-Rip'),
                       ('DVDR|DVD-Full|Full-rip', 'DVD-R'),
                       ('PDTV|DVBRip', 'PDTV'),
                       ('DSR(?:ip)?|SATRip|DTHRip', 'DSRip'),
                       ('HDTV(?:Rip)?', 'HDTV'),
                       ('D?TVRip|DVBRip', 'TVRip'),
                       ('VODR(?:ip)?', 'VODRip'),
                       ('HD-Rip', 'HD-Rip'),
                       ('Blu-?Ray', 'Blu-ray'),
                       ('BD?R(?:ip)|BDR', 'BDRip'),
                       ('BRRip', 'BRRip'),
                       # Match this last as it can show up with others.
                       ('PPV(?:Rip)?', 'Pay-Per-View Rip')]
patterns['producer'] = [('(ATVP)', 'Apple TV+'),
              ('AMZN', 'Amazon Studios'),
              ('NF|Netflix', 'Netflix'),
              ('NICK', 'Nickelodeon'),
              ('RED', 'YouTube Premium'),
              ('DSNP', 'Disney Plus')]
patterns['producer'] = suffix_pattern_with(link_pattern_options(patterns['quality']),
                                           patterns['producer'], delimiters)
patterns['codec'] = [('xvid', 'Xvid'),
                     ('av1', 'AV1'),
                     ('[hx]\.?264', 'H.264'),
                     ('[hx]\.?265', 'H.265'),
                     ('HEVC', 'H.265')]
patterns['audio'] = [('MP3', None, 'upper'),
                     ('LiNE', 'LiNE'),
                     ('Dual[\- ]Audio', 'Dual Audio')
                     ] + get_channel_audio_options([
    ('DD|AC-?3', 'Dolby Digital'),
    ('DDP|E-?AC-?3|EC-3', 'Dolby Digital Plus'),
    ('DTS', 'DTS'),
    ('AAC[ \.\-]LC', 'AAC-LC'),
    ('AAC', 'AAC')
])
patterns['region'] = ('R[0-9]', None, 'upper')
patterns['extended'] = '(EXTENDED(:?.CUT)?)'
patterns['hardcoded'] = 'HC'
patterns['proper'] = 'PROPER'
patterns['repack'] = 'REPACK'
patterns['container'] = ('(MKV|AVI|MP4)', None, 'upper')
patterns['widescreen'] = 'WS'
patterns['website'] = '^(\[ ?([^\]]+?) ?\])'
patterns['subtitles'] = '((?:{delimiters})?subs?{delimiters}*({langs}*)|({langs}*)(?:multi{delimiters}*)?subs?)' \
    .format(delimiters=delimiters, langs=lang_list_pattern)  # 'subs' can be at beginning or end + '|-?(?:subs?)'
patterns['language'] = '(' + lang_list_pattern + '+)(?!' + patterns['subtitles'] + ')'
patterns['sbs'] = [('Half-SBS', 'Half SBS'),
                   ('SBS', None, 'upper')]
patterns['unrated'] = 'UNRATED'
patterns['size'] = ('(\d+(?:\.\d+)?(?:GB|MB))', None, 'upper')
patterns['bitDepth'] = '((8|10)bit)'
patterns['3d'] = '3D'
patterns['internal'] = 'iNTERNAL'
patterns['readnfo'] = 'READNFO'

types = {
    'season': 'integer',
    'episode': 'integer',
    'bitDepth': 'integer',
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
