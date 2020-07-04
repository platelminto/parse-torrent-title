#!/usr/bin/env python

# Post-processing functions that run after the main parsing.

from . import re

from .extras import link_patterns
from .patterns import episode_name_pattern, patterns, langs, pre_group_encoder_pattern, delimiters


# Before excess functions (before we split what was unmatched in the title into a list).
# They all take in the parse object and what was unmatched, and must return the latter minus
# what they used.


# Try and find the episode name.
def try_episode_name(self, unmatched):
    match = re.findall(episode_name_pattern, unmatched)
    # First we see if there's a match in unmatched, then we look if it's after an episode
    # or a day in the full release title.
    if match:
        match = re.search('(?:' + link_patterns(patterns['episode']) + '|' +
                          patterns['day'] + r')[._\-\s+]*(' + re.escape(match[0]) + ')',
                          self.torrent_name, re.IGNORECASE)
        if match:
            match_s, match_e = match.start(len(match.groups())), match.end(len(match.groups()))
            match = match.groups()[-1]
            self._part('episodeName', (match_s, match_e), self._clean_string(match))
            unmatched = unmatched.replace(match, '')
    return unmatched


def try_encoder_before_group(self, unmatched):
    match = re.findall(pre_group_encoder_pattern, unmatched.strip())

    if match:
        match = re.search(r'[\s\-]' + re.escape(match[0]) + '$', self.torrent_name, re.IGNORECASE)
        if match:
            match_s, match_e = match.start(0), match.end(0)
            encoder_and_group = list(filter(None, re.split(r'[\-\s]', match.group(0))))
            if len(encoder_and_group) == 2:
                encoder_raw = encoder_and_group[0]
                group_raw = encoder_and_group[1]
                self._part('encoder', (match_s, match_e - len(group_raw)), self._clean_string(encoder_raw))
                self._part('group', (match_s + len(encoder_raw), match_e), self._clean_string(group_raw))
                unmatched = unmatched.replace(match.group(0), '')

    return unmatched


post_processing_before_excess = [
    try_episode_name,
    try_encoder_before_group,
]


# After excess functions take in just the parse object, and shouldn't return anything.


# Group is assumed to be the last element of `excess`, if not already added.
def try_group(self):
    if 'excess' not in self.parts or 'group' in self.parts:
        return
    excess = self.parts['excess']
    if not isinstance(excess, list):
        excess = [excess]

    if excess:
        group = excess.pop()
        self._part('group', None, group)

    if not excess:
        self.parts.pop('excess')
    else:
        self._part('excess', None, excess, overwrite=True)


# Split group name and encoder, adding the latter to self.parts
def try_encoder(self):
    if 'group' in self.parts:
        group = self.parts['group']
        pat = r'(\[(.*)\])'
        match = re.findall(pat, group, re.IGNORECASE)
        if match:
            match = match[0]
            raw = match[0]
            if match:
                if not re.match(r'[\[\],.+\-]*\Z', match[1], re.IGNORECASE):
                    # Might be written by pre_excess method, but we overwrite it.
                    self._part('encoder', None, match[1], overwrite=True)
                self._part('group', None, group.replace(raw, ''), overwrite=True)
                if not self.parts['group'].strip():
                    self.parts.pop('group')


# If this match starts like the language one did, the only match for language
# and subtitles is a list of langs directly followed by a subs-string. When this
# is true, they would both match on it, but what it likely means is that all the
# langs are language, and the subs string just indicates the existance of subtitles.
# (e.g. Ita.Eng.MSubs would match Ita and Eng for language and subs - this makes
# subs only become MSubs, and leaves language as Ita and Eng)
def fix_same_subtitles_language_match(self):
    if 'language' in self.part_slices and 'subtitles' in self.part_slices and \
        self.part_slices['language'][0] == self.part_slices['subtitles'][0]:
        subs = self.parts['subtitles'][-1]
        if self.standardise:
            subs = 'Available'
        self._part('subtitles', None, subs, overwrite=True)


# If there are no languages, but subtitles were matched, we should assume the first lang
# is the actual language, and remove it from the subtitles.
def fix_subtitles_no_language(self):
    if 'language' not in self.parts and 'subtitles' in self.parts and \
        isinstance(self.parts['subtitles'], list) and len(self.parts['subtitles']) > 1:
        self._part('language', None, self.parts['subtitles'][0])
        self._part('subtitles', None, self.parts['subtitles'][1:], overwrite=True)


# Language matches, to support multi-language releases that have the audio with each
# language, will contain audio info. We remove non-lang matching items from this list.
def fix_audio_in_language(self):
    if 'language' in self.parts and isinstance(self.parts['language'], list):
        languages = list(self.parts['language'])
        for lang in self.parts['language']:
            matched = False
            for (lang_regex, lang_clean) in langs:
                if re.match(lang_regex, lang, re.IGNORECASE):
                    matched = True
                    break
            if not matched:
                languages.remove(lang)

        self._part('language', self.part_slices['language'], languages, overwrite=True)


post_processing_after_excess = [
    try_group,
    try_encoder,
    fix_same_subtitles_language_match,
    fix_subtitles_no_language,
    fix_audio_in_language,
]
