#!/usr/bin/env python

import re
from typing import Any

from .extras import link_patterns, complete_series, langs
from .patterns import episode_name_pattern, patterns, pre_website_encoder_pattern

# Compile regex patterns once for reuse
episode_name_compiled = re.compile(episode_name_pattern)
pre_website_encoder_compiled = re.compile(pre_website_encoder_pattern.strip(), re.IGNORECASE)
complete_series_compiled = re.compile(link_patterns(complete_series), re.IGNORECASE)
filetype_pattern_compiled = re.compile(link_patterns(patterns['filetype']), re.IGNORECASE)


# Post-processing functions that run after the main parsing.

# Before excess functions (before we split what was unmatched in the title into a list).
# They all take in the parse object and what was unmatched, and must return the latter minus
# what they used.

# Try and find the episode name.
def try_episode_name(self: Any, unmatched: str) -> str:
    match = episode_name_compiled.findall(unmatched)
    if match:
        pattern = rf"(?:{link_patterns(patterns['episodes'])}|{patterns['day']}|{patterns['year']})[._\-\s+]*({re.escape(match[0])})"
        match = re.search(pattern, self.torrent_name, re.IGNORECASE)
        if match:
            match_s, match_e = match.start(len(match.groups())), match.end(len(match.groups()))
            self._part("episodeName", (match_s, match_e), self._clean_string(match.group(len(match.groups()))))
            unmatched = unmatched.replace(match.group(len(match.groups())), "")
    return unmatched


def try_encoder_before_site(self: Any, unmatched: str) -> str:
    match = pre_website_encoder_compiled.findall(unmatched.strip())
    if match:
        for m in match:
            pattern = rf"[\s\-]({re.escape(m)})(?:\.{filetype_pattern_compiled.pattern})?$"
            full_title_match = re.search(pattern, self.torrent_name, re.I)
            if full_title_match:
                match_s, match_e = full_title_match.start(0), full_title_match.end(0)
                encoder_and_site = list(filter(None, re.split(r"[\-\s\)]", full_title_match.group(1))))
                if len(encoder_and_site) == 2:
                    encoder_raw, site_raw = encoder_and_site
                    self._part("encoder", (match_s, match_e - len(site_raw)), self._clean_string(encoder_raw))
                    self._part("site", (match_s + len(encoder_raw), match_e), self._clean_string(site_raw), overwrite=False)
                    unmatched = unmatched.replace(full_title_match.group(0), "")
                break
    return unmatched


def remove_complete_series_string(self: Any, unmatched: str) -> str:
    if "title" in self.parts:
        complete_match = complete_series_compiled.search(self.parts["title"])
        if complete_match:
            title = self.parts["title"]
            title = title[:complete_match.start()] + title[complete_match.end():]
            self._part("title", (complete_match.start(), complete_match.end()), self._clean_string(title), overwrite=True)
    return unmatched


post_processing_before_excess = [
    remove_complete_series_string,
    try_episode_name,
    try_encoder_before_site,
]


# After excess functions take in just the parse object, and shouldn't return anything.

# encoder is assumed to be the last element of `excess`, if not already added.
def try_encoder(self: Any) -> None:
    if "excess" not in self.parts or "encoder" in self.parts:
        return
    excess = self.parts["excess"]
    if not isinstance(excess, list):
        excess = [excess]
    if excess:
        encoder = excess.pop()
        self._part("encoder", None, encoder, overwrite=True)
    if not excess:
        self.parts.pop("excess")
    else:
        self._part("excess", None, excess, overwrite=True)


# Split encoder name and site, adding the latter to self.parts
def try_site(self: Any) -> None:
    if "encoder" not in self.parts or "site" in self.parts:
        return
    encoder = self.parts["encoder"]
    if self.coherent_types:
        encoder = encoder[0]
    match = re.findall(r"(\[(.*)\])", encoder, re.IGNORECASE)
    if match:
        raw, site = match[0]
        if not re.match(r"[\[\],.+\-]*\Z", site, re.IGNORECASE):
            self._part("site", None, site)
        self._part("encoder", None, encoder.replace(raw, ""), overwrite=True)


# If there are no languages, but subtitles were matched, we should assume the first lang
# is the actual languages, and remove it from the subtitles.
def fix_subtitles_no_language(self: Any) -> None:
    if (
        "languages" not in self.parts
        and "subtitles" in self.parts
        and isinstance(self.parts["subtitles"], list)
        and len(self.parts["subtitles"]) > 1
    ):
        self._part("languages", None, self.parts["subtitles"][:1])
        self._part("subtitles", None, self.parts["subtitles"][1:], overwrite=True)


# Language matches, to support multi-languages releases that have the audio with each
# languages, will contain audio info (or simply extra strings like 'dub').
# We remove non-lang matching items from this list.
def filter_non_languages(self: Any) -> None:
    if "languages" in self.parts and isinstance(self.parts["languages"], list):
        languages = [
            lang for lang in self.parts["languages"]
            if any(re.match(lang_regex, lang, re.IGNORECASE) for lang_regex, _ in langs)
        ]
        self._part("languages", self.part_slices["languages"], languages, overwrite=True)


def is_subtitle_available(self: Any) -> None:
    if "subtitles" not in self.parts:
        return
    subtitles = self.parts.get("subtitles")
    self.parts["is_subtitle_available"] = bool(subtitles)
    if subtitles == "Available":
        self._part("subtitles", self.part_slices["subtitles"], self.parts.get("languages", []), overwrite=True)
    elif subtitles == "Available":
        self.parts.pop("subtitles")


def try_vague_season_episode(self: Any) -> None:
    title = self.parts["title"]
    m = re.search(r"(\d{1,2})-(\d{1,2})$", title)
    if m and "seasons" not in self.parts and "episodes" not in self.parts:
        offset = self.part_slices["title"][0]
        self._part("seasons", (offset + m.start(1), offset + m.end(1)), [int(m.group(1))])
        self._part("episodes", (offset + m.start(2), offset + m.end(2)), [int(m.group(2))])
        new_title = title[:m.start()]
        self._part("title", (offset, offset + len(new_title)), self._clean_string(new_title), overwrite=True)


# Probably for movies like 1917, where the title is just the year (would need the release year to also be absent)
def use_year_as_title_if_absent(self: Any) -> None:
    if "year" in self.parts and not self.parts.get("title"):
        self._part("title", None, str(self.parts["year"]), overwrite=True)
        self.parts.pop("year")


def remove_empty_parts(self: Any) -> None:
    self.parts = {part: value for part, value in self.parts.items() if value != ""}


post_processing_after_excess = [
    try_encoder,
    try_site,
    fix_subtitles_no_language,
    filter_non_languages,
    is_subtitle_available,
    try_vague_season_episode,
    use_year_as_title_if_absent,
    remove_empty_parts,
]
