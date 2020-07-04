#!/usr/bin/env python

# Post-processing functions that run after the main parsing.

from . import re

from .extras import link_patterns
from .patterns import episode_name_pattern, patterns, langs


# Before excess functions (before we split what was unmatched in the title into a list).
# They all take in the parse object and what was unmatched, and must return the latter minus
# what they used.


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


post_processing_before_excess = [
    try_episode_name,
]


# After excess functions take in just the parse object, and shouldn't return anything.


def try_group(self):
    if 'excess' not in self.parts:
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


def try_encoder(self):
    # split group name and encoder, adding the latter to self.parts
    if 'group' in self.parts:
        group = self.parts['group']
        pat = r'(\[(.*)\])'
        match = re.findall(pat, group, re.IGNORECASE)
        if match:
            match = match[0]
            raw = match[0]
            if match:
                if not re.match(r'[\[\],.+\-]*\Z', match[1], re.IGNORECASE):
                    self._part('encoder', None, match[1])
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
