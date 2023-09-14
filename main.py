import pprint
import asyncio
import time

from connection import get_conditions
from ranking import get_page_list, html_parsing, calculate_ranking


async def main():
    start = time.time()

    users_products = get_conditions()
    for user_product in users_products:
        get_page_html_list = await get_page_list(user_product)
        parsing_data = html_parsing(get_page_html_list)
        product_ranking_data = calculate_ranking(parsing_data)
        pprint.pprint(product_ranking_data)
        print(f"{product_ranking_data[0]['user_id']} DB insert 완료")
        await asyncio.sleep(20)

    end = time.time()
    print("time", end - start)

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
