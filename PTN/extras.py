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

# Patterns that should only try to be matched after the 'title delimiter', either a year
# or a season. So if we have a language in the title it won't cause issues by getting matched.
# Empty list indicates to always do so, as opposed to matching specific regexes.
patterns_ignore_title = [('language', []), ('audio', ['LiNE'])]


channels = [(2, 0), (5, 1), (7, 1)]
dd_pattern = 'DD|AC-?3'
ddp_pattern = 'DDP|E-?AC-?3|EC-3'


# Return tuple with regexes for audio name with appended channel types
def get_channel_audio_options(patterns_with_names):
    options = list()
    for (audio_pattern, name) in patterns_with_names:
        for (speakers, subwoofers) in channels:
            options.append(('((?:{})[. \-]*?{}[. \-]?{})'.format(audio_pattern, speakers, subwoofers),
                '{} {}.{}'.format(name, speakers, subwoofers)))
        options.append(('({})'.format(audio_pattern), name))  # After for loop, would match first

    return options


def get_audio_options():
    # These don't need channels appended
    audios = ['MP3',
     ('LiNE', 'LiNE'),
     ('Dual[\- ]Audio', 'Dual Audio')
     ]

    audios.extend(get_channel_audio_options([
        (dd_pattern, 'Dolby Digital'),
        (ddp_pattern, 'Dolby Digital Plus'),
        ('DTS', 'DTS'),
        ('AAC[ \.\-]LC', 'AAC-LC'),
        ('AAC', 'AAC')
    ]))

    return audios
