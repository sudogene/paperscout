import requests
import datetime
import time
import aiohttp


async def biorxiv(session, start_date: datetime.date, end_date: datetime.date, wait=0.5):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    url = f"https://api.biorxiv.org/details/biorxiv/{start_date_str}/{end_date_str}"
    async with session.get(url) as response:
        response_json = await response.json()
        total_results = int(response_json["messages"][0]["total"])
        results = response_json["collection"]
        for i in range(100, total_results, 100):
            time.sleep(wait)
            async with session.get(f"{url}/{i}") as response:
                response_json = await response.json()
                results.extend(response_json["collection"])
        return results


async def medrxiv(session, start_date: datetime.date, end_date: datetime.date, wait=0.5):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    url = f"https://api.biorxiv.org/details/medrxiv/{start_date_str}/{end_date_str}"
    async with session.get(url) as response:
        response_json = await response.json()
        total_results = int(response_json["messages"][0]["total"])
        results = response_json["collection"]
        for i in range(100, total_results, 100):
            time.sleep(wait)
            async with session.get(f"{url}/{i}") as response:
                response_json = await response.json()
                results.extend(response_json["collection"])
        return results


apis = {"biorxiv": biorxiv, "medrxiv": medrxiv}