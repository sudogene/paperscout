import os
from optparse import OptionParser
import datetime
import json

import asyncio
import aiohttp
from aiohttp.client import ClientSession

from utils.api import apis


async def get_results(days=3):
    today = datetime.date.today()
    prev_date = today - datetime.timedelta(days=days)
    timeout = aiohttp.ClientTimeout(connect=60, total=180)
    async with ClientSession(timeout=timeout) as session:
        api_tasks = [api(session, prev_date, today) for api in apis.values()]
        api_results = await asyncio.gather(*api_tasks)
    return {k: v for k, v in zip(apis.keys(), api_results)}


def parse_query(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()


def filter_results(results, queries):
    if not queries:
        return results
    filtered_results = {k: [] for k in results.keys()}
    for k, v in results.items():
        for paper in v:
            paper_text = " ".join(paper.values())
            for q in queries:
                if q in paper_text:
                    filtered_results[k].append(paper)
    return filtered_results


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
    
    try:
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(get_results(num_days))
    except Exception as e:
        print(f"Error fetching papers, try again later: {e}")
    filtered_results = filter_results(results, queries)
    
    with open(options.output, "w") as f:
        json.dump(filtered_results, f, indent=4)
