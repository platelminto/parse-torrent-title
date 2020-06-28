#!/usr/bin/env python

# Patterns are either just a regex, or a tuple (or list of tuples) that contain the regex
# to match, (optional) what it should be replaced with (None if to not replace), and
# (optional) a string function's name to transform the value after everything (None if
# to do nothing). The transform can also be a tuple (or list of tuples) with function names
# and list of arguments.
# The list of regexes all get matched, but only the first gets added to the returning info,
# the rest are just matched to be removed from `excess`.

from .extras import *

delimiters = '[\.\s\-\+_\/]'
langs = [('rus(?:sian)?', 'Russian'),
         ('(?:True)?fre?(?:nch)?', 'French'),
         ('(?:nu)?ita(?:liano?)?', 'Italian'),
         ('castellano|spanish|es', 'Spanish'),
         ('swedish', 'Swedish'),
         ('dk|dan(?:ish)?', 'Danish'),
         ('german', 'German'),
         ('nordic', 'Nordic'),
         ('exyu', 'ExYu'),
         ('chs', 'Chinese'),
         ('hin(?:di)?', 'Hindi'),
         ('polish', 'Polish'),
         ('mandarin', 'Mandarin'),
         ('kor(?:ean)?', 'Korean'),
         ('bengali|bangla', 'Bengali'),
         ('kannada', 'Kannada'),
         ('tam(?:il)?', 'Tamil'),
         ('tel(?:ugu)?', 'Telugu'),
         ('marathi', 'Marathi'),
         ('mal(?:ayalam)?', 'Malayalam'),
         ('japanese|jp', 'Japanese'),
         ('interslavic', 'Interslavic'),
         ('ara(?:bic)?', 'Arabic'),
         ('en?(?:g(?:lish)?)?', 'English')  # Must be at end, matches just an 'e'
         ]

season_range_pattern = '(?:Complete' + delimiters + '*)?' + delimiters + '*(?:s(?:easons?)?)' + delimiters + \
                       '*(?:s?[0-9]{1,2}[\s]*(?:(?:\-|(?:\s*to\s*))[\s]*s?[0-9]{1,2})+)(?:' + delimiters + '*Complete)?'

lang_list_pattern = r'\b(?:' + link_patterns(langs) + '(?:' + delimiters + r'|\b)+)'
subs_list_pattern = r'\b(?:' + link_patterns(langs) + delimiters + '*)'

year_pattern = '(?:19[0-9]|20[0-2])[0-9]'
month_pattern = '0[1-9]|1[0-2]'
day_pattern = '[0-2][0-9]|3[01]'

episode_name_pattern = '((?:[Pp](?:ar)?t' + delimiters + '*[0-9]|[A-Za-z][a-z]*(?:' + delimiters + \
                       '|$))+)'

# Forces an order to go by the regexes, as we want this to be deterministic (different
# orders can generate different matchings). e.g. "doctor_who_2005..." in input.json
patterns_ordered = ['season', 'episode', 'year', 'month', 'day', 'resolution', 'quality',
                    'codec', 'audio', 'region', 'extended', 'hardcoded', 'proper', 'repack',
                    'container', 'widescreen', 'website', 'documentary', 'language', 'subtitles',
                    'sbs', 'unrated', 'size', 'bitDepth', '3d', 'internal', 'readnfo', 'network',
                    'fps', 'hdr']

patterns = dict()
patterns['episode'] = ['(?<![a-z])(?:[ex]|ep)(?:[0-9]{1,2}(?:-(?:[ex]|ep)?(?:[0-9]{1,2}))?)(?![0-9])',
                       '\s\-\s\d{1,3}\s'  # Very specific as it could match too liberally otherwise
                       ]
