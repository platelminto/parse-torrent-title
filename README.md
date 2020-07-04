# parse-torrent-title

> Extract media information from torrent-like filename

![Python versions](https://img.shields.io/badge/Python-2.7%2C%203.5-brightgreen.svg?style=flat-square)
[![Build Status](https://travis-ci.com/platelminto/parse-torrent-title.svg?branch=master)](https://travis-ci.com/platelminto/parse-torrent-title)

Originally based off of [this JavaScript
library](https://github.com/jzjzjzj/parse-torrent-name).

Extract all possible media information from a filename. Multiple regex 
rules are applied on the filename, each of which extracts appropriate
information. If a rule matches, the corresponding part
is removed from the filename. Finally, what remains is taken as the
title of the content.


## Install

PTN can be installed automatically using `pip`.

```sh
$ pip install parse-torrent-title
```

### Requirements

Requirements are **optional**. That being said, the `regex` library increases performance on Python 2 by more than 10x, so it might be worth installing with:

```sh
$ pip install -r requirements.txt
```

With Python 3, the default `re` module is faster than `regex`, so it will always be used regardless of installed requirements.

## Why?

Online APIs by providers like
[TMDb](https://www.themoviedb.org/documentation/api),
[TVDb](http://thetvdb.com/wiki/index.php?title=Programmers_API), and
[OMDb](http://www.omdbapi.com/) don't react well to
queries which include any kind of extra information. To get proper results from
these APIs, only the title of the content should be provided in the search
query. The accuracy of the results can be
improved by passing in the year, which can also be extracted using this library.

## Examples

Both movies and TV (seasons & episodes) can be parsed. All meaningful information is
extracted and returned in a dictionary. Text which couldn't be
parsed is returned in the `excess` field.

```py
PTN.parse('The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]')
# {
#     'group': 'ASAP',
#     'title': 'The Walking Dead',
#     'season':  5,
#     'episode': 3,
#     'resolution': '720p',
#     'codec': 'H.264',
#     'quality': 'HDTV',
#     'encoder': 'ettv'
# }

PTN.parse('Vacancy (2007) 720p Bluray Dual Audio [Hindi + English] ⭐800 MB⭐ DD - 2.0 MSub x264 - Shadow (BonsaiHD)')
# {
#     'group': 'BonsaiHD',
#     'title': 'Vacancy',
#     'resolution': '720p',
#     'codec': 'H.264',
#     'year':  2007,
#     'audio': 'Dolby Digital 2.0',
#     'quality': 'Blu-ray',
#     'language': ['Hindi', 'English'],
#     'subtitles': 'Available',
#     'size': 800MB,
#     'excess': ['⭐⭐', 'Shadow']
# }

PTN.parse('Deadliest.Catch.S00E66.No.Safe.Passage.720p.AMZN.WEB-DL.DDP2.0.H.264-NTb[TGx]')
# {
#     'group': 'NTb',
#     'title': 'Deadliest Catch',
#     'resolution': '720p',
#     'codec': 'H.264',
#     'audio' : 'Dolby Digital Plus 2.0',
#     'network': 'Amazon Studios',
#     'season':  0,
#     'episode': 66,
#     'quality': 'WEB-DL',
#     'episodeName': 'No Safe Passage',
#     'encoder': 'TGx'
# }

PTN.parse('Z Nation (2014)S01-01-13 (2014) Full Season.XviD - Italian English.Ac3.Sub.ita.eng.MIRCrew')
# {
#     'group': '.MIRCrew',
#     'title': 'Z Nation',
#     'season': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
#     'codec': 'Xvid',
#     'year':  2014,
#     'audio': 'Dolby Digital',
#     'language': ['Italian', 'English'],
#     'subtitles': ['Italian', 'English']
# }
```

More examples (inputs and outputs) can be found looking through `tests/files`.

### Raw info

The matches in the torrent name are standardised into specific strings, according to scene rules where possible - `'WEBDL'`, `'WEB DL'`, and `'HDRip'` are all converted to `'WEB-DL'`, for example. `'DDP51'` becomes `'Dolby Digital Plus 5.1'`. `['ita', 'eng']` becomes `['Italian', 'English']`.To disable this, and return just what was matched in the torrent, run:

```py
PTN.parse('A freakishly cool movie or TV episode', standardise=False)
```

### Parts extracted

* **audio**         *(string)*
* **bitDepth**      *(integer)*
* **codec**         *(string)*
* **container**     *(string)*
* **day**           *(integer)*
* **directorsCut**  *(boolean)*
* **documentary**   *(boolean)*
* **encoder**       *(string)*
* **episode**       *(integer, integer list)*
* **episodeName**   *(string)*
* **excess**        *(string, string list)*
* **extended**      *(boolean)*
* **fps**           *(integer)*
* **group**         *(string)*
* **hardcoded**     *(boolean)*
* **hdr**           *(boolean)*
* **internal**      *(boolean)*
* **language**      *(string, string list)*
* **limited**       *(boolean)*
* **month**         *(integer)*
* **network**       *(string)*
* **proper**        *(boolean)*
* **quality**       *(string)*
* **readnfo**       *(boolean)*
* **region**        *(string)*
* **remastered**    *(boolean)*
* **remux**         *(boolean)*
* **repack**        *(boolean)*
* **resolution**    *(string)*
* **sbs**           *(string)*
* **season**        *(integer, integer list)*
* **size**          *(string)*
* **subtitles**     *(string, string list)*
* **title**         *(string)*
* **unrated**       *(boolean)*
* **untouched**     *(boolean)*
* **upscaled**      *(boolean)*
* **website**       *(string)*
* **widescreen**    *(boolean)*
* **year**          *(integer)*
* **3d**            *(boolean)*

## Contributing

Submit a PR on the `dev` branch, including tests for what gets newly matched (if applicable). Please provide input torrent names in `tests/files/input.json` and full output json objects (with `standardise=False`) in `tests/files/output_raw.json` (where the fields `group`, `excess`, and `episodeName` don't have to be included). Also add the standardised output to `tests/files/output_standard.json`, only including fields that are changed, along with `title`.

## Additions to parse-torrent-name

Below are the additions that have been made to [/u/divijbindlish's original repo](https://github.com/divijbindlish/parse-torrent-name), including other contributors' work. parse-torrent-title was initially forked from [here](https://github.com/roidayan/parse-torrent-name/tree/updates), but a lot of extra work has been done since, and given that the original repo is inactive, it was unforked.

### Updates on top of [/u/roidayan's work](https://github.com/roidayan/parse-torrent-name/tree/updates)

- Added standardisation of output strings.
- Added multi-language support.
- Added multi-episode support.
- Improved support for anime tv releases.
- Improved support for Indian releases.
- Added various fields (see field list above).
- Added proper subtitle support.
- Added proper support for matching episode names.
- Added support for full `YYYY-MM-DD`-type dates, usually useful for daily shows that otherwise have no episode name.
- Added support for 2020s release years.
- Added exceptions list for media with known, non-fixable issues.
- Expanded and improved matching for various fields.
- Fixed incorrect parsing of titles containing years.
- Added more tests and cleaned up previous ones.


### [/u/roidayan's work](https://github.com/roidayan/parse-torrent-name/tree/updates) on top of [the original](https://github.com/divijbindlish/parse-torrent-name)

- Added support for complete season parsing (either just a full season, or a range), not just single episodes.
- Added to various fields' patterns.
- Improved season & episode matching.
- Fixed group names from having the container & bt site name.
- Added more tests.

## License

MIT © 2015-2017 [Divij Bindlish](http://divijbindlish.in)

MIT © 2020 [Giorgio Momigliano](https://github.com/platelminto)
