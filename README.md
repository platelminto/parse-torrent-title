# parse-torrent-title

> Extract media information from torrent-like filename

![Python versions](https://img.shields.io/badge/Python-2.7%2C%203.5-brightgreen.svg?style=flat-square)

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

Movies, series (seasons & episodes), and subtitles can be parsed. All meaningful information is
extracted and returned in a dictionary. Text which couldn't be
parsed is returned in the `excess` field.

```py
import PTN


PTN.parse('The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]')
# {
#     'encoder': 'ASAP',
#     'title': 'The Walking Dead',
#     'season':  5,
#     'episode': 3,
#     'resolution': '720p',
#     'codec': 'H.264',
#     'quality': 'HDTV',
#     'website': 'ettv'
# }

PTN.parse('Vacancy (2007) 720p Bluray Dual Audio [Hindi + English] ⭐800 MB⭐ DD - 2.0 MSub x264 - Shadow (BonsaiHD)')
# {
#     'encoder': 'Shadow',
#     'title': 'Vacancy',
#     'resolution': '720p',
#     'codec': 'H.264',
#     'year':  2007,
#     'audio': 'Dolby Digital 2.0',
#     'quality': 'Blu-ray',
#     'language': ['Hindi', 'English'],
#     'subtitles': 'Available',
#     'size': 800MB,
#     'website': BonsaiHD
#     'excess': '⭐⭐'
# }

PTN.parse('Deadliest.Catch.S00E66.No.Safe.Passage.720p.AMZN.WEB-DL.DDP2.0.H.264-NTb[TGx]')
# {
#     'encoder': 'NTb',
#     'title': 'Deadliest Catch',
#     'resolution': '720p',
#     'codec': 'H.264',
#     'audio' : 'Dolby Digital Plus 2.0',
#     'network': 'Amazon Studios',
#     'season':  0,
#     'episode': 66,
#     'quality': 'WEB-DL',
#     'episodeName': 'No Safe Passage',
#     'website': 'TGx'
# }

PTN.parse('Insecure.S04.COMPLETE.720p.AMZN.WEBRip.x264-GalaxyTV')
# {
#     'title': 'Insecure'
#     'encoder': 'GalaxyTV',
#     'codec': 'H.264',
#     'season': 4,
#     'resolution': '720p',
#     'network': 'Amazon Studios',
#     'quality': 'WEBRip',
# }
```

More examples (inputs and outputs) can be found looking through `tests/files`.

## CLI

You can use PTN from your command line, where the output will be printed as JSON:

```sh
$ python cli.py 'Insecure.S04.COMPLETE.720p.AMZN.WEBRip.x264-GalaxyTV'

 {
     'title': 'Insecure'
     'encoder': 'GalaxyTV',
     'codec': 'H.264',
     'season': 4,
     'resolution': '720p',
     'network': 'Amazon Studios',
     'quality': 'WEBRip',
 }
```

For help, use the `-h` or `--help` flag:

```sh
$ python cli.py --help
```

This will provide a brief overview of the available options and their usage.

### Raw info

The matches in the torrent name are standardised into specific strings, according to scene rules where possible - `'WEBDL'`, `'WEB DL'`, and `'HDRip'` are all converted to `'WEB-DL'`, for example. `'DDP51'` becomes `'Dolby Digital Plus 5.1'`. `['ita', 'eng']` becomes `['Italian', 'English']`.To disable this, and return just what was matched in the torrent, run:

```py
PTN.parse('A freakishly cool movie or TV episode', standardise=False)
```

In the CLI, you can use the `--raw` flag:

```sh
$ python cli.py --raw 'A freakishly cool movie or TV episode'
```

### Types of parts

The types of parts can be strings, integers, booleans, or lists of the first 2. To simplify this, you can enable the `coherent_types` flag. This will override the types described below according to these rules:
- `title` and `episodeName` will always be strings.
- All other non-boolean fields will become lists of the type they currently are. For example, `language` will always be a list of strings, and `episode` a list of episodes. This can be weird for some fields, but it avoids a lot of `isinstance` calls - just always use `x in y` and you should be fine.
- Boolean types will remain as booleans.

To enable this flag:
```py
PTN.parse('An even cooler movie or TV episode', coherent_types=True)
```

In the CLI, you can use the `--coherent-types` flag:

```sh
$ python cli.py --coherent-types 'A freakishly cool movie or TV episode'
```

### Parts extracted

* **audio**         *(string)*
* **bitDepth**      *(integer)*
* **codec**         *(string)*
* **day**           *(integer)*
* **directorsCut**  *(boolean)*
* **documentary**   *(boolean)*
* **encoder**       *(string)*
* **episode**       *(integer, integer list)*
* **episodeName**   *(string)*
* **excess**        *(string, string list)*
* **extended**      *(boolean)*
* **filetype**      *(string)*
* **fps**           *(integer)*
* **genre**         *(string, string list)*
* **hardcoded**     *(boolean)*
* **hdr**           *(boolean)*
* **internal**      *(boolean)*
* **internationalCut** *(boolean)*
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
* **site**       *(string)*
* **size**          *(string)*
* **subtitles**     *(string, string list)*
* **title**         *(string)*
* **unrated**       *(boolean)*
* **untouched**     *(boolean)*
* **upscaled**      *(boolean)*
* **widescreen**    *(boolean)*
* **year**          *(integer)*
* **3d**            *(boolean)*

## Contributing

Submit a PR on the `dev` branch. If you have changed the regex for a pattern, I can assume this is because you had a title that was being incorrectly processed, and your change fixes it. Please add the title to the test suite!

To add new titles to the tests, you have 2 options (the first is easier):
- Add the titles to `tests/test_generator`'s main method (in `add_titles()`), and run it. When asked for input, type 's', and it will automatically add what's needed to `files/input.json`, `files/output_raw.json`, and `files/output_standard.json`. The fields `encoder`, `excess`, `site`, and `episodeName` don't always have to be correct - if they're giving you issues, or seem wrong, feel free to manually remove them from the output test files.

- Otherwise, you must add input torrent names to `tests/files/input.json` and full output json objects (with `standardise=False`) to `tests/files/output_raw.json`. Also add the standardised output to `tests/files/output_standard.json`, only including fields that are different from `output_raw.json`, along with `title`.

## Additions to parse-torrent-name

Below are the additions that have been made to [/u/divijbindlish's original repo](https://github.com/divijbindlish/parse-torrent-name), including other contributors' work. parse-torrent-title was initially forked from [here](https://github.com/roidayan/parse-torrent-name/tree/updates), but a lot of extra work has been done since, and given that the original repo is inactive, it was unforked.

### Updates on top of [/u/roidayan's work](https://github.com/roidayan/parse-torrent-name/tree/updates)

- Added standardisation of output strings.
- Added multi-language support.
- Added multi-episode support.
- Added a basic CLI.
- Added thread safety.
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
- Fixed groups/encoders/websites mixups: a group/encoder is now just called an encoder, and a public tracker site goes under website.
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
