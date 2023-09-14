from datetime import date
from dotenv import load_dotenv

import asyncio
import time
import os

from connection import get_conditions, insert_product_ranking
from ranking import get_page_list, html_parsing, calculate_ranking
from logger import logger


load_dotenv()


async def main():
    start = time.time()
    today = date.today()
    interval = int(os.getenv("USER_INTERVAL"))
    error_cnt = -1
    is_error = False

    while error_cnt == -1 or (is_error and error_cnt < 3):
        if error_cnt == -1:
            error_cnt += 1
        try:
            users_products = get_conditions()

            for user_product in users_products:
                user_products = users_products[user_product]

                get_page_html_list = await get_page_list(user_products)
                parsing_data = html_parsing(get_page_html_list)
                product_ranking_data = calculate_ranking(parsing_data)

                insert_product_ranking(product_ranking_data, today)
                print(f"user {product_ranking_data[0]['user_id']} DB insert 완료")

                is_error = False
                await asyncio.sleep(interval)

        except Exception as error:
            logger.error(f"Error: {error}", exc_info=True)
            error_cnt += 1
            is_error = True
            await asyncio.sleep(interval*2)

    end = time.time()
    print(f"{today} DB insert 완료, 소요 시간: {end - start}")

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
