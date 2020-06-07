# Some titles just can't be parsed without breaking everything else, so here
# are known those known exceptions. They are executed when the parsed_title and
# incorrect_parse match within a .parse() dict, removing the latter, and replacing
# the former with actual_title.
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


# Return tuple with regexes for audio name with appended channel types, and without any channels
def get_channel_audio_options(patterns_with_names):
    options = list()
    for (audio_pattern, name) in patterns_with_names:
        for (speakers, subwoofers) in channels:
            options.append(('((?:{})[. \-]*?{}[. \-]?{})'.format(audio_pattern, speakers, subwoofers),
                '{} {}.{}'.format(name, speakers, subwoofers)))
        options.append(('({})'.format(audio_pattern), name))  # After for loop, would match first

    return options


def prefix_pattern_with(prefixes, pattern_options, between='', optional=False):
    if optional:
        optional_char = '?'
    else:
        optional_char = ''
    options = list()
    if not isinstance(prefixes, list):
        prefixes = [prefixes]
    for prefix in prefixes:
        if not isinstance(pattern_options, list):
            pattern_options = [pattern_options]
        for pattern_option in pattern_options:
            if isinstance(pattern_option, str):
                options.append('(?:{}){}(?:{})?({})'.format(prefix, optional_char, between, pattern_option))
            else:
                options.append(('(?:{}){}(?:{})?({})'.format(prefix, optional_char, between, pattern_option[0]),) + pattern_option[1:])

    return options


def suffix_pattern_with(suffixes, pattern_options, between='', optional=False):
    if optional:
        optional_char = '?'
    else:
        optional_char = ''
    options = list()
    if not isinstance(suffixes, list):
        suffixes = [suffixes]
    for suffix in suffixes:
        if not isinstance(pattern_options, list):
            pattern_options = [pattern_options]
        for pattern_option in pattern_options:
            if isinstance(pattern_option, str):
                options.append('({})(?:{})?(?:{}){}'.format(pattern_option, between, suffix, optional_char))
            else:
                options.append(('({})(?:{})?(?:{}){}'.format(pattern_option[0], between, suffix, optional_char),) + pattern_option[1:])

    return options


# Link a regex-tuple list into a single regex (to be able to use elsewhere while
# maintaining standardisation functionality).
def link_pattern_options(pattern_options):
    return '|'.join([pattern_option[0] for pattern_option in pattern_options])