patterns['season'] = ['\ss?(\d{1,2})\s\-\s\d{1,2}\s',  # Avoids matching some anime releases season and episode as a season range
                      r'\b' + season_range_pattern + r'\b',  # Describes season ranges
                      # Describes season, optionally with complete or episode
                      r'\b(?:Complete' + delimiters + ')?s([0-9]{1,2})' + link_patterns(patterns['episode']) + r'?\b',
                      r'\b([0-9]{1,2})x[0-9]{2}\b',  # Describes 5x02, 12x15 type descriptions
                      '[0-9]{1,2}(?:st|nd|rd|th)' + delimiters + 'season',
                      r'\b(?:Complete' + delimiters + r')?Season[\. -][0-9]{1,2}\b',  # Describes Season.15 type descriptions
                      ]
# The first 4 season regexes won't have 'Part' in them.
patterns['episode'] += [link_patterns(patterns['season'][4:]) + delimiters + '*P(?:ar)?t' + delimiters + '*(\d{1,3})']
patterns['year'] = '((' + year_pattern + '))'
patterns['month'] = '(?:{year}){delimiters}({month}){delimiters}(?:{day})' \
    .format(delimiters=delimiters, year=year_pattern, month=month_pattern, day=day_pattern)
patterns['day'] = '(?:{year}){delimiters}(?:{month}){delimiters}({day})' \
    .format(delimiters=delimiters, year=year_pattern, month=month_pattern, day=day_pattern)
patterns['resolution'] = [('([0-9]{3,4}p)', None, 'lower'),
                          ('(1280x720p?)', '720p'),
                          ('FHD', '1080p'),
                          ('HD', 'HD'),
                          ('4K', '4K')]
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
                       ('DVD-?(?:Rip|Mux)', 'DVD-Rip'),
                       ('DVDR|DVD-Full|Full-rip', 'DVD-R'),
                       ('PDTV|DVBRip', 'PDTV'),
                       ('DSR(?:ip)?|SATRip|DTHRip', 'DSRip'),
                       ('HDTV(?:Rip)?', 'HDTV'),
                       ('D?TVRip|DVBRip', 'TVRip'),
                       ('VODR(?:ip)?', 'VODRip'),
                       ('HD-Rip', 'HD-Rip'),
                       ('Blu-?Ray', 'Blu-ray'),
                       ('BD?R(?:ip)|BDR', 'BDRip'),
                       ('BR-?Rip', 'BRRip'),
                       # Match this last as it can show up with others.
                       ('PPV(?:Rip)?', 'Pay-Per-View Rip')]
patterns['network'] = [('ATVP', 'Apple TV+'),
                        ('AMZN', 'Amazon Studios'),
                        ('NF|Netflix', 'Netflix'),
                        ('NICK', 'Nickelodeon'),
                        ('RED', 'YouTube Premium'),
                        ('DSNY?P', 'Disney Plus'),
                        ('HMAX', 'HBO Max'),
                        ('HULU', 'Hulu Networks'),
                        ('MS?NBC', 'MSNBC'),
                        ('DCU', 'DC Universe'),
                        ]
patterns['network'] = suffix_pattern_with(link_patterns(patterns['quality']),
                                          patterns['network'], delimiters)
# Not all networks always show up just before the quality.
patterns['network'] += [('BBC', 'BBC'),
                        ('Hoichoi', 'Hoichoi'),
                        ('Zee5', 'ZEE5'),
                        ]
patterns['codec'] = [('xvid', 'Xvid'),
                     ('av1', 'AV1'),
                     ('[hx]\.?264', 'H.264'),
                     ('AVC', 'H.264'),
                     ('[hx]\.?265', 'H.265'),
                     ('HEVC', 'H.265'),
                     ('[h]\.?263', 'H.263')]
