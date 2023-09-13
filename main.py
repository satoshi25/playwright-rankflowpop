import pprint
import asyncio
import time

from connection import get_conditions
from ranking import get_market_url, get_market_name, get_ranking


async def main():
    start = time.time()

    conditions = get_conditions()
    search_list = get_market_url(conditions)
    results = await get_market_name(search_list)
    data = await get_ranking(results)

    end = time.time()

    pprint.pprint(data)
    print("time", end - start)

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
