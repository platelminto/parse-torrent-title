#!/usr/bin/env python

import re
from .patterns import patterns, types, delimiters, langs, patterns_ordered, episode_name_pattern
from .extras import exceptions, patterns_ignore_title, link_pattern_options


class PTN(object):
    def __init__(self):
        self.excess_raw = None
        self.torrent_name = None
        self.title_start = None
        self.title_end = None
        self.parts = None
        self.match_slices = None

        self.post_title_pattern = '(?:{}|{})'.format(link_pattern_options(patterns['season'])
                                                     , link_pattern_options(patterns['year']))

    # Ignored patterns will still remove their match from excess.
    def _part(self, name, match_slice, raw, clean, overwrite=False):
        if overwrite or name not in self.parts:
            if isinstance(clean, list) and len(clean) == 1:
                clean = clean[0]  # Avoids making a list if it only has 1 element
            self.parts[name] = clean

        if match_slice:
            # The instructions for extracting title
            start, end = match_slice
            if start == 0:
                self.title_start = end
            elif self.title_end is None or start < self.title_end:
                self.title_end = start

        if name != 'excess':
            # The instructions for adding excess
            if not match_slice:
                self.excess_raw = self.excess_raw.replace(raw, '', 1)
            else:
                self.match_slices.append(match_slice)

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
        self.torrent_name = name
        self.excess_raw = name
        self.title_start = 0
        self.title_end = None
        self.match_slices = []

        for key, pattern_options in [(key, patterns[key]) for key in patterns_ordered]:
            pattern_options = self.normalise_pattern_options(pattern_options)

            for (pattern, replace, transforms) in pattern_options:
                if key not in ('season', 'episode', 'website', 'language'):
                    pattern = r'\b(?:{})\b'.format(pattern)

                clean_name = re.sub(r'_', ' ', self.torrent_name)
                matches = self.get_matches(pattern, clean_name, key)

                if not matches:
                    continue

                # With multiple matches, we will usually want to use the first match.
                # For 'year', we instead use the last instance of a year match since,
                # if a title includes a year, we don't want to use this for the year field.
                match_index = 0
                if key == 'year':
                    match_index = -1

                match = matches[match_index]['match']

                index = self.get_match_indexes(match)

                # patterns for multiseason/episode make the range, and only the range, appear in match[0]
                if (key == 'season' or key == 'episode') and index['clean'] == 0:
                    clean = self.get_season_episode(match)
                elif key == 'language' or key == 'subtitles':
                    clean = self.get_language_subtitles(match)
                elif key in types.keys() and types[key] == 'boolean':
                    clean = True
                else:
                    clean = match[index['clean']]
                    if key in types.keys() and types[key] == 'integer':
                        clean = int(clean)

                if standardise:
                    clean = self.standardise_clean(clean, key, replace, transforms)

                self._part(key, (matches[match_index]['start'], matches[match_index]['end']),
                           match[index['raw']], clean)

        self.process_title()
        self.fix_known_exceptions()

        self.process_excess()

        # Start process for end, where more general fields (episode name, group, and
        # encoder) get set.
        clean = re.sub(r'(^[-. ()]+)|([-. ]+$)', '', self.excess_raw)
        clean = re.sub(r'[()/]', ' ', clean)

        clean = self.try_episode_name(clean)

        clean = self.clean_excess(clean)

        self.try_group(clean)
        self.try_encoder()

        if clean:
            self._part('excess', None, self.excess_raw, clean)

        return self.parts

    @staticmethod
    def get_language_subtitles(match):
        # handle multi language
        m = re.split(r'{}+'.format(delimiters), match[0])
        m = list(filter(None, m))
        clean = list()
        for x in m:
            if len(m) == 1 and re.match('subs?', x, re.I):
                clean.append(x)
            elif not re.match('subs?|soft', x, re.I):
                clean.append(x)
        return clean

    @staticmethod
    def get_season_episode(match):
        # handle multi season/episode
        # e.g. S01-S09
        clean = None
        m = re.findall(r'[0-9]+', match[0])
        if m and len(m) > 1:
            clean = list(range(int(m[0]), int(m[-1]) + 1))
        elif m:
            clean = int(m[0])
        return clean

    def standardise_clean(self, clean, key, replace, transforms):
        if replace:
            clean = replace
        if transforms:
            for transform in filter(lambda t: t[0], transforms):
                # For python2 compatibility, we're not able to simply pass functions as str.upper
                # means different things in 2.7 and 3.5.
                clean = getattr(clean, transform[0])(*transform[1])
        if key == 'language' or key == 'subtitles':
            clean = self.standardise_languages(clean)
            if not clean:
                clean = 'Available'
        return clean

    @staticmethod
    def get_match_indexes(match):
        index = {'raw': 0, 'clean': 0}

        if len(match) > 1:
            # for season we might have it in index 1 or index 2
            # e.g. "5x09"
            for i in range(1, len(match)):
                if match[i]:
                    index['clean'] = i
                    break

        return index

    def get_matches(self, pattern, clean_name, key):
        grouped_matches = list()
        matches = list(re.finditer(pattern, clean_name, re.IGNORECASE))
        for m in matches:
            if m.start() < self.ignore_before_index(clean_name, key):
                continue
            groups = m.groups()
            if not groups:
                grouped_matches.append((m.group(), m.start(), m.end()))
            else:
                grouped_matches.append((groups, m.start(), m.end()))

        parsed_matches = list()
        for match in grouped_matches:
            m = match[0]
            if isinstance(m, tuple):
                m = list(m)
            else:
                m = [m]
            parsed_matches.append({'match': m,
                                    'start': match[1],
                                    'end': match[2]})
        return parsed_matches

    # Handles all the optional/missing tuple elements into a consistent list.
    @staticmethod
    def normalise_pattern_options(pattern_options):
        pattern_options_norm = list()

        if isinstance(pattern_options, tuple):
            pattern_options = [pattern_options]
        elif not isinstance(pattern_options, list):
            pattern_options = [(pattern_options, None, None)]
        for options in pattern_options:
            if len(options) == 2:  # No transformation
                pattern_options_norm.append(options + (None,))
            elif isinstance(options, tuple):
                if isinstance(options[2], tuple):
                    pattern_options_norm.append(tuple(list(options[:2]) + [[options[2]]]))
                elif isinstance(options[2], list):
                    pattern_options_norm.append(options)
                else:
                    pattern_options_norm.append(tuple(list(options[:2]) + [[(options[2], [])]]))

            else:
                pattern_options_norm.append((options, None, None))
        pattern_options = pattern_options_norm
        return pattern_options

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
        raw = self.torrent_name
        if self.title_end is not None:
            raw = raw[self.title_start:self.title_end].split('(')[0]
        clean = self._clean_string(raw)
        self._part('title', (self.title_start, self.title_end), raw, clean)

    # Merge all the match slices (such as when they overlap), then remove
    # them from excess.
    def process_excess(self):
        matches = sorted(self.match_slices, key=lambda match: match[0])

        i = 0
        slices = list()
        while i < len(matches):
            start, end = matches[i]
            i += 1
            for (next_start, next_end) in matches[i:]:
                if next_start <= end:
                    end = max(end, next_end)
                    i += 1
                else:
                    break
            slices.append((start, end))

        shift = 0
        for (start, end) in slices:
            self.excess_raw = self.excess_raw[:start-shift] + self.excess_raw[end-shift:]
            shift += end - start

    # Only use part of the torrent name after the (guessed) title (split at a season or year)
    # to avoid matching certain patterns that could show up in a release title.
    def ignore_before_index(self, clean_name, key):
        match = None
        for (ignore_key, ignore_patterns) in patterns_ignore_title:
            if ignore_key == key and not ignore_patterns:
                match = re.search(self.post_title_pattern, clean_name, re.IGNORECASE)
            elif ignore_key == key:
                for ignore_pattern in ignore_patterns:
                    if re.findall(ignore_pattern, clean_name, re.IGNORECASE):
                        match = re.search(self.post_title_pattern, clean_name, re.IGNORECASE)

        if match:
            return match.start()
        return 0

    def fix_known_exceptions(self):
        # Considerations for results that are known to cause issues, such
        # as media with years in them but without a release year.
        for exception in exceptions:
            incorrect_key, incorrect_value = exception['incorrect_parse']
            if (self.parts['title'] == exception['parsed_title'] and
               incorrect_key in self.parts and self.parts[incorrect_key] == incorrect_value):
                self.parts.pop(incorrect_key)
                self.parts['title'] = exception['actual_title']

    @staticmethod
    def clean_excess(clean):
        clean = re.sub(r'(^[-_. (),]+)|([-. ,]+$)', '', clean)
        clean = re.sub(r'[()/]', ' ', clean)
        match = re.split(r'\.\.+| +', clean)
        if match and isinstance(match[0], tuple):
            match = list(match[0])
        clean = filter(bool, match)
        clean = [item.strip('-') for item in clean]
        filtered = list()
        for extra in clean:
            # re.fullmatch() is not available in python 2.7, so we manually do it with \Z.
            if not re.match(r'(?:Complete|Season|Full)?[\]\[,.+\-]*(?:Complete|Season|Full)?\Z', extra, re.IGNORECASE):
                filtered.append(extra)
        return filtered

    def try_episode_name(self, clean):
        match = re.findall(episode_name_pattern, clean)
        if match:
            match = re.findall(patterns['episode'] + r'[._\-\s+]*(' + re.escape(match[0]) + ')',
                               self.torrent_name, re.IGNORECASE)
            if match:
                self._part('episodeName', None, match[0], self._clean_string(match[0]))
                clean = clean.replace(match[0], '')
        return clean

    def try_group(self, clean):
        if len(clean) != 0:
            group = clean.pop()
            self._part('group', None, group, group)
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
            match = re.findall(pat, group, re.IGNORECASE)
            if match:
                match = match[0]
                raw = match[0]
                if match:
                    if not re.match(r'[\[\],.+\-]*\Z', match[1], re.IGNORECASE):
                        self._part('encoder', None, raw, match[1])
                    self.parts['group'] = group.replace(raw, '')
                    if not self.parts['group'].strip():
                        self.parts.pop('group')
