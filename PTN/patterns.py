#!/usr/bin/env python

from .extras import (
    delimiters,
    genres,
    get_channel_audio_options,
    langs,
    link_patterns,
    suffix_pattern_with,
)

# Patterns are either just a regex, or a tuple (or list of tuples) that contain the regex
# to match, (optional) what it should be replaced with (None if to not replace), and
# (optional) a string function's name to transform the value after everything (None if
# to do nothing). The transform can also be a tuple (or list of tuples) with function names
# and list of arguments.
# The list of regexes all get matched, but only the first gets added to the returning info,
# the rest are just matched to be removed from `excess`.


season_range_pattern = (
    rf"(?:Complete{delimiters}*)?{delimiters}*(?:s(?:easons?)?){delimiters}*(?:s?[0-9]{{1,2}}[\s]*(?:(?:\-|(?:\s*to\s*))[\s]*s?[0-9]{{1,2}}))(?:{delimiters}*Complete)?"
)

year_pattern = r"(?:19[0-9]|20[0-2])[0-9]"
month_pattern = r"0[1-9]|1[0-2]"
day_pattern = r"[0-2][0-9]|3[01]"

episode_name_pattern = rf"((?:[Pp](?:ar)?t{delimiters}*[0-9]|(?:[A-Za-z]|[0-9])[a-z]*(?:{delimiters}|$))+)"
pre_website_encoder_pattern = r"[^\s\.\[\]\-\(\)]+\)\s*\[[^\s\-]+\]|[^\s\.\[\]\-\(\)]+\s*(?:-\s)?[^\s\.\[\]\-]+$"

# Forces an order to go by the regexes, as we want this to be deterministic (different
# orders can generate different matchings). e.g. "doctor_who_2005..." in input.json
patterns_ordered = [
    "resolution",
    "quality",
    "seasons",
    "episodes",
    "year",
    "month",
    "day",
    "codec",
    "audio",
    "region",
    "extended",
    "hardcoded",
    "proper",
    "repack",
    "filetype",
    "widescreen",
    "sbs",
    "site",
    "documentary",
    "languages",
    "subtitles",
    "unrated",
    "size",
    "bitDepth",
    "3d",
    "internal",
    "readnfo",
    "network",
    "fps",
    "hdr",
    "limited",
    "remastered",
    "directorsCut",
    "upscaled",
    "untouched",
    "remux",
    "internationalCut",
    "genres",
]


# Some patterns overlap with others. Season & episodes do this a lot. Without something like this, we'd get issues like
# the Avatar test: ... Complete Series 1080p ... 'Series 10' would be matched as a season, but the 10 is
# from 1080p, which also gets matched.
patterns_allow_overlap = [
    "seasons",
    "episodes",
    "languages",
    "subtitles",
    "sbs",
]

