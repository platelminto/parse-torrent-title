#!/usr/bin/env python
from typing import List, Tuple, Union

# Helper functions and constants for patterns.py

delimiters = r"[\.\s\-\+_\/(),]"

langs = [
    (r"rus(?:sian)?|russo", "Russian"),
    (r"(?:True)?fre?(?:nch)?|fr(?:ench|a|e|anc[eê]s)?", "French"),
    (r"(?:nu)?ita(?:liano?)?", "Italian"),
    (r"castellano|spa(?:nish)?|esp?", "Spanish"),
    (r"swedish", "Swedish"),
    (r"dk|dan(?:ish)?", "Danish"),
    (r"ger(?:man)?|deu(?:tsch)?|alem[aã]o", "German"),
    (r"nordic", "Nordic"),
    (r"exyu", "ExYu"),
    (r"chs|chi(?:nese)?|(?:mand[ae]rin|ch[sn])|chin[eê]s|zh-hans", "Chinese"),
    (r"hin(?:di)?", "Hindi"),
    (r"polish|poland|pl", "Polish"),
    (r"kor(?:ean)?|coreano", "Korean"),
    (r"ben(?:gali)?|bangla", "Bengali"),
    (r"kan(?:nada)?", "Kannada"),
    (r"t[aâ]m(?:il)?", "Tamil"),
    (r"tel(?:ugu)?", "Telugu"),
    (r"mar(?:athi)?", "Marathi"),
    (r"mal(?:ayalam)?", "Malayalam"),
    (r"guj(?:arati)?", "Gujarati"),
    (r"pun(?:jabi)?", "Punjabi"),
    (r"ori(?:ya)?", "Oriya"),
    (r"japanese|ja?p|jpn|japon[eê]s", "Japanese"),
    (r"interslavic", "Interslavic"),
    (r"ara(?:bic)?", "Arabic"),
    (r"urdu", "Urdu"),
    (r"tur(?:kish)?|tr", "Turkish"),
    (r"tailand[eê]s|thai?", "Thai"),
    (r"tagalog", "Tagalog"),
    (r"ind(?:onesian)?", "Indonesian"),
    (r"vie(?:tnamese)?", "Vietnamese"),
    (r"heb(?:rew)?", "Hebrew"),
    (r"gre(?:ek)?", "Greek"),
    (r"cz(?:ech)?", "Czech"),
    (r"hun(?:garian)?", "Hungarian"),
    (r"ukr(?:ainian)?", "Ukrainian"),
    (r"fin(?:nish)?", "Finnish"),
    (r"nor(?:wegian)?", "Norwegian"),
    (r"sin(?:hala)?", "Sinhala"),
    (r"dutch|nl", "Dutch"),
    (r"p[ua]n(?:jabi)?", "Punjabi"),
    (r"por(?:tuguese)?|portugu[eèê]s[ea]?|p[rt]|port?", "Portuguese"),
    (r"alb(?:anian?)?|albanais", "Albanian"),
    (r"egypt(?:ian)?|egy", "Egyptian"),
    (r"en?(?:g(?:lish)?)?|ing(?:l[eéê]s)?", "English"),  # Must be at end, matches just an 'e'
]

genres = [
    (r"Sci-?Fi", "Sci-Fi"),
    (r"Drama", "Drama"),
    (r"Comedy", "Comedy"),
    (r"West(?:\.|ern)?", "Western"),
    (r"Action", "Action"),
    (r"Adventure", "Adventure"),
    (r"Thriller", "Thriller"),
]

# Match strings like "complete series" for tv seasons/series, matching within the final title string.
complete_series = [
    r"(?:the\s)?complete\s(?:series|season|collection)$",
    r"(?:the)\scomplete\s?(?:series|season|collection)?$",
]

