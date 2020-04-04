# parse-torrent-name

> Extract media information from torrent-like filename

![Python versions](https://img.shields.io/badge/Python-2.7%2C%203.3-brightgreen.svg?style=flat-square)

A python port of [Jānis](https://github.com/jzjzjzj)' awesome JavaScript
[library](https://github.com/jzjzjzj/parse-torrent-name).

Extract all possible media information from a filename. Multiple regex 
rules are applied on the filename, each of which extracts appropriate
information. If a rule matches, the corresponding part
is removed from the filename. Finally, what remains is taken as the
title of the content.

### Updates on top of [/u/roidayan's work](https://github.com/roidayan/parse-torrent-name/tree/updates)

- Added more languages in `patterns.py`.
- Added multi-language support.
- Added `AAC2` audio support.
- Improved complete season regex matching.
- Improved TV episode detection.
- Fixed incorrect parsing of titles with a year in them.
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

print info # All details that were parsed
```

PTN works well for both movies and TV seasons & episodes. All meaningful information is
extracted and returned in a dictionary. Text which couldn't be
parsed is returned in the `excess` field.

### Movies

```py
PTN.parse('San Andreas 2015 720p WEB-DL x264 AAC-JYK')
# {
#     'group': 'JYK',
#     'title': 'San Andreas',
#     'resolution': '720p',
#     'codec': 'x264',
#     'year':  2015,
#     'audio': 'AAC',
#     'quality': 'WEB-DL'
# }

PTN.parse('The Martian 2015 540p HDRip KORSUB x264 AAC2 0-FGT')
# {
#     'group': '0-FGT',
#     'title': 'The Martian',
#     'resolution': '540p',
#     'excess': 'KORSUB',
#     'codec': 'x264',
#     'year': 2015,
#     'audio': 'AAC2',
#     'quality': 'HDRip'
# }
```

### TV episodes 

```py
PTN.parse('Mr Robot S01E05 HDTV x264-KILLERS[ettv]')
# {
#     'episode': 5,
#     'season': 1,
#     'title': 'Mr Robot',
#     'codec': 'x264',
#     'group':  'KILLERS',
#     'quality': 'HDTV'
# }

PTN.parse('friends.s02e01.720p.bluray-sujaidr')
# {
#     'episode': 1,
#     'season': 2,
#     'title': 'friends',
#     'resolution': '720p',
#     'group': 'sujaidr',
#     'quality': 'bluray'    
# }
```

### TV seasons

```
PTN.parse('South Park Season 23 Complete 720p AMZN WEB-DL x264 [i_c]')
#  {
#    'title': 'South Park',
#    'season': 23,
#    'resolution': '720p',
#    'codec': 'x264',
#    'quality': 'WEB-DL',
#    'group': '[i_c]',
#    'excess': ['Complete', 'AMZN']
# }
  
PTN.parse('The.X-Files.Complete.S01-S09.1080p.BluRay.x264-GECKOS')
# {
#    'season': [1, 2, 3, 4, 5, 6, 7, 8, 9],
#    'title': 'The X-Files',
#    'resolution': '1080p',
#    'quality': 'BluRay',
#    'codec': 'x264',
#    'group': 'GECKOS'
# }
```

### Note

PTN does not guarantee the fields `group`, `excess` and `episodeName` as these 
fields might be interchanged with each other. This shoudn't affect most 
applications since episode names can be fetched from an online database 
after correctly getting the season and episode number.

### Parts extracted

* audio
* codec
* container
* episode
* episodeName
* excess
* extended
* garbage
* group
* hardcoded
* language
* proper
* quality
* region
* repack
* resolution
* season
* title
* website
* widescreen
* year

## Install

### Automatic

PTN can be installed automatically using `pip`.

```sh
$ pip install git+git://github.com/platelminto/parse-torrent-name.git@main
```

Note that you might require `sudo` permission depending on whether
a virtual environment is used or not.

### Manual

First clone the repository.

```sh
$ git clone https://github.com/platelminto/parse-torrent-name PTN && cd PTN
```

And run the command for installing the package.

```sh
$ python setup.py install
```

## Contributing

Submit a PR, including tests (if applicable) for what you've added. Please provide input torrent names in `tests/files/input.json` and output json objects in `tests/files/output.json` (where the non-guaranteed fields `group`, `excess`, and `episodeName` don't have to be included).

## License

MIT © [Divij Bindlish](http://divijbindlish.in)