patterns = {}
patterns["episodes"] = [
    r"(?<![a-z])(?:e|ep)(?:\(?[0-9]{1,2}(?:-?(?:e|ep)?(?:[0-9]{1,2}))?\)?)(?![0-9])",
    # Very specific as it could match too liberally
    r"\s\-\s\d{1,3}\s",
    r"\b[0-9]{1,2}x([0-9]{2})\b",
    rf"\bepisod(?:e|io){delimiters}\d{{1,2}}\b",
]
# If adding seasons patterns, remember to look at episodes, as it uses the last few!
patterns["seasons"] = [
    rf"\b(?:Seasons?){delimiters}(\d{{1,2}})(?:(?:{delimiters}|&|and|to){{1,3}}(\d{{1,2}})){{2,}}\b",
    r"\ss?(\d{1,2})\s\-\s\d{1,2}\s",  # Avoids matching some anime releases seasons and episodes as a season range
    rf"\b{season_range_pattern}\b",  # Describes season ranges
    r"(?:s\d{1,2}[.+\s]*){2,}\b",  # for S01.S02.etc. patterns
    # Describes season, optionally with complete or episodes
    rf"\b(?:Complete{delimiters})?s([0-9]{{1,2}}){link_patterns(patterns['episodes'])}?\b",
    r"\b([0-9]{1,2})x[0-9]{2}\b",  # Describes 5x02, 12x15 type descriptions
    rf"[0-9]{{1,2}}(?:st|nd|rd|th){delimiters}season",
    rf"Series{delimiters}\d{{1,2}}",
    rf"\b(?:Complete{delimiters})?Season[\. -][0-9]{{1,2}}\b",  # Describes Season.15 type descriptions
]
# The first 4 season regexes won't have 'Part' in them.
patterns["episodes"] += [
    rf"{link_patterns(patterns['seasons'][6:])}{delimiters}*P(?:ar)?t{delimiters}*(\d{{1,3}})",
]
patterns["year"] = year_pattern
patterns["month"] = rf"(?:{year_pattern}){delimiters}({month_pattern}){delimiters}(?:{day_pattern})"
patterns["day"] = rf"(?:{year_pattern}){delimiters}(?:{month_pattern}){delimiters}({day_pattern})"
# resolution pattern according to https://ihax.io/display-resolution-explained/ and GPT4.
# order from highest to lowest due to some torrent name having '4K HD' in them but its technically 4K.
patterns["resolution"] = [
    (r"([0-9]{3,4}(?:p|i))", None, "lower"),  # Generic pattern for resolutions like 480p, 720p, 1080p, etc.
    (rf"(8K|7680{delimiters}?x{delimiters}?4320p?)", "8K"),  # Pattern for 8K
    (rf"(5K|5120{delimiters}?x{delimiters}?2880p?)", "5K"),  # Pattern for 5K
    (rf"(4K UHD|UHD|3840{delimiters}?x{delimiters}?2160p?)", "2160p"),  # Pattern for 4K UHD / 2160p
    (rf"(4K|4096{delimiters}?x{delimiters}?2160p?)", "4K"),  # Pattern for 4K / Cinema 4K
    (rf"(QHD|QuadHD|WQHD|2560{delimiters}?x{delimiters}?1440p?)", "1440p"),  # Pattern for QHD / 1440p
    (rf"(2K|2048{delimiters}?x{delimiters}?1080p?)", "2K"),  # Pattern for 2K
    (rf"(Full HD|FHD|1920{delimiters}?x{delimiters}?1080p?)", "1080p"),  # Pattern for Full HD / 1080p
    (rf"(HD|1280{delimiters}?x{delimiters}?720p?)", "720p"),  # Pattern for HD / 720p
    (r"(qHD)", "540p"),  # Pattern for quarter High Definition
    (r"(SD)", "480p"),  # Pattern for Standard Definition
]

