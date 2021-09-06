import argparse
import json

import PTN

parser = argparse.ArgumentParser(
    description="Extract media information from torrent-like filename."
)
parser.add_argument("torrent", type=str, help="a torrent-like filename")
parser.add_argument(
    "--raw",
    dest="standardise",
    action="store_const",
    const=False,
    default=True,
    help="don't standardise the output",
)
parser.add_argument(
    "--coherent-types",
    dest="coherent_types",
    action="store_const",
    const=True,
    default=False,
    help="make all non-boolean fields (outside of title and episodeName) into lists."
)
args = parser.parse_args()

parsed = PTN.parse(args.torrent, standardise=args.standardise, coherent_types=args.coherent_types)

print(json.dumps(parsed, indent=2))
