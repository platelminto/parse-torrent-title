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

### Updates on top of [/u/roidayan's work](https://github.com/roidayan/parse-torrent-name/tree/updates)

- Added standardisation of output strings.
- Added multi-language support.
- Added multi-episode support.
- Improved support for anime tv releases.
- Improved support for Indian releases.
- Added various fields (see field list below).
- Added proper subtitle support.
- Added proper support for matching episode names.
- Added support for full `YYYY-MM-DD`-type dates, usually useful for daily shows that otherwise have no episode name.
- Added support for 2020s release years.
- Added exceptions list for media with known, non-fixable issues.
- Expanded and improved matching for various fields.
- Fixed incorrect parsing of titles containing years.
- Added more tests and cleaned up previous ones.


### [/u/roidayan's work](https://github.com/roidayan/parse-torrent-name/tree/updates) on top of [/u/divijbindlish's original python port](https://github.com/divijbindlish/parse-torrent-name)

- Added support for complete season parsing (either just a full season, or a range), not just single episodes.
- Added to various fields' patterns.
- Improved season & episode matching.
- Fixed group names from having the container & bt site name.
- Added more tests.


## Why?

Online APIs by providers like
[TMDb](https://www.themoviedb.org/documentation/api),
[TVDb](http://thetvdb.com/wiki/index.php?title=Programmers_API), and
[OMDb](http://www.omdbapi.com/) don't react well to
queries which include any kind of extra information. To get proper results from
these APIs, only the title of the content should be provided in the search
query. The accuracy of the results can be
improved by passing in the year, which can also be extracted using this library.

## Usage

```py
import PTN

info = PTN.parse('A freakishly cool movie or TV episode')

print(info) # All details that were parsed.
```

Both movies and TV (seasons & episodes) can be parsed. All meaningful information is
extracted and returned in a dictionary. Text which couldn't be
parsed is returned in the `excess` field.

### Raw info

The matches in the torrent name are standardised into specific strings, according to scene rules where possible - `'WEBDL'`, `'WEB DL'`, and `'HDRip'` are all converted to `'WEB-DL'`, for example. `'DDP51'` becomes `'Dolby Digital Plus 5.1'`. `['ita', 'eng']` becomes `['Italian', 'English']`.To disable this, and return just what was matched in the torrent, run:

```py
import PTN

info = PTN.parse('A freakishly cool movie or TV episode', standardise=False)

print(info) # All details that were parsed as they exist in the torrent name.
```


### Movies

```py
PTN.parse('San Andreas 2015 720p WEB-DL x264 AAC-JYK')
# {
#     'group': 'JYK',
#     'title': 'San Andreas',
#     'resolution': '720p',
#     'codec': 'H.264',
#     'year':  2015,
#     'audio': 'AAC',
#     'quality': 'WEB-DL'
# }

PTN.parse('The Martian 2015 540p HDRip KORSUB x264 AAC2 0-FGT')
# {
#     'group': '0-FGT',
#     'title': 'The Martian',
#     'resolution': '540p',
#     'codec': 'H.264',
#     'year': 2015,
#     'audio': 'AAC 2.0',
#     'quality': 'WEB-DL',
#     'subtitles': 'Korean'
# }
```

### TV episodes 

```py
PTN.parse('Mr Robot S01E05 HDTV x264-KILLERS[ettv]')
# {
#     'episode': 5,
#     'season': 1,
#     'title': 'Mr Robot',
#     'codec': 'H.264',
#     'group':  'KILLERS',
#     'encoder': 'ettv',
#     'quality': 'HDTV'
# }

PTN.parse('friends.s02e01.720p.bluray-sujaidr')
# {
#     'episode': 1,
#     'season': 2,
#     'title': 'friends',
#     'resolution': '720p',
#     'group': 'sujaidr',
#     'quality': 'Blu-ray'    
# }
```

### TV seasons

```py
PTN.parse('South Park Season 23 Complete 720p AMZN WEB-DL x264 [i_c]')
# {
#     'title': 'South Park',
#     'season': 23,
#     'resolution': '720p',
#     'codec': 'H.264',
#     'quality': 'WEB-DL',
#     'encoder': 'i_c',
#     'producer': 'Amazon Studios'
# }

  
PTN.parse('The.X-Files.Complete.S01-S09.1080p.BluRay.x264-GECKOS')
# {
#     'season': [1, 2, 3, 4, 5, 6, 7, 8, 9],
#     'title': 'The X-Files',
#     'resolution': '1080p',
#     'quality': 'Blu-ray',
#     'codec': 'H.264',
#     'group': 'GECKOS'
# }
```

### Note

The fields `group`, `excess`, and `episodeName` are not guaranteed, as these 
fields might be interchanged with each other. This shoudn't affect most 
applications since episode names can be fetched from an online database 
after correctly getting the season and episode number.

### Parts extracted

* audio
* bitDepth
* codec
* container
* day
* documentary
* encoder
* episode
* episodeName
* excess
* extended
* group
* hardcoded
* internal
* language
* month
* producer
* proper
* quality
* readnfo
* region
* repack
* resolution
* sbs
* season
* size
* subtitles
* title
* unrated
* website
* widescreen
* year
* 3d

## Install

### Automatic

PTN can be installed automatically using `pip`.

```sh
$ pip install parse-torrent-title
```

Note that you might require `sudo` permission depending on whether
a virtual environment is used or not.

### Manual

First clone the repository.

```sh
$ git clone https://github.com/platelminto/parse-torrent-title PTN && cd PTN
```

And run the command for installing the package.

```sh
$ python setup.py install
```

## Contributing

Submit a PR on the `dev` branch, including tests for what gets newly matched (if applicable). Please provide input torrent names in `tests/files/input.json` and full output json objects (with `standardise=False`) in `tests/files/output_raw.json` (where the fields `group`, `excess`, and `episodeName` don't have to be included). Also add the standardised output to `tests/files/output_standard.json`, only including fields that are changed, along with `title`.

## License

MIT © 2015-2017 [Divij Bindlish](http://divijbindlish.in)

MIT © 2020 [Giorgio Momigliano](https://github.com/platelminto)