patterns["quality"] = [
    (r"WEB[ -\.]?DL(?:Rip|Mux)?|HDRip", "WEB-DL"),
    # Match WEB-DL's first as they can show up with others.
    (r"WEB[ -]?Cap", "WEBCap"),
    (r"W[EB]B[ -]?(?:Rip)|WEB", "WEBRip"),
    (r"(?:HD)?CAM(?:-?Rip)?", "Cam"),
    (r"(?:HD)?TS|TELESYNC|PDVD|PreDVDRip", "Telesync"),
    (r"WP|WORKPRINT", "Workprint"),
    (r"(?:HD)?TC|TELECINE", "Telecine"),
    (r"(?:DVD)?SCR(?:EENER)?|BDSCR", "Screener"),
    (r"DDC", "Digital Distribution Copy"),
    (r"DVD-?(?:Rip|Mux)", "DVD-Rip"),
    (r"DVDR|DVD-Full|Full-rip", "DVD-R"),
    (r"PDTV|DVBRip", "PDTV"),
    (r"DSR(?:ip)?|SATRip|DTHRip", "DSRip"),
    (r"AHDTV(?:Mux)?", "AHDTV"),
    (r"HDTV(?:Rip)?", "HDTV"),
    (r"D?TVRip|DVBRip", "TVRip"),
    (r"VODR(?:ip)?", "VODRip"),
    (r"HD-Rip", "HD-Rip"),
    (rf"Blu-?Ray{delimiters}Rip|BDR(?:ip)?", "BDRip"),
    (r"Blu-?Ray|(?:US|JP)?BD(?:remux)?", "Blu-ray"),
    (r"BR-?Rip", "BRRip"),
    (r"HDDVD", "HD DVD"),
    # Match this last as it can show up with others.
    (r"PPV(?:Rip)?", "Pay-Per-View Rip"),
]
patterns["network"] = [
    ("ATVP", "Apple TV+"),
    ("AMZN|Amazon", "Amazon Studios"),
    ("NF|Netflix", "Netflix"),
    ("NICK", "Nickelodeon"),
    ("RED", "YouTube Premium"),
    ("DSNY?P", "Disney Plus"),
    ("DSNY", "DisneyNOW"),
    ("HMAX", "HBO Max"),
    ("HBO", "HBO"),
    ("HULU", "Hulu Networks"),
    ("MS?NBC", "MSNBC"),
    ("DCU", "DC Universe"),
    ("ID", "Investigation Discovery"),
    ("iT", "iTunes"),
    ("AS", "Adult Swim"),
    ("CRAV", "Crave"),
    ("CC", "Comedy Central"),
    ("SESO", "Seeso"),
    ("VRV", "VRV"),
    ("PCOK", "Peacock"),
    ("CBS", "CBS"),
    ("iP", "BBC iPlayer"),
    ("NBC", "NBC"),
    ("AMC", "AMC"),
    ("PBS", "PBS"),
    ("STAN", "Stan."),
    ("RTE", "RTE Player"),
    ("CR", "Crunchyroll"),
    ("ANPL", "Animal Planet Live"),
    ("DTV", "DirecTV Stream"),
    ("VICE", "VICE"),
]
patterns["network"] = suffix_pattern_with(
    link_patterns(patterns["quality"]), patterns["network"], delimiters
)
# Not all networks always show up just before the quality, so if they're unlikely to clash,
# they should be added here.
patterns["network"] += [
    ("BBC", "BBC"),
    ("Hoichoi", "Hoichoi"),
    ("Zee5", "ZEE5"),
    ("Hallmark", "Hallmark"),
    ("Sony\s?LIV", "SONY LIV"),
]

patterns["codec"] = [
    (r"xvid", "Xvid"),
    (r"av1", "AV1"),
    (rf"[hx]{delimiters}?264", "H.264"),
    (r"AVC", "H.264"),
    (rf"HEVC(?:{delimiters}Main{delimiters}?10P?)", "H.265 Main 10"),
    (rf"[hx]{delimiters}?265", "H.265"),  # Separate from HEVC so if both are present, it won't pollute excess.
    (r"HEVC", "H.265"),
    (rf"[h]{delimiters}?263", "H.263"),
    (r"VC-1", "VC-1"),
    (rf"MPEG{delimiters}?2", "MPEG-2"),
]

patterns["audio"] = get_channel_audio_options(
    [
        (r"TrueHD", "Dolby TrueHD"),
        (r"Atmos", "Dolby Atmos"),
        (rf"DD{delimiters}?EX", "Dolby Digital EX"),
        (rf"DD|AC{delimiters}?3|DolbyD", "Dolby Digital"),
        (rf"DDP|E{delimiters}?AC{delimiters}?3|EC{delimiters}?3", "Dolby Digital Plus"),
        (rf"DTS{delimiters}?HD(?:{delimiters}?(?:MA|Masters?(?:{delimiters}Audio)?))", "DTS-HD MA"),
        (r"DTSMA", "DTS-HD MA"),
        (rf"DTS{delimiters}?HD", "DTS-HD"),
        (rf"DTS{delimiters}?ES", "DTS-ES"),
        (rf"DTS{delimiters}?EX", "DTS-EX"),
        (rf"DTS{delimiters}?X", "DTS:X"),
        (r"DTS", "DTS"),
        (rf"HE{delimiters}?AAC", "HE-AAC"),
        (rf"HE{delimiters}?AACv2", "HE-AAC v2"),
        (rf"AAC{delimiters}?LC", "AAC-LC"),
        (r"AAC", "AAC"),
        (rf"Dual{delimiters}Audios?", "Dual"),
        (rf"Custom{delimiters}Audios?", "Custom"),
        (r"FLAC", "FLAC"),
        (r"OGG", "OGG"),
    ]
) + [
    (rf"7.1(?:{delimiters}?ch(?:annel)?(?:{delimiters}?Audio)?)?", "7.1"),
    (rf"5.1(?:{delimiters}?ch(?:annel)?(?:{delimiters}?Audio)?)?", "5.1"),
    (r"MP3", None, "upper"),
    (rf"2.0(?:{delimiters}?ch(?:annel)?(?:{delimiters}?Audio)?)?|2CH|stereo", "Dual"),
    (rf"1{delimiters}?Ch(?:annel)?(?:{delimiters}?Audio)?", "Mono"),
    (rf"(?:Original|Org){delimiters}Aud(?:io)?", "Original"),
    (r"LiNE", "LiNE"),
]

