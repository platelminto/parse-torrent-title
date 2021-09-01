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
    help="whether to standardise the output",
)
args = parser.parse_args()

parsed = PTN.parse(args.torrent, standardise=args.standardise)

print(json.dumps(parsed, indent=2))
