#!/usr/bin/env python
import re
from typing import Dict, List, Tuple, Union, Optional, Any

from .extras import (
    delimiters,
    langs,
    genres,
    exceptions,
    patterns_ignore_title,
    link_patterns,
)
from .patterns import patterns, patterns_ordered, types, patterns_allow_overlap
from .post import post_processing_after_excess, post_processing_before_excess


class PTN:
    """
    Class to parse torrent names into meaningful components.
    """

    def __init__(self):
        self.compiled_patterns = self._compile_patterns()

    def _generate_post_title_pattern(self) -> str:
        """
        Generate the pattern to match post titles.
        """
        return f"(?:{link_patterns(patterns['seasons'])}|{link_patterns(patterns['year'])}|720p|1080p)"

    def _compile_patterns(self) -> Dict[str, List[Tuple[re.Pattern, Optional[str], Optional[Union[str, List[Tuple[str, List[Any]]]]]]]]:
        """
        Compile all regex patterns for better performance.
        """
        compiled_patterns = {}
        for key in patterns:
            pattern_options = self.normalise_pattern_options(patterns[key])
            compiled_patterns[key] = [(re.compile(opt[0], re.IGNORECASE), opt[1], opt[2]) for opt in pattern_options]
        return compiled_patterns

    def _part(self, name: str, match_slice: Optional[Tuple[int, int]], clean: Union[str, int, List[int], bool], overwrite: bool = False) -> None:
        """
        Add a part to the parts dictionary.
        """
        if overwrite or name not in self.parts:
            if self.coherent_types and name not in ["title", "episodeName"] and not isinstance(clean, bool):
                if not isinstance(clean, list):
                    clean = [clean]
            self.parts[name] = clean
            self.part_slices[name] = match_slice

        # Ignored patterns will still be considered 'matched' to remove them from excess.
        if match_slice:
            self.match_slices.append(match_slice)

    @staticmethod
    def _clean_dots(string: str) -> str:
        """
        Clean dots in a string.
        """
        if ' ' not in string and '.' in string:
            string = re.sub(r"\.{4,}", "... ", string)

            # Replace any instances of less than 3 dots with a space
            # Lookarounds are used to prevent the 3-dots (ellipses) from being replaced
            string = re.sub(r"(?<!\.)\.\.(?!\.)", " ", string)
            string = re.sub(r"(?<!\.)\.(?!\.\.)", " ", string)
        return string

    def _clean_string(self, string: str) -> str:
        """
        Clean a string.
        """
        clean = re.sub(r"^( -|\(|\[)", "", string)
        clean = self._clean_dots(clean)
        clean = re.sub(r"_", " ", clean)
        clean = re.sub(r"([\[)_\]]|- )$", "", clean).strip()
        clean = clean.strip(" _-")

        # Again, we need to clean up the dots & strip for non-english chars titles that get cleaned from above re.sub.
        clean = self._clean_dots(clean).strip()
        return clean

    def parse(self, name: str, standardise: bool = False, coherent_types: bool = False) -> Dict[str, Union[str, int, List[int], bool]]:
        """
        Parse a torrent name into its components.
        """
        self.torrent_name = name.strip()
        self.parts = {}
        self.part_slices = {}
        self.match_slices = []
        self.standardise = standardise
        self.coherent_types = coherent_types
        self.post_title_pattern = self._generate_post_title_pattern()

        for key in patterns_ordered:
            pattern_options = self.compiled_patterns[key]
            self._apply_patterns(key, pattern_options)

        self.process_title()
        self.fix_known_exceptions()

        unmatched = self.get_unmatched()
        for f in post_processing_before_excess:
            unmatched = f(self, unmatched)

        cleaned_unmatched = self.clean_unmatched()
        if cleaned_unmatched:
            self._part("excess", None, cleaned_unmatched)

        for f in post_processing_after_excess:
            f(self)

        return self.parts

    def _apply_patterns(self, key: str, pattern_options: List[Tuple[re.Pattern, Optional[str], Optional[Union[str, List[Tuple[str, List[Any]]]]]]]) -> None:
        """
        Apply patterns to the torrent name.
        """
        for pattern, replace, transforms in pattern_options:
            if key not in ("seasons", "episodes", "site", "languages", "genres"):
                pattern = re.compile(rf"\b(?:{pattern.pattern})\b", re.IGNORECASE)

            clean_name = self.torrent_name.replace("_", " ")
            matches = self.get_matches(pattern, clean_name, key)

            if not matches:
                continue

            # With multiple matches, we will usually want to use the first match.
            # For 'year', we instead use the last instance of a year match since,
            # if a title includes a year, we don't want to use this for the year field.
            match_index = -1 if key == "year" else 0
            match = matches[match_index]["match"]
            match_start, match_end = matches[match_index]["start"], matches[match_index]["end"]

            if key in self.parts:  # We can skip ahead if we already have a matched part
                self._part(key, (match_start, match_end), None, overwrite=False)
                continue

            index = self.get_match_indexes(match)
            clean = self._get_clean_value(key, match, index)

            if self.standardise:
                clean = self.standardise_clean(clean, key, replace, transforms)

            if not self._has_overlap(match_start, match_end):
                self._part(key, (match_start, match_end), clean)

    @staticmethod
    def normalise_pattern_options(pattern_options: Union[str, Tuple, List[Union[str, Tuple]]]) -> List[Tuple[str, Optional[str], Optional[Union[str, List[Tuple[str, List[Any]]]]]]]:
        """
        Normalise pattern options.
        """
        if isinstance(pattern_options, (str, tuple)):
            pattern_options = [pattern_options]
        normalized = []
        for option in pattern_options:
            if isinstance(option, str):
                normalized.append((option, None, None))
            elif len(option) == 2:
                normalized.append(option + (None,))
            else:
                transforms = option[2]
                if isinstance(transforms, tuple):
                    transforms = [transforms]
                elif not isinstance(transforms, list):
                    transforms = [(transforms, [])]
                normalized.append((option[0], option[1], transforms))
        return normalized

    def get_matches(self, pattern: re.Pattern, clean_name: str, key: str) -> List[Dict[str, Union[str, int]]]:
        """
        Get all matches for a pattern in the clean_name.
        """
        matches = pattern.finditer(clean_name)
        grouped_matches = [
            {"match": (m.groups() if m.groups() else [m.group()]), "start": m.start(), "end": m.end()}
            for m in matches if m.start() >= self.ignore_before_index(clean_name, key)
        ]
        return grouped_matches

    def ignore_before_index(self, clean_name: str, key: str) -> int:
        """
        Ignore matches before a certain index to avoid false positives.
        """
        if key not in patterns_ignore_title:
            return 0
        patterns_ignored = patterns_ignore_title[key]
        match = re.search(self.post_title_pattern, clean_name, re.IGNORECASE) if not patterns_ignored else None
        if not match:
            for ignore_pattern in patterns_ignored:
                if re.findall(ignore_pattern, clean_name, re.IGNORECASE):
                    match = re.search(self.post_title_pattern, clean_name, re.IGNORECASE)
                    if match:
                        break
        return match.start() if match else 0

    @staticmethod
    def get_match_indexes(match: List[str]) -> Dict[str, int]:
        """
        Get the indexes of raw and clean matches.
        """
        return {"raw": 0, "clean": next((i for i in range(1, len(match)) if match[i]), 0)}

    @staticmethod
    def get_season_episode(match: List[str]) -> Optional[List[int]]:
        """
        Get season or episode numbers from a match.
        """
        m = re.findall(r"[0-9]+", match[0])
        if m and len(m) > 1:
            return list(range(int(m[0]), int(m[-1]) + 1))
        if len(match) > 1 and match[1] and m:
            return list(range(int(m[0]), int(match[1]) + 1))
        if m:
            return [int(m[0])]
        return None

    @staticmethod
    def split_multi(match: List[str]) -> List[str]:
        """
        Split multiple values in a match.
        """
        return list(filter(None, re.split(rf"{delimiters}+", match[0])))

    @staticmethod
    def get_subtitles(match: List[str]) -> List[str]:
        """
        Get subtitles from a match.
        """
        m = list(filter(None, re.split(rf"{delimiters}+", match[0])))
        return m if len(m) == 1 else [x for x in m if not re.match("subs?|soft", x, re.I)]

    def standardise_clean(self, clean: Union[str, List[str]], key: str, replace: Optional[str], transforms: Optional[Union[str, List[Tuple[str, List[Any]]]]]) -> Union[str, List[str]]:
        """
        Standardise the clean value.
        """
        if replace:
            clean = replace
        if transforms:
            for transform in filter(lambda t: t[0], transforms):
                clean = getattr(clean, transform[0])(*transform[1])
        if key in ["languages", "subtitles"]:
            clean = self.standardise_languages(clean)
            if not clean:
                clean = "Available"
        if key == "genres":
            clean = self.standardise_genres(clean)
        return clean

    @staticmethod
    def standardise_languages(clean: List[str]) -> List[str]:
        """
        Standardise language names.
        """
        cleaned_langs = []
        for lang in clean:
            for lang_regex, lang_clean in langs:
                if re.match(lang_regex, re.sub(link_patterns(patterns["subtitles"][-2:]), "", lang, flags=re.I), re.IGNORECASE):
                    cleaned_langs.append(lang_clean)
                    break
        return cleaned_langs

    @staticmethod
    def standardise_genres(clean: List[str]) -> List[str]:
        """
        Standardise genre names.
        """
        standard_genres = []
        for genre in clean:
            for regex, clean_genre in genres:
                if re.match(regex, genre, re.IGNORECASE):
                    standard_genres.append(clean_genre)
                    break
        return standard_genres

    def merge_match_slices(self) -> None:
        """
        Merge overlapping match slices.
        """
        self.match_slices.sort(key=lambda match: match[0])
        merged = []
        i = 0
        while i < len(self.match_slices):
            start, end = self.match_slices[i]
            i += 1
            while i < len(self.match_slices) and self.match_slices[i][0] <= end:
                end = max(end, self.match_slices[i][1])
                i += 1
            merged.append((start, end))
        self.match_slices = merged

    def process_title(self) -> None:
        """
        Process the title from unmatched parts.
        """
        unmatched = self.unmatched_list(keep_punctuation=False)
        if unmatched:
            title_start, title_end = unmatched[0]
            if len(self.part_slices) > 3 and title_start > sorted(self.part_slices.values(), key=lambda s: s[0])[3][0]:
                self._part("title", None, "")

            raw = self.torrent_name[title_start:title_end]
            # Something in square brackets with 3 chars or fewer is too weird to be right.
            # If this seems too arbitrary, make it any square bracket, and Mother test
            # case will lose its translated title (which is mostly fine I think).
            m = re.search(r"\(|(?:\[(?:.{,3}\]|[^\]]*\d[^\]]*\]?))", raw, flags=re.I)
            if m:
                relative_title_end = m.start()
                raw = raw[:relative_title_end]
                title_end = relative_title_end + title_start
            # Similar logic as above, but looking at beginning of string unmatched brackets.
            m = re.search(r"^(?:\)|\[.*\])", raw)
            if m:
                relative_title_start = m.end()
                raw = raw[relative_title_start:]
                title_start = relative_title_start + title_start
            clean = self._clean_string(self.clean_title(raw))
            # Re-add title_start to unrelative the index from raw to self.torrent_name
            self._part("title", (title_start, title_end), clean)
        else:
            self._part("title", None, "")

    def unmatched_list(self, keep_punctuation: bool = True) -> List[Tuple[int, int]]:
        """
        Get list of unmatched parts of the torrent name.
        """
        self.merge_match_slices()
        unmatched = []
        prev_start = 0
        # A default so the last append won't crash if nothing has matched
        end = len(self.torrent_name)
        # Find all unmatched strings that aren't just punctuation
        for start, end in self.match_slices:
            if keep_punctuation or not re.match(rf"{delimiters}*\Z", self.torrent_name[prev_start:start]):
                unmatched.append((prev_start, start))
            prev_start = end

        # Add the last unmatched slice
        if keep_punctuation or not re.match(rf"{delimiters}*\Z", self.torrent_name[end:]):
            unmatched.append((end, len(self.torrent_name)))

        # If nothing matched, assume the whole thing is the title
        if not self.match_slices:
            unmatched.append((0, len(self.torrent_name)))
        return unmatched

    def fix_known_exceptions(self) -> None:
        """
        Fix known exceptions in the parsing.
        Considerations for results that are known to cause issues, such as media with years in them but without a release year.
        """
        for exception in exceptions:
            incorrect_key, incorrect_value = exception["incorrect_parse"]
            if self.parts.get("title") == exception["parsed_title"] and incorrect_key in self.parts:
                if self.parts[incorrect_key] == incorrect_value or (self.coherent_types and incorrect_value in self.parts[incorrect_key]):
                    self.parts.pop(incorrect_key)
                    self._part("title", None, exception["actual_title"], overwrite=True)

    def get_unmatched(self) -> str:
        """
        Get the unmatched parts of the torrent name.
        """
        return "".join([self.torrent_name[start:end] for start, end in self.unmatched_list()])

    def clean_unmatched(self) -> List[str]:
        """
        Clean the unmatched parts of the torrent name.
        """
        unmatched = [self.torrent_name[start:end] for start, end in self.unmatched_list()]
        unmatched_clean = []
        for raw in unmatched:
            clean = re.sub(r"(^[-_.\s(),]+)|([-.\s,]+$)", "", raw)
            clean = re.sub(r"[()/]", " ", clean)
            unmatched_clean.extend(re.split(r"\.\.+|\s+", clean))
        return [extra for extra in unmatched_clean if not re.match(rf"(?:Complete|Season|Full)?[\]\[,.+\- ]*(?:Complete|Season|Full)?\Z", extra, re.IGNORECASE)]

    @staticmethod
    def clean_title(raw_title: str) -> str:
        """
        Clean the title string.
        """
        cleaned_title = raw_title.replace(r"[[(]movie[)\]]", "")
        cleaned_title = re.sub(patterns["RUSSIAN_CAST_REGEX"], " ", cleaned_title)
        cleaned_title = re.sub(patterns["RELEASE_GROUP_REGEX_START"], r"\1", cleaned_title)
        cleaned_title = re.sub(patterns["RELEASE_GROUP_REGEX_END"], r"\1", cleaned_title)
        cleaned_title = re.sub(patterns["ALT_TITLES_REGEX"], "", cleaned_title)
        cleaned_title = re.sub(patterns["NOT_ONLY_NON_ENGLISH_REGEX"], "", cleaned_title)
        return cleaned_title

    @staticmethod
    def _is_overlap(part_slice: Tuple[int, int], match_slice: Tuple[int, int]) -> bool:
        """
        Check if two slices overlap.
        """
        return (part_slice[0] < match_slice[0] < part_slice[1]) or (part_slice[0] < match_slice[1] < part_slice[1])

    def _get_clean_value(self, key: str, match: List[str], index: Dict[str, int]) -> Union[str, int, List[int], bool]:
        """
        Get clean value based on key and match.
        """
        if key in ("seasons", "episodes"):
            return self.get_season_episode(match)
        if key == "subtitles":
            return self.get_subtitles(match)
        if key in ("languages", "genres"):
            return self.split_multi(match)
        if key in types and types[key] == "boolean":
            return True
        clean = match[index["clean"]]
        if key in types and types[key] == "integer":
            return int(clean)
        return clean

    def _has_overlap(self, match_start: int, match_end: int) -> bool:
        """
        Check if there is an overlap with existing parts.
        """
        return any(
            self._is_overlap(part_slice, (match_start, match_end))
            for part, part_slice in self.part_slices.items()
            if part not in patterns_allow_overlap
        )