patterns["region"] = (r"R[0-9]", None, "upper")

# If changing below, remember to change patterns_ignore_title (in extras.py) too.
patterns["extended"] = [
    r"(EXTENDED)",
    rf"(EXTENDED{delimiters}(?:(?:CUT|EDITIONS?)))",
]

patterns["hardcoded"] = r"HC"
patterns["proper"] = r"PROPER"
patterns["repack"] = r"REPACK"
patterns["fps"] = rf"([1-9][0-9]{{1,2}}){delimiters}*fps"
patterns["filetype"] = [
    (r"\.?(MKV|AVI|(?:SRT|SUB|SSA)$)", None, "upper"),
    (r"MP-?4", "MP4"),
    (r"\.?(iso)$", "ISO"),
]
patterns["widescreen"] = r"WS"

# Valid the sites with strict URL rules and then other possible sites with more relaxed rules
patterns["site"] = [
    r"^(www\.[\w-]+\.[\w-]+)\s+-\s*",
    r"^((?:www\.)?[\w-]+\.[\w-]+(?:\.[\w-]+)?)\s+-\s*",
    r"^(\[ ?([^\]]+?)\s?\])"
]

lang_list_pattern = (
    rf"\b(?:{link_patterns(langs)}(?:{delimiters}+(?:dub(?:bed)?|{link_patterns(patterns['audio'])}))?(?:{delimiters}+|\b))"
)
subs_list_pattern = rf"(?:{link_patterns(langs)}{delimiters}*)"

patterns["subtitles"] = [
    # Below must stay first, see patterns["languages"]
    rf"sub(?:title|bed)?s?{delimiters}*{subs_list_pattern}+",
    rf"(?:soft{delimiters}*)?{subs_list_pattern}+(?:(?:m(?:ulti(?:ple)?)?{delimiters}*)?sub(?:title|bed)?s?)",
    ("VOSTFR", ["French"]),
    # The following are patterns just for the 'subs' strings. Add normal sub stuff above.
    # Need a pattern just for subs, and can't just make above regexes * over + as we want
    # just 'subs' to match last.
    # The second-last one must stay second-last, see patterns["languages"]
    rf"(?:m(?:ulti(?:ple)?)?{delimiters}*)sub(?:title|bed)?s?",
    rf"(?:m(?:ulti(?:ple)?)?[\.\s\-\+_\/]*)?sub(?:title|bed)?s?{delimiters}*",
]
# Language takes precedence over subs when ambiguous - if we have a lang match, and
# then a subtitles match starting with subs, the first langs are languages, and the
# rest will be left as subtitles. Otherwise, don't match if there are subtitles matches
# after the langs.
patterns["languages"] = [
    rf"({lang_list_pattern}+)(?:{delimiters}*{patterns['subtitles'][0]})",
    rf"({lang_list_pattern}+)(?!{delimiters}*{link_patterns(patterns['subtitles'])})",
    rf"({lang_list_pattern}+)(?:{delimiters}*{patterns['subtitles'][-2]})",
]
patterns["sbs"] = [("Half-SBS", "Half SBS"), ("SBS", None, "upper")]
patterns["unrated"] = r"UNRATED"
patterns["size"] = (
    r"\d+(?:\.\d+)?\s?(?:GB|MB)",
    None,
    [("upper", []), ("replace", [" ", ""])],
)
patterns["bitDepth"] = r"(8|10)-?bits?"
patterns["3d"] = r"3D"
patterns["internal"] = r"iNTERNAL"
patterns["readnfo"] = r"READNFO"
patterns["hdr"] = r"HDR(?:10)?"
patterns["documentary"] = r"DOCU(?:menta?ry)?"
patterns["limited"] = r"LIMITED"
patterns["remastered"] = r"REMASTERED"
patterns["directorsCut"] = r"DC|Director'?s.?Cut"
patterns["upscaled"] = rf"(?:AI{delimiters}*)?upscaled?"
patterns["untouched"] = r"untouched"
patterns["remux"] = r"REMUX"
patterns["internationalCut"] = rf"International{delimiters}Cut"
# Spaces are only allowed before the genres list if after a word boundary or punctuation
patterns["genres"] = rf"\b\s*[\(\-\]]+\s*((?:{link_patterns(genres)}{delimiters}?)+)\b"

