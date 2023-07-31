import json

import feedparser
import numpy

RECENT_FEED = 'http://localhost:9117/api/v2.0/indexers/torrentgalaxy/results/torznab/api?apikey' \
              '=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=2000&q='
RECENT_FEED_2 = 'http://localhost:9117/api/v2.0/indexers/1337x/results/torznab/api?apikey=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=&q='
POPULAR_FEED_TV = 'http://localhost:9117/api/v2.0/indexers/rarbg/results/torznab/api?apikey=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=5030,5040,5045&q='
POPULAR_FEED_MOVIE = 'http://localhost:9117/api/v2.0/indexers/rarbg/results/torznab/api?apikey=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=2030,2040,2045,2050,2060&q='
ANIME_FEED = 'http://localhost:9117/api/v2.0/indexers/torrentgalaxyorg/results/torznab/api?apikey=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=5070&q='
FOREIGN_MOVIE_FEED = 'http://localhost:9117/api/v2.0/indexers/torrentgalaxyorg/results/torznab/api?apikey=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=2010&q='
DOCUMENTARY_FEED = 'http://localhost:9117/api/v2.0/indexers/torrentgalaxyorg/results/torznab/api?apikey=rfvvjrk9r22qe7k2cbdjxdazriemhifq&t=search&cat=5080&q='


recent_results = feedparser.parse(RECENT_FEED)
recent2_results = feedparser.parse(RECENT_FEED_2)
popular_tv_results = feedparser.parse(POPULAR_FEED_TV)
popular_movie_results = feedparser.parse(POPULAR_FEED_MOVIE)
anime_results = feedparser.parse(ANIME_FEED)
foreign_movies_results = feedparser.parse(FOREIGN_MOVIE_FEED)
documentary_results = feedparser.parse(DOCUMENTARY_FEED)


INDENT = 2
SPACE = " "
NEWLINE = "\n"


def to_json(o, level=0):
    ret = ""
    if isinstance(o, dict):
        ret += "{" + NEWLINE
        comma = ""
        for k in sorted(o):
            v = o[k]
            ret += comma
            comma = ",\n"
            ret += SPACE * INDENT * (level + 1)
            ret += '"' + str(k) + '":' + SPACE
            ret += to_json(v, level + 1)

        ret += NEWLINE + SPACE * INDENT * level + "}"
    elif isinstance(o, str):
        ret += '"' + o + '"'
    elif isinstance(o, list):
        if isinstance(o[0], dict):
            ret += "[\n" + SPACE * INDENT * (level + 1) + (",\n" + SPACE * INDENT * (level + 1)).join(
                [to_json(e, level + 1) for e in o]) + "\n]"
        else:
            ret += "[" + ",".join([to_json(e, level + 1) for e in o]) + "]"
    elif isinstance(o, bool):
        ret += "true" if o else "false"
    elif isinstance(o, int):
        ret += str(o)
    elif isinstance(o, float):
        ret += '%.7g' % o
    elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.integer):
        ret += "[" + ','.join(map(str, o.flatten().tolist())) + "]"
    elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.inexact):
        ret += "[" + ','.join(map(lambda x: '%.7g' % x, o.flatten().tolist())) + "]"
    elif o is None:
        ret += 'null'
    else:
        raise TypeError("Unknown type '%s' for json serialization" % str(type(o)))
    return ret

#for entry in [j for i in zip(recent_results['entries'],popular_results['entries']) for j in i]:
for entry in recent2_results['entries']:
    import PTN

    title = entry['title']
    with open('files/seen_inputs.json', 'a+') as seen_inputs:
        if seen_inputs.tell() == 0:
            seen_inputs.write('[]')
        seen_inputs.seek(0)
        seen = json.load(seen_inputs)
        if title in seen:
            continue
    print(title)
    raw_parsed = PTN.parse(title, standardise=False)
    standard_parsed = PTN.parse(title, standardise=True)
    difference_parsed = dict()
    standard_filtered = dict()
    standard_filtered['title'] = raw_parsed['title']

    for key, raw_value in raw_parsed.items():
        standard_value = standard_parsed[key]
        if standard_value != raw_value:
            difference_parsed[key] = [raw_value, standard_value]
            standard_filtered[key] = standard_value
        else:
            difference_parsed[key] = raw_value

    print(to_json(difference_parsed))
    print()

    option = input('(s)ave/(i)gnore/s(k)ip: ')

    if option == 's' or option == 'save':
        with open('files/input.json', 'r') as inputs_file:
            inputs = json.load(inputs_file)
        inputs.append(title)
        with open('files/input.json', 'w') as inputs_file:
            inputs_file.write(json.dumps(inputs, indent=2))
        with open('files/seen_inputs.json', 'r') as seen_inputs:
            inputs = json.load(seen_inputs)
        inputs.append(title)
        with open('files/seen_inputs.json', 'w') as seen_inputs:
            seen_inputs.write(json.dumps(inputs))

        filtered_parsed = raw_parsed.copy()
        # filtered_parsed.pop('group', '')
        filtered_parsed.pop('excess', '')
        with open('files/output_raw.json', 'r') as outputs_file:
            outputs = json.load(outputs_file)
        outputs.append(filtered_parsed)
        with open('files/output_raw.json', 'w') as outputs_file:
            outputs_file.write(to_json(outputs))

        with open('files/output_standard.json', 'r') as outputs_file:
            outputs = json.load(outputs_file)
        outputs.append(standard_filtered)
        with open('files/output_standard.json', 'w') as outputs_file:
            outputs_file.write(to_json(outputs))

    elif option == 'i' or option == 'ignore':
        with open('files/seen_inputs.json', 'r') as seen_inputs:
            inputs = json.load(seen_inputs)
        inputs.append(title)
        with open('files/seen_inputs.json', 'w') as seen_inputs:
            seen_inputs.write(json.dumps(inputs))
    elif option == 'k' or option == 'skip':
        continue
    else:
        break