# Some titles just can't be parsed without breaking everything else, so here
# are known those known exceptions. They are executed when the parsed_title and
# incorrect_parse match within a .parse() dict, removing the latter, and replacing
# the former with actual_title.
exceptions = [
    {
        "parsed_title": "Marvel's Agents of S H I E L D",
        "incorrect_parse": ("title", "Marvel's Agents of S H I E L D"),
        "actual_title": "Marvel's Agents of S.H.I.E.L.D.",
    },
    {
        "parsed_title": "Marvels Agents of S H I E L D",
        "incorrect_parse": ("title", "Marvels Agents of S H I E L D"),
        "actual_title": "Marvel's Agents of S.H.I.E.L.D.",
    },
    {
        "parsed_title": "Magnum P I",
        "incorrect_parse": ("title", "Magnum P I"),
        "actual_title": "Magnum P.I.",
    },
]

# Patterns that should only try to be matched after the 'title delimiter', either a year
# or a season. So if we have a language in the title it won't cause issues by getting matched.
# Empty list indicates to always do so, as opposed to matching specific regexes.
patterns_ignore_title = {
    "languages": [],
    "audio": [r"LiNE"],
    "network": [r"Hallmark"],
    "untouched": [],
    "internal": [],
    "limited": [],
    "proper": [],
    "extended": [rf"(EXTENDED{delimiters}(?!(?:CUT|EDITIONS?)))"],
}

channels = [(1, 0), (2, 0), (5, 0), (5, 1), (6, 1), (7, 1)]


# Return tuple with regexes for audio name with appended channel types, and without any channels
def get_channel_audio_options(patterns_with_names: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    options = []
    for audio_pattern, name in patterns_with_names:
        for speakers, subwoofers in channels:
            options.append(
                (
                    rf"((?:{audio_pattern}){delimiters}*{speakers}[. \-]?{subwoofers}(?:ch)?)",
                    f"{name} {speakers}.{subwoofers}",
                )
            )
        options.append((rf"({audio_pattern})", name))  # After for loop, would match first
    return options


def prefix_pattern_with(prefixes: Union[str, List[str]], pattern_options: Union[str, List[Union[str, Tuple]]], between: str = "", optional: bool = False) -> List[Union[str, Tuple]]:
    optional_char = "?" if optional else ""
    options = []
    if not isinstance(prefixes, list):
        prefixes = [prefixes]
    for prefix in prefixes:
        if not isinstance(pattern_options, list):
            pattern_options = [pattern_options]
        for pattern_option in pattern_options:
            if isinstance(pattern_option, str):
                options.append(
                    rf"(?:{prefix}){optional_char}(?:{between})?({pattern_option})"
                )
            else:
                options.append(
                    (
                        rf"(?:{prefix}){optional_char}(?:{between})?({pattern_option[0]})",
                    ) + pattern_option[1:]
                )
    return options


def suffix_pattern_with(suffixes: Union[str, List[str]], pattern_options: Union[str, List[Union[str, Tuple]]], between: str = "", optional: bool = False) -> List[Union[str, Tuple]]:
    optional_char = "?" if optional else ""
    options = []
    if not isinstance(suffixes, list):
        suffixes = [suffixes]
    for suffix in suffixes:
        if not isinstance(pattern_options, list):
            pattern_options = [pattern_options]
        for pattern_option in pattern_options:
            if isinstance(pattern_option, tuple):
                options.append(
                    (
                        rf"({pattern_option[0]})(?:{between})?(?:{suffix}){optional_char}",
                    ) + pattern_option[1:]
                )
            else:
                options.append(
                    rf"({pattern_option})(?:{between})?(?:{suffix}){optional_char}"
                )
    return options


def link_patterns(pattern_options: Union[str, List[Union[str, Tuple]]]) -> str:
    if not isinstance(pattern_options, list):
        return pattern_options
    return rf"(?:{'|'.join([pattern_option[0] if isinstance(pattern_option, tuple) else pattern_option for pattern_option in pattern_options])})"
