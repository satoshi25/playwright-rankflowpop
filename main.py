import pprint
import asyncio
import time

from ranking import get_conditions, get_market_url, get_market_name


async def main():
    start = time.time()
    conditions = get_conditions()
    search_list = get_market_url(conditions)

    results = await get_market_name(search_list)

    end = time.time()
    print(end - start)
    pprint.pprint(results)

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
