#!/usr/bin/env python
import re
from .extras import exceptions, genres, langs, link_patterns, patterns_ignore_title
from .patterns import delimiters, patterns, patterns_ordered, types, patterns_allow_overlap, patterns_allow_multiple
from .post import post_processing_after_excess, post_processing_before_excess


class PTN:
    def __init__(self):
        self.post_title_pattern = "(?:{}|{}|720p|1080p)".format(
            link_patterns(patterns["season"]), link_patterns(patterns["year"])
        )

    def _part(self, name, match_slice, clean, overwrite=False):
        if overwrite or name not in self.parts:
            if self.coherent_types:
                if name not in ["title", "episodeName"] and not isinstance(clean, bool):
                    if not isinstance(clean, list):
                        clean = [clean]
            else:
                if isinstance(clean, list) and len(clean) == 1:
                    clean = clean[0]  # Avoids making a list if it only has 1 element

            self.parts[name] = clean
            self.part_slices[name] = match_slice

        # Ignored patterns will still be considered 'matched' to remove them from excess.
        if match_slice:
            self.match_slices.append(match_slice)

    @staticmethod
    def _clean_string(string):
        clean = re.sub(r"^( -|\(|\[)", "", string)
        if clean.find(" ") == -1 and clean.find(".") != -1:
            # 4 dots likely means we want an ellipsis and a space
            clean = re.sub(r"\.{4,}", "... ", clean)

            # Replace any instances of less than 3 dots with a space
            # Lookarounds are used to prevent the 3-dots (ellipses) from being replaced
            clean = re.sub(r"(?<!\.)\.\.(?!\.)", " ", clean)
            clean = re.sub(r"(?<!\.)\.(?!\.\.)", " ", clean)

        clean = re.sub(r"_", " ", clean)
        clean = re.sub(r"([\[)_\]]|- )$", "", clean).strip()
        clean = clean.strip(" _-")

        return clean

    def _values_are_different(self, value1, value2, field_key=None):
        """
        Check if two values are significantly different.
        
        This prevents adding duplicate values when different regex patterns
        match the same or semantically equivalent content.
        
        Args:
            value1: First value to compare
            value2: Second value to compare
            field_key: The field key (optional, used for field-specific logic)
            
        Returns:
            True if values are different enough to be treated as separate matches
        """
        # Normalize for comparison
        v1_str = str(value1)
        v2_str = str(value2)
        
        v1 = v1_str.lower().replace("-", "").replace(".", "").replace(" ", "")
        v2 = v2_str.lower().replace("-", "").replace(".", "").replace(" ", "")
        
        # If they're identical after normalization, they're not different
        if v1 == v2:
            return False
        
        # Field-specific logic
        if field_key == "codec":
            # x265 and HEVC are the same codec
            # x264 and AVC are the same codec
            codec_equivalents = [
                {"x265", "hevc", "h265", "h.265"},
                {"x264", "avc", "h264", "h.264"},
                {"xvid"},
                {"av1"},
                {"vc1", "vc-1"},
            ]
            for equiv_set in codec_equivalents:
                if v1 in equiv_set and v2 in equiv_set:
                    return False
        
        if field_key == "resolution":
            # QHD (1440p) and qHD (540p) can both match "QHD" in text
            # If we have 1440p, don't add 540p (QHD takes precedence over qHD)
            if (v1 == "1440p" or v1 == "qhd") and (v2 == "540p" or v2 == "qhd"):
                return False
            if (v2 == "1440p" or v2 == "qhd") and (v1 == "540p" or v1 == "qhd"):
                return False
                    
        if field_key == "quality":
            # PPV (Pay-Per-View) is often used to describe content type rather than source quality
            # If one is PPV and the other is a proper source quality, don't consider them different
            quality_sources = ["webdl", "webrip", "bluray", "brrip", "bdrip", "dvdrip", "hdtv", 
                             "web", "cam", "ts", "tc", "screener", "dvdr", "hddvd", "remux"]
            v1_is_ppv = "ppv" in v1
            v2_is_ppv = "ppv" in v2
            v1_is_source = any(src in v1 for src in quality_sources)
            v2_is_source = any(src in v2 for src in quality_sources)
            
            if v1_is_ppv and v2_is_source:
                return False  # Don't add PPV if we have a proper source
            if v2_is_ppv and v1_is_source:
                return False  # Don't add PPV if we have a proper source
        
        # Special handling for standalone channel numbers (e.g., "5.1", "7.1")
        # These should not be added if a full audio format with that channel exists
        standalone_channels = ["5.1", "7.1", "2.0", "1.0", "2.1", "6.1"]
        v1_is_channel = v1_str.strip() in standalone_channels
        v2_is_channel = v2_str.strip() in standalone_channels
        
        if v1_is_channel or v2_is_channel:
            # If one is a standalone channel, check if it's contained in the other
            if v1_is_channel and v1_str.strip() in v2_str:
                return False  # v1 is redundant
            if v2_is_channel and v2_str.strip() in v1_str:
                return False  # v2 is redundant
        
        # Check for substring containment - if one is contained in the other,
        # they're likely the same thing (e.g., "DTS" and "DTS-HD MA")
        if v1 in v2 or v2 in v1:
            # Exception: different channel configurations should be considered different
            # e.g., "DTS 5.1" vs "DTS 7.1"
            has_channel_v1 = any(ch in v1_str for ch in ["5.1", "7.1", "2.0", "1.0"])
            has_channel_v2 = any(ch in v2_str for ch in ["5.1", "7.1", "2.0", "1.0"])
            if has_channel_v1 and has_channel_v2:
                # Both have channel info - extract and compare channels
                channel_v1 = None
                channel_v2 = None
                for ch in ["5.1", "7.1", "2.0", "1.0", "2.1", "6.1"]:
                    if ch in v1_str:
                        channel_v1 = ch
                    if ch in v2_str:
                        channel_v2 = ch
                # They're different if channels differ
                return channel_v1 != channel_v2
            # Otherwise, substring containment means they're similar enough
            return False
        
        return True

    def parse(self, name, standardise, coherent_types):
        name = name.strip()
        self.parts: dict = {}
        self.part_slices: dict = {}
        self.torrent_name: str = name
        self.match_slices: list = []
        self.standardise: bool = standardise
        self.coherent_types: bool = coherent_types

        for key, pattern_options in [(key, patterns[key]) for key in patterns_ordered]:
            pattern_options = self.normalise_pattern_options(pattern_options)

            for (pattern, replace, transforms) in pattern_options:
                if key not in ("season", "episode", "site", "language", "genre"):
                    pattern = r"\b(?:{})\b".format(pattern)

                clean_name = re.sub(r"_", " ", self.torrent_name)
                matches = self.get_matches(pattern, clean_name, key)

                if not matches:
                    continue

                # With multiple matches, we will usually want to use the first match.
                # For 'year', we instead use the last instance of a year match since,
                # if a title includes a year, we don't want to use this for the year field.
                match_index = 0
                if key == "year":
                    match_index = -1

                match = matches[match_index]["match"]
                match_start, match_end = (
                    matches[match_index]["start"],
                    matches[match_index]["end"],
                )
                
                # Check if this match is part of a larger hyphenated term
                # (e.g., "HD" in "DTS-HD")
                # We want to skip matches that are in the middle of compound terms
                is_within_hyphenated_term = False
                has_hyphen_before = False
                has_hyphen_after = False
                
                if match_start > 0 and self.torrent_name[match_start - 1] == '-':
                    # Check if there's a non-delimiter character before the hyphen
                    if match_start > 1 and not re.match(delimiters, self.torrent_name[match_start - 2]):
                        has_hyphen_before = True
                        
                if match_end < len(self.torrent_name) and self.torrent_name[match_end] == '-':
                    # Check if there's a non-delimiter character after the hyphen
                    if match_end + 1 < len(self.torrent_name) and not re.match(delimiters, self.torrent_name[match_end + 1]):
                        has_hyphen_after = True
                
                # Only skip if BOTH sides have hyphens (e.g., "something-HD-something")
                # OR if it's before a hyphen and the match is very short/ambiguous (like "HD")
                if key in ["resolution"]:
                    match_text = self.torrent_name[match_start:match_end]
                    # Skip if it's a short ambiguous term like "HD" that's part of a compound
                    if has_hyphen_before or (has_hyphen_after and len(match_text) <= 3):
                        is_within_hyphenated_term = True
                
                # Skip this match if it's within a hyphenated term
                if is_within_hyphenated_term:
                    # Still mark as matched to track the slice, but don't add to parts
                    self._part(key, (match_start, match_end), None, overwrite=False)
                    continue
                
                # Handle fields that can have multiple values
                if key in self.parts and key in patterns_allow_multiple:
                    # Extract and process the new value first
                    index = self.get_match_indexes(match)
                    
                    if key in ("season", "episode"):
                        clean = self.get_season_episode(match)
                    elif key == "subtitles":
                        clean = self.get_subtitles(match)
                    elif key in ("language", "genre"):
                        clean = self.split_multi(match)
                    elif key in types.keys() and types[key] == "boolean":
                        clean = True
                    else:
                        clean = match[index["clean"]]
                        if key in types.keys() and types[key] == "integer":
                            clean = int(clean)
                    
                    if self.standardise:
                        clean = self.standardise_clean(clean, key, replace, transforms)
                    
                    # Check if this is a significantly different value
                    existing = self.parts[key]
                    if not isinstance(existing, list):
                        existing = [existing]
                    
                    # Check if the new value is different from all existing values
                    is_different = True
                    for existing_value in existing:
                        if not self._values_are_different(clean, existing_value, key):
                            is_different = False
                            break
                    
                    if is_different:
                        # Check for overlaps before adding
                        part_overlaps = False
                        for part, part_slices in self.part_slices.items():
                            if part not in patterns_allow_overlap:
                                if (
                                    (part_slices[0] < match_start < part_slices[1])
                                    or (part_slices[0] < match_end < part_slices[1])
                                ):
                                    part_overlaps = True
                                    break
                        
                        if not part_overlaps:
                            # Add the new value to the list
                            updated_list = existing + [clean]
                            self._part(key, (match_start, match_end), updated_list, overwrite=True)
                    else:
                        # Still mark as matched to remove from excess
                        self._part(key, (match_start, match_end), None, overwrite=False)
                    continue
                elif key in self.parts:
                    # We can skip ahead if we already have a matched part (and it doesn't allow multiple)
                    self._part(key, (match_start, match_end), None, overwrite=False)
                    continue

                index = self.get_match_indexes(match)

                if key in ("season", "episode"):
                    clean = self.get_season_episode(match)
                elif key == "subtitles":
                    clean = self.get_subtitles(match)
                elif key in ("language", "genre"):
                    clean = self.split_multi(match)
                elif key in types.keys() and types[key] == "boolean":
                    clean = True
                else:
                    clean = match[index["clean"]]
                    if key in types.keys() and types[key] == "integer":
                        clean = int(clean)

                if self.standardise:
                    clean = self.standardise_clean(clean, key, replace, transforms)

                part_overlaps = False
                for part, part_slices in self.part_slices.items():
                    if part not in patterns_allow_overlap:
                        # Strict smaller/larger than since punctuation can overlap.
                        if (
                            (part_slices[0] < match_start < part_slices[1])
                            or (part_slices[0] < match_end < part_slices[1])
                        ):
                            part_overlaps = True
                            break

                if not part_overlaps:
                    self._part(key, (match_start, match_end), clean)

        self.process_title()
        self.fix_known_exceptions()

        unmatched = self.get_unmatched()
        for f in post_processing_before_excess:
            unmatched = f(self, unmatched)

        # clean_unmatched() depends on the before_excess methods adding more match slices.
        cleaned_unmatched = self.clean_unmatched()
        if cleaned_unmatched:
            self._part("excess", None, cleaned_unmatched)

        for f in post_processing_after_excess:
            f(self)

        return self.parts

    # Handles all the optional/missing tuple elements into a consistent list.
    @staticmethod
    def normalise_pattern_options(pattern_options):
        pattern_options_norm = []

        if isinstance(pattern_options, tuple):
            pattern_options = [pattern_options]
        elif not isinstance(pattern_options, list):
            pattern_options = [(pattern_options, None, None)]
        for options in pattern_options:
            if len(options) == 2:  # No transformation
                pattern_options_norm.append(options + (None,))
            elif isinstance(options, tuple):
                if isinstance(options[2], tuple):
                    pattern_options_norm.append(
                        tuple(list(options[:2]) + [[options[2]]])
                    )
                elif isinstance(options[2], list):
                    pattern_options_norm.append(options)
                else:
                    pattern_options_norm.append(
                        tuple(list(options[:2]) + [[(options[2], [])]])
                    )

            else:
                pattern_options_norm.append((options, None, None))
        pattern_options = pattern_options_norm
        return pattern_options

    def get_matches(self, pattern, clean_name, key):
        grouped_matches = []
        matches = list(re.finditer(pattern, clean_name, re.IGNORECASE))
        for m in matches:
            if m.start() < self.ignore_before_index(clean_name, key):
                continue
            groups = m.groups()
            if not groups:
                grouped_matches.append((m.group(), m.start(), m.end()))
            else:
                grouped_matches.append((groups, m.start(), m.end()))

        parsed_matches = []
        for match in grouped_matches:
            m = match[0]
            if isinstance(m, tuple):
                m = list(m)
            else:
                m = [m]
            parsed_matches.append({"match": m, "start": match[1], "end": match[2]})
        return parsed_matches

    # Only use part of the torrent name after the (guessed) title (split at a season or year)
    # to avoid matching certain patterns that could show up in a release title.
    def ignore_before_index(self, clean_name, key):
        match = None
        if key in patterns_ignore_title:
            patterns_ignored = patterns_ignore_title[key]
            if not patterns_ignored:
                match = re.search(self.post_title_pattern, clean_name, re.IGNORECASE)
            else:
                for ignore_pattern in patterns_ignored:
                    if re.findall(ignore_pattern, clean_name, re.IGNORECASE):
                        match = re.search(
                            self.post_title_pattern, clean_name, re.IGNORECASE
                        )

        if match:
            return match.start()
        return 0

    @staticmethod
    def get_match_indexes(match):
        index = {"raw": 0, "clean": 0}

        if len(match) > 1:
            # for season we might have it in index 1 or index 2
            # e.g. "5x09" TODO is this weirdness necessary
            for i in range(1, len(match)):
                if match[i]:
                    index["clean"] = i
                    break

        return index

    @staticmethod
    def get_season_episode(match):
        clean = None
        m = re.findall(r"[0-9]+", match[0])
        if m and len(m) > 1:
            clean = list(range(int(m[0]), int(m[-1]) + 1))
        # This elif exists entirely for the Seasons 1, 2, 3, 4, etc. case. No other regex gives a number in match[1].
        elif len(match) > 1 and match[1] and m:
            clean = list(range(int(m[0]), int(match[1]) + 1))
        elif m:
            clean = int(m[0])

        return clean

    @staticmethod
    def split_multi(match):
        m = re.split(r"{}+".format(delimiters), match[0])
        clean = list(filter(None, m))

        return clean

    @staticmethod
    def get_subtitles(match):
        # handle multi subtitles
        m = re.split(r"{}+".format(delimiters), match[0])
        m = list(filter(None, m))
        clean = []
        # If it's only 1 result, it's fine if it's just 'subs'.
        if len(m) == 1:
            clean = m
        else:
            for x in m:
                if not re.match("subs?|soft", x, re.I):
                    clean.append(x)

        return clean

    def standardise_clean(self, clean, key, replace, transforms):
        if replace:
            clean = replace
        if transforms:
            for transform in filter(lambda t: t[0], transforms):
                clean = getattr(clean, transform[0])(*transform[1])
        if key == "language" or key == "subtitles":
            clean = self.standardise_languages(clean)
            if not clean:
                clean = "Available"
        if key == "genre":
            clean = self.standardise_genres(clean)
        return clean

    @staticmethod
    def standardise_languages(clean):
        cleaned_langs = []
        for lang in clean:
            for (lang_regex, lang_clean) in langs:
                if re.match(
                    lang_regex,
                    re.sub(
                        link_patterns(patterns["subtitles"][-2:]), "", lang, flags=re.I
                    ),
                    re.IGNORECASE,
                ):
                    cleaned_langs.append(lang_clean)
                    break
        clean = cleaned_langs
        return clean

    @staticmethod
    def standardise_genres(clean):
        standard_genres = []
        for genre in clean:
            for (regex, clean) in genres:
                if re.match(regex, genre, re.IGNORECASE):
                    standard_genres.append(clean)
                    break
        return standard_genres

    # Merge all the match slices (such as when they overlap), then remove
    # them from excess.
    def merge_match_slices(self):
        matches = sorted(self.match_slices, key=lambda match: match[0])

        i = 0
        slices = []
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
        unmatched = self.unmatched_list(keep_punctuation=False)

        # Use the first one as the title
        if unmatched:
            title_start, title_end = unmatched[0][0], unmatched[0][1]

            # If our unmatched is after the first 3 matches, we assume the title is missing
            # (or more likely got parsed as something else), as no torrents have it that
            # far away from the beginning of the release title.
            if (
                len(self.part_slices) > 3
                and title_start
                > sorted(self.part_slices.values(), key=lambda s: s[0])[3][0]
            ):
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
            clean = self._clean_string(raw)
            # Re-add title_start to unrelative the index from raw to self.torrent_name
            self._part("title", (title_start, title_end), clean)
        else:
            self._part("title", None, "")

    def unmatched_list(self, keep_punctuation=True):
        self.merge_match_slices()
        unmatched = []
        prev_start = 0
        # A default so the last append won't crash if nothing has matched
        end = len(self.torrent_name)
        # Find all unmatched strings that aren't just punctuation
        for (start, end) in self.match_slices:
            if keep_punctuation or not re.match(
                delimiters + r"*\Z", self.torrent_name[prev_start:start]
            ):
                unmatched.append((prev_start, start))
            prev_start = end

        # Add the last unmatched slice
        if keep_punctuation or not re.match(
            delimiters + r"*\Z", self.torrent_name[end:]
        ):
            unmatched.append((end, len(self.torrent_name)))

        # If nothing matched, assume the whole thing is the title
        if not self.match_slices:
            unmatched.append((0, len(self.torrent_name)))

        return unmatched

    def fix_known_exceptions(self):
        # Considerations for results that are known to cause issues, such
        # as media with years in them but without a release year.
        for exception in exceptions:
            incorrect_key, incorrect_value = exception["incorrect_parse"]
            if (
                self.parts["title"] == exception["parsed_title"]
                and incorrect_key in self.parts
            ):
                if self.parts[incorrect_key] == incorrect_value or (
                    self.coherent_types and incorrect_value in self.parts[incorrect_key]
                ):
                    self.parts.pop(incorrect_key)
                    self._part("title", None, exception["actual_title"], overwrite=True)

    def get_unmatched(self):
        unmatched = ""
        for (start, end) in self.unmatched_list():
            unmatched += self.torrent_name[start:end]

        return unmatched

    def clean_unmatched(self):
        unmatched = []
        for (start, end) in self.unmatched_list():
            unmatched.append(self.torrent_name[start:end])

        unmatched_clean = []
        for raw in unmatched:
            clean = re.sub(r"(^[-_.\s(),]+)|([-.\s,]+$)", "", raw)
            clean = re.sub(r"[()/]", " ", clean)
            unmatched_clean += re.split(r"\.\.+|\s+", clean)

        filtered = []
        for extra in unmatched_clean:
            if not re.match(
                r"(?:Complete|Season|Full)?[\]\[,.+\- ]*(?:Complete|Season|Full)?\Z",
                extra,
                re.IGNORECASE,
            ):
                filtered.append(extra)
        return filtered
