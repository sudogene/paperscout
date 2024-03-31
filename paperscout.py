import sys
import os
from optparse import OptionParser
import json
import asyncio

from utils.helper import get_results, parse_query, unique_results, filter_results


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", dest="num_days", default=1, help="Past `n` days of publications to search. Default 1.")
    parser.add_option("-q", dest="filename", default="query.txt", help="File containing newline-separated text. Default query.txt.")
    parser.add_option("-o", dest="output", default="papers.json", help="Output JSON file. Default papers.json.")
    (options, args) = parser.parse_args()

    if os.path.isfile(options.filename):
        queries = parse_query(options.filename)
    else:
        print(f"File {options.filename} not found, defaulting to no queries.")
        queries = []

    try:
        num_days = int(options.num_days)
    except ValueError:
        print(f"Invalid number of days {options.num_days}, defaulting to 1.")
        num_days = 1
    
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(get_results(num_days))

    results = unique_results(results)
    results = filter_results(results, queries)
    results = {'query': queries} | results

    with open(options.output, "w") as f:
        json.dump(results, f, indent=4)
