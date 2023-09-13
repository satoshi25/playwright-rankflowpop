import pprint
import asyncio
import time

from connection import get_conditions
from ranking import get_market_url, get_market_name, get_page_list, html_parsing


async def main():
    start = time.time()

    conditions = get_conditions()
    search_list = get_market_url(conditions)
    results = await get_market_name(search_list)
    data = await get_page_list(results)
    parsing_data = html_parsing(data)

    end = time.time()

    pprint.pprint(parsing_data)
    print("time", end - start)

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
