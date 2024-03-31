import datetime

import asyncio
import aiohttp
from aiohttp.client import ClientSession

from .api import apis


async def get_results(days=1, retries=3):
    today = datetime.date.today()
    prev_date = today - datetime.timedelta(days=days)
    timeout = aiohttp.ClientTimeout(connect=60, total=180)
    results = {}
    for attempt in range(retries):
        try:
            async with ClientSession(timeout=timeout) as session:
                api_tasks = [api(session, prev_date, today) for api in apis.values()]
                api_results = await asyncio.gather(*api_tasks)
                results = {k: v for k, v in zip(apis.keys(), api_results)}
        except Exception as e:
            if attempt >= retries:
                print(f"Max retries exceeded. Try again later :(")
    return results


def parse_query(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()


def unique_results(results):
    dois = set()
    unique_results = {k: [] for k in results.keys()}
    for k, v in results.items():
        for paper in v:
            if paper["doi"] not in dois:
                dois.add(paper["doi"])
                unique_results[k].append(paper)
    return unique_results


def filter_results(results, queries):
    if not queries:
        return results
    filtered_results = {k: [] for k in results.keys()}
    for k, v in results.items():
        for paper in v:
            paper_text = " ".join(paper.values()).lower()
            for q in queries:
                if q in paper_text:
                    filtered_results[k].append(paper)
                    break
    return filtered_results