import pprint
import asyncio
import time

from connection import get_conditions
from ranking import get_market_url, get_market_name, get_page_list, html_parsing, calculate_ranking


async def main():
    start = time.time()

    conditions = get_conditions()
    search_list = get_market_url(conditions)
    get_market_named_list = await get_market_name(search_list)
    get_page_html_list = await get_page_list(get_market_named_list)
    parsing_data = html_parsing(get_page_html_list)
    product_ranking_data = calculate_ranking(parsing_data)

    end = time.time()

    pprint.pprint(product_ranking_data)
    print("time", end - start)

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
