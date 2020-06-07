#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from .patterns import patterns, types, delimiters, langs, patterns_ordered
from .extras import exceptions, patterns_ignore_title


class PTN(object):
    @staticmethod
    def _escape_regex(string):
        return re.sub(r'[\-\[\]{}()*+?.,\\^$|#\s]', '\\$&', string)

    def __init__(self):
        self.torrent = None
        self.excess_raw = None
        self.group_raw = None
        self.start = None
        self.end = None
        self.title_raw = None
        self.parts = None

        self.post_title_pattern = '{}|{}'.format(patterns['season'], patterns['year'])

    def _part(self, name, match, raw, clean, overwrite=False):
        if overwrite or name not in self.parts:
            if isinstance(clean, list) and len(clean) == 1:
                clean = clean[0]  # Avoids making a list if it only has 1 element
            self.parts[name] = clean

        if len(match) != 0:
            # The instructions for extracting title
            index = self.torrent['name'].find(match[0])
            if index == 0:
                self.start = len(match[0])
            elif self.end is None or index < self.end:
                self.end = index

        if name != 'excess':
            # The instructions for adding excess
            if name == 'group':
                self.group_raw = raw
            if raw is not None:
                self.excess_raw = self.excess_raw.replace(raw, '')


    @staticmethod
    def _clean_string(string):
        clean = re.sub(r'^ -', '', string)
        if clean.find(' ') == -1 and clean.find('.') != -1:
            clean = re.sub(r'\.', ' ', clean)
        clean = re.sub(r'_', ' ', clean)
        clean = re.sub(r'([\[(_]|- )$', '', clean).strip()
        clean = clean.strip(' _-')

        return clean

    def parse(self, name, standardise):
        name = name.strip()
        self.parts = {}
        self.torrent = {'name': name}
        self.excess_raw = name
        self.group_raw = ''
        self.start = 0
        self.end = None
        self.title_raw = None

        for key, pattern_options in [(key, patterns[key]) for key in patterns_ordered]:
            pattern_options_norm = list()
            if isinstance(pattern_options, str):
                pattern_options = [(pattern_options, None, None)]
            elif isinstance(pattern_options, tuple):
                pattern_options = [pattern_options]
            for options in pattern_options:
                if isinstance(options, str):
                    pattern_options_norm.append((options, None, None))
                elif len(options) == 2:  # No transformation
                    pattern_options_norm.append(options + (None,))
                else:
                    pattern_options_norm.append(options)

            pattern_options = pattern_options_norm

            for (pattern, replace, transform) in pattern_options:
                if key not in ('season', 'episode', 'episodeName', 'website'):
                    pattern = r'\b{}\b'.format(pattern)

                clean_name = self.get_clean_name(key)

                match = re.findall(pattern, clean_name, re.IGNORECASE)
                if len(match) == 0:
                    continue

                index = {}

                # With multiple matches, we will usually want to use the first match.
                # For 'year', we instead use the last instance of a year match since,
                # if a title includes a year, we don't want to use this for the year field.
                match_index = 0
                if key == 'year':
                    match_index = -1

                if isinstance(match[match_index], tuple):
                    match = list(match[match_index])
                if len(match) > 1:
                    index['raw'] = 0
                    index['clean'] = 0
                    # for season we might have it in index 1 or index 2
                    # e.g. "5x09"
                    for i in range(1, len(match)):
                        if match[i]:
                            index['clean'] = i
                            break
                else:
                    index['raw'] = 0
                    index['clean'] = 0

                # patterns for multiseason/episode make the range, and only the range, appear in match[0]
                if (key == 'season' or key == 'episode') and index['clean'] == 0:
                    # handle multi season/episode
                    # i.e. S01-S09
                    m = re.findall(r'[0-9]+', match[0])
                    if m and len(m) > 1:
                        clean = list(range(int(m[0]), int(m[1]) + 1))
                    elif m:
                        clean = int(m[0])
                elif key == 'language' or key == 'subtitles':
                    # handle multi language
                    m = re.split(r'{}+'.format(delimiters), match[index['clean']])
                    clean = list(filter(None, m))
                elif key in types.keys() and types[key] == 'boolean':
                    clean = True
                else:
                    clean = match[index['clean']]
                    if key in types.keys() and types[key] == 'integer':
                        clean = int(clean)

                if standardise:
                    if replace:
                        clean = replace
                    if transform:
                        clean = getattr(clean, transform)()  # For python2 compatibility

                    if key == 'subtitles' and len(clean) == 1 and clean[0].lower() == 'subs':
                        clean = 'Available'
                    elif key == 'language' or key == 'subtitles':
                        clean = self.standardise_languages(clean)

                self._part(key, match, match[index['raw']], clean)

        self.process_title()
        self.fix_known_exceptions()

        # Start process for end, where more general fields (episode name, group, and
        # encoder) get set.
        clean = re.sub(r'(^[-. ()]+)|([-. ]+$)', '', self.excess_raw)
        clean = re.sub(r'[()/]', ' ', clean)

        clean = self.try_episode_name(clean)

        clean = re.sub(r'(^[-_. ()]+)|([-. ]+$)', '', clean)
        clean = re.sub(r'[()/]', ' ', clean)
        match = re.split(r'\.\.+| +', clean)
        if len(match) > 0 and isinstance(match[0], tuple):
            match = list(match[0])

        clean = filter(bool, match)
        clean = [item for item in filter(lambda a: a != '-', clean)]
        clean = [item.strip('-') for item in clean]

        self.try_group(clean)
        self.try_encoder()

        if len(clean) != 0:
            self._part('excess', [], self.excess_raw, clean)
        return self.parts

    @staticmethod
    def standardise_languages(clean):
        cleaned_langs = list()
        for lang in clean:
            for (lang_regex, lang_clean) in langs:
                if re.match(lang_regex, lang, re.IGNORECASE):
                    cleaned_langs.append(lang_clean)
                    break
        clean = cleaned_langs
        return clean

    def process_title(self):
        raw = self.torrent['name']
        if self.end is not None:
            raw = raw[self.start:self.end].split('(')[0]
        clean = self._clean_string(raw)
        self._part('title', [], raw, clean)

    def get_clean_name(self, key):
        clean_name = re.sub(r'_', ' ', self.torrent['name'])
        # Only use part of the torrent name after the (guessed) title (split at a season or year)
        # to avoid matching certain patterns that could show up in a release title.
        for (ignore_key, ignore_patterns) in patterns_ignore_title:
            if ignore_key == key and not ignore_patterns:
                clean_name = re.split(self.post_title_pattern, clean_name, 1, re.IGNORECASE)[-1]
            elif ignore_key == key:
                for ignore_pattern in ignore_patterns:
                    if re.findall(ignore_pattern, clean_name, re.IGNORECASE):
                        clean_name = re.split(self.post_title_pattern, clean_name, 1, re.IGNORECASE)[-1]
        return clean_name

    def fix_known_exceptions(self):
        # Considerations for results that are known to cause issues, such
        # as media with years in them but without a release year.
        for exception in exceptions:
            incorrect_key, incorrect_value = exception['incorrect_parse']
            if self.parts['title'] == exception['parsed_title'] \
                and self.parts[incorrect_key] == incorrect_value:
                self.parts.pop(incorrect_key)
                self.parts['title'] = exception['actual_title']

    def try_episode_name(self, clean):
        match = re.findall(r'((?:(?:[A-Za-z][a-z]+|[A-Za-z])(?:[. \-+_]|$))+)', clean)
        if match:
            match = re.findall(patterns['episode'] + r'[._\-\s+]*(' + re.escape(match[0]) + ')',
                               self.torrent['name'], re.IGNORECASE)
            if match:
                self._part('episodeName', match, match[0], self._clean_string(match[0]))
                clean = clean.replace(match[0], '')
        return clean

    def try_group(self, clean):
        if len(clean) != 0:
            group = clean.pop() + self.group_raw
            self._part('group', [], group, group)
        # clean group name from having a container name
        if 'group' in self.parts and 'container' in self.parts:
            group = self.parts['group']
            container = self.parts['container']
            if group.lower().endswith('.' + container.lower()):
                group = group[:-(len(container) + 1)]
                self.parts['group'] = group

    def try_encoder(self):
        # split group name and encoder, adding the latter to self.parts
        if 'group' in self.parts:
            group = self.parts['group']
            pat = r'(\[(.*)\])'
            match = re.findall(pat, group, flags=re.IGNORECASE)
            if match:
                match = match[0]
                raw = match[0]
                if match:
                    self._part('encoder', match, raw, match[1])
                    self.parts['group'] = group.replace(raw, '')
                    if not self.parts['group'].strip():
                        self.parts.pop('group')