types = {
    "seasons": "integer",
    "episodes": "integer",
    "bitDepth": "integer",
    "year": "integer",
    "month": "integer",
    "day": "integer",
    "fps": "integer",
    "extended": "boolean",
    "hardcoded": "boolean",
    "proper": "boolean",
    "repack": "boolean",
    "widescreen": "boolean",
    "unrated": "boolean",
    "3d": "boolean",
    "internal": "boolean",
    "readnfo": "boolean",
    "documentary": "boolean",
    "hdr": "boolean",
    "limited": "boolean",
    "remastered": "boolean",
    "directorsCut": "boolean",
    "upscaled": "boolean",
    "untouched": "boolean",
    "remux": "boolean",
    "internationalCut": "boolean",
}

patterns["NON_ENGLISH_CHARS"] = (
    "\u3040-\u30ff"  # Japanese characters
    "\u3400-\u4dbf"  # Chinese characters
    "\u4e00-\u9fff"  # Chinese characters
    "\uf900-\ufaff"  # CJK Compatibility Ideographs
    "\uff66-\uff9f"  # Halfwidth Katakana Japanese characters
    "\u0400-\u04ff"  # Cyrillic characters (Russian)
    "\u0600-\u06ff"  # Arabic characters
)
patterns["RUSSIAN_CAST_REGEX"] = r"\([^)]*[\u0400-\u04ff][^)]*\)$|\/.*\((.*)\)$"
patterns["ALT_TITLES_REGEX"] = rf"[^/|(]*[{patterns['NON_ENGLISH_CHARS']}][^/|]*/|[/|][^/|(]*[{patterns['NON_ENGLISH_CHARS']}][^/|]*"
patterns["NOT_ONLY_NON_ENGLISH_REGEX"] = rf"(?:[a-zA-Z][^{patterns['NON_ENGLISH_CHARS']}]+|^)[{patterns['NON_ENGLISH_CHARS']}].*[{patterns['NON_ENGLISH_CHARS']}]|[{patterns['NON_ENGLISH_CHARS']}].*[{patterns['NON_ENGLISH_CHARS']}](?=[^{patterns['NON_ENGLISH_CHARS']}]+[a-zA-Z])"
patterns["NOT_ALLOWED_SYMBOLS_AT_START_AND_END"] = rf"^[^\w{patterns['NON_ENGLISH_CHARS']}#[【★]+|[ \-:/\\\[|{{(#$&^]+$"
patterns["REMAINING_NOT_ALLOWED_SYMBOLS_AT_START_AND_END"] = rf"^[^\w{patterns['NON_ENGLISH_CHARS']}#]+|]$"
patterns["RELEASE_GROUP_REGEX_START"] = r"^[\[【★].*[\]】★][ .]?(.+)"
patterns["RELEASE_GROUP_REGEX_END"] = r"(.+)[ .]?[\[【★].*[\]】★]$"