patterns['audio'] = get_channel_audio_options([
    ('TrueHD', 'Dolby TrueHD'),
    ('Atmos', 'Dolby Atmos'),
    ('DD|AC-?3', 'Dolby Digital'),
    ('DDP|E-?AC-?3|EC-3', 'Dolby Digital Plus'),
    ('DTS{delimiters}?HD(?:{delimiters}?(?:MA|Masters?(?:{delimiters}Audio)?))'.format(delimiters=delimiters), 'DTS-HD MA'),
    ('DTS{delimiters}?HD'.format(delimiters=delimiters), 'DTS-HD'),
    ('DTS', 'DTS'),
    ('AAC[ \.\-]LC', 'AAC-LC'),
    ('AAC', 'AAC'),
    ('Dual[\- ]Audio', 'Dual')
]) + [('5.1(?:' + delimiters + '?ch(?:annel)?(?:' + delimiters + '?Audio)?)?', '5.1'),
      ('2.0(?:' + delimiters + '?ch(?:annel)?(?:' + delimiters + '?Audio)?)?', 'Dual'),
      ('7.1(?:' + delimiters + '?ch(?:annel)?(?:' + delimiters + '?Audio)?)?', '7.1'),
      ('1' + delimiters + '?Ch(?:annel)?(?:' + delimiters + '?Audio)?', 'Mono'),
      ('FLAC', 'FLAC'),
      ('MP3', None, 'upper'),
      ('LiNE', 'LiNE'),
      ]
patterns['region'] = ('R[0-9]', None, 'upper')
patterns['extended'] = '(EXTENDED(:?.CUT)?)'
patterns['hardcoded'] = 'HC'
patterns['proper'] = 'PROPER'
patterns['repack'] = 'REPACK'
patterns['fps'] = '([1-9][0-9]{1,2})' + delimiters + '*fps'
patterns['container'] = [('MKV|AVI', None, 'upper'),
                          ('MP-?4', 'MP4')]
patterns['widescreen'] = 'WS'
patterns['website'] = '^(\[ ?([^\]]+?) ?\])'
patterns['subtitles'] = ['sub(?:title)?s?{delimiters}*{langs}+'.format(delimiters=delimiters, langs=subs_list_pattern),
                         '(?:soft{delimiters}*)?{langs}+(?:(?:m(?:ulti(?:ple)?)?{delimiters}*)?sub(?:title)?s?)'.format(delimiters=delimiters, langs=subs_list_pattern),
                         # Need a pattern just for subs, and can't just make above regexes * over + as we want
                         # just 'subs' to match last.
                         '(?:m(?:ulti(?:ple)?)?{delimiters}*)sub(?:title)?s?'.format(delimiters=delimiters),
                         '(?:m(?:ulti(?:ple)?)?[\.\s\-\+_\/]*)?sub(?:title)?s?{delimiters}*'.format(delimiters=delimiters),
                        ]
# Language takes precedence over subs when ambiguous - if we have a lang match, and
# then a subtitles match starting with subs, the first langs are languages, and the
# rest will be left as subtitles. Otherwise, don't match if there are subtitles matches
# after the langs.
patterns['language'] = ['(' + lang_list_pattern + '+)(?:' + delimiters + '*' + patterns['subtitles'][0] + ')',
                        '(' + lang_list_pattern + '+)(?!' + delimiters + '*' + link_patterns(patterns['subtitles']) + ')',
                        '(' + lang_list_pattern + '+)(?:' + delimiters + '*' + patterns['subtitles'][2] + ')',
                        ]
patterns['sbs'] = [('Half-SBS', 'Half SBS'),
                   ('SBS', None, 'upper')]
patterns['unrated'] = 'UNRATED'
patterns['size'] = ('\d+(?:\.\d+)?\s?(?:GB|MB)', None, [('upper', []), ('replace', [' ', ''])])
patterns['bitDepth'] = '(8|10)bits?'
patterns['3d'] = '3D'
patterns['internal'] = 'iNTERNAL'
patterns['readnfo'] = 'READNFO'
patterns['hdr'] = 'HDR'
patterns['documentary'] = 'DOCU(?:menta?ry)?'

types = {
    'season': 'integer',
    'episode': 'integer',
    'bitDepth': 'integer',
    'year': 'integer',
    'month': 'integer',
    'day': 'integer',
    'fps': 'integer',
    'extended': 'boolean',
    'hardcoded': 'boolean',
    'proper': 'boolean',
    'repack': 'boolean',
    'widescreen': 'boolean',
    'unrated': 'boolean',
    '3d': 'boolean',
    'internal': 'boolean',
    'readnfo': 'boolean',
    'documentary': 'boolean',
    'hdr': 'boolean'
}
