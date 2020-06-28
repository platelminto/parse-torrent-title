#!/usr/bin/env python

import pkgutil
import re
import sys

from .patterns import patterns, types, delimiters, langs, patterns_ordered, episode_name_pattern
from .extras import exceptions, patterns_ignore_title, link_patterns

# Regex in python 2 is very slow so we check if the faster 'regex' library is available.
faster_regex = pkgutil.find_loader('regex')
if faster_regex is not None and sys.version_info[0] < 3:
    re = faster_regex.load_module('regex')


class PTN(object):
    def __init__(self):
        self.excess_raw = None
        self.torrent_name = None
        self.parts = None
        self.part_slices = None
        self.match_slices = None

        self.post_title_pattern = '(?:{}|{})'.format(link_patterns(patterns['season'])
                                                     , link_patterns(patterns['year']))

    # Ignored patterns will still remove their match from excess.
    def _part(self, name, match_slice, raw, clean, overwrite=False):
        if overwrite or name not in self.parts:
            if isinstance(clean, list) and len(clean) == 1:
                clean = clean[0]  # Avoids making a list if it only has 1 element
            self.parts[name] = clean
            self.part_slices[name] = match_slice

        if name != 'excess':
            # The instructions for adding excess
            if not match_slice and raw:
                self.excess_raw = self.excess_raw.replace(raw, '', 1)
            elif match_slice:
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
        self.parts = dict()
        self.part_slices = dict()
        self.torrent_name = name
        self.excess_raw = name
        self.match_slices = list()

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
                match_start, match_end = matches[match_index]['start'], matches[match_index]['end']
                if key in self.parts:  # We can skip ahead if we already have a matched part
                    self._part(key, (match_start, match_end),
                               match[0], None, overwrite=False)
                    continue

                index = self.get_match_indexes(match)

                # patterns for multiseason/episode make the range, and only the range, appear in match[0]
                if (key == 'season' or key == 'episode') and index['clean'] == 0:
                    clean = self.get_season_episode(match)
                elif key == 'language':
                    clean = self.get_language(match)
                elif key == 'subtitles':
                    clean = self.get_subtitles(match, match_start)
                elif key in types.keys() and types[key] == 'boolean':
                    clean = True
                else:
                    clean = match[index['clean']]
                    if key in types.keys() and types[key] == 'integer':
                        clean = int(clean)

                if standardise:
                    clean = self.standardise_clean(clean, key, replace, transforms)

                self._part(key, (match_start, match_end),
                           match[index['raw']], clean)

        self.merge_match_slices()

        self.process_title()
        self.fix_known_exceptions()

        self.fix_subtitles_no_language()

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

    @staticmethod
    def get_language(match):
        # handle multi subtitles
        m = re.split(r'{}+'.format(delimiters), match[0])
        clean = list(filter(None, m))

        return clean

    def get_subtitles(self, match, match_start):
        # handle multi subtitles
        m = re.split(r'{}+'.format(delimiters), match[0])
        m = list(filter(None, m))
        clean = list()
        for x in m:
            if len(m) == 1 and re.match('subs?', x, re.I):
                clean.append(x)
            elif not re.match('subs?|soft', x, re.I):
                clean.append(x)

        # If this match starts like the language one did, the only match for language
        # and subtitles is a list of langs directly followed by a subs-string. When this
        # is true, they would both match on it, but what it likely means is that all the
        # langs are language, and the subs string just indicates the existance of subtitles.
        # (e.g. Ita.Eng.MSubs would match Ita and Eng for language and subs - this makes
        # subs only become MSubs, and leaves language as Ita and Eng)
        if 'language' in self.part_slices and self.part_slices['language'][0] == match_start:
            clean = clean[-1]

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
    def standardise_languages(clean):
        cleaned_langs = list()
        for lang in clean:
            for (lang_regex, lang_clean) in langs:
                if re.match(lang_regex, re.sub(link_patterns(patterns['subtitles'][2:]), '', lang, flags=re.I), re.IGNORECASE):
                    cleaned_langs.append(lang_clean)
                    break
        clean = cleaned_langs
        return clean

    # Merge all the match slices (such as when they overlap), then remove
    # them from excess.
    def merge_match_slices(self):
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

        self.match_slices = slices

    def process_title(self):
        unmatched = list()
        prev_start = 0
        # Find all unmatched strings that aren't just punctuation
        for (start, end) in self.match_slices:
            if not re.match(delimiters + '*\Z', self.torrent_name[prev_start:start]):
                unmatched.append((prev_start, start))
            prev_start = end

        # Use the first one as the title
        if unmatched:
            title = unmatched[0]
            title_start, title_end = title[0], title[1]

            raw = self.torrent_name[title_start:title_end].split('(')[0]
            clean = self._clean_string(raw)
            self._part('title', (title_start, title_end), raw, clean)
            self.merge_match_slices()
        else:
            self._part('title', None, '', '')

    def fix_known_exceptions(self):
        # Considerations for results that are known to cause issues, such
        # as media with years in them but without a release year.
        for exception in exceptions:
            incorrect_key, incorrect_value = exception['incorrect_parse']
            if (self.parts['title'] == exception['parsed_title'] and
               incorrect_key in self.parts and self.parts[incorrect_key] == incorrect_value):
                self.parts.pop(incorrect_key)
                self._part('title', None, exception['actual_title'], exception['actual_title'], overwrite=True)

    def fix_subtitles_no_language(self):
        if 'language' not in self.parts and 'subtitles' in self.parts and \
            (len(self.parts['subtitles']) if isinstance(self.parts['subtitles'], list) else 0) > 1:
            self._part('language', None, None, self.parts['subtitles'][0])
            self._part('subtitles', None, None, self.parts['subtitles'][1:], overwrite=True)

    def process_excess(self):
        shift = 0
        for (start, end) in self.match_slices:
            self.excess_raw = self.excess_raw[:start-shift] + self.excess_raw[end-shift:]
            shift += end - start

    def try_episode_name(self, clean):
        match = re.findall(episode_name_pattern, clean)
        if match:
            match = re.search('(?:' + link_patterns(patterns['episode']) + '|' +
                              patterns['day'] + r')[._\-\s+]*(' + re.escape(match[0]) + ')',
                              self.torrent_name, re.IGNORECASE)
            if match:
                match_s, match_e = match.start(len(match.groups())-1), match.end(len(match.groups())-1)
                match = match.groups()[-1]
                self._part('episodeName', (match_s, match_e), match, self._clean_string(match))
                clean = clean.replace(match, '')
        return clean

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
                self._part('group', None, group, group, overwrite=True)

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
                    self._part('group', None, group.replace(raw, ''), group.replace(raw, ''), overwrite=True)
                    if not self.parts['group'].strip():
                        self.parts.pop('group')
