from datetime import date
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

import asyncio
import random
import os

from connection import get_conditions, insert_product_ranking
from ranking import get_page_list, html_parsing, calculate_ranking
from logger import error_logger, app_logger


load_dotenv()

server_timezone = timezone("Asia/Seoul")
hour = os.getenv("TASK_HOUR")
minute = os.getenv("TASK_MINUTE")


async def main():
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
                app_logger.info(f"user {product_ranking_data[0]['user_id']} DB insert complete")

                is_error = False
                await asyncio.sleep(random.uniform(interval, interval + 5))

        except Exception as error:
            error_logger.error(f"Error: {error}", exc_info=True)
            error_cnt += 1
            is_error = True
            await asyncio.sleep(interval*2)

    app_logger.info(f"{today} DB insert complete")


scheduler = AsyncIOScheduler()
scheduler.add_job(main, 'cron', hour=hour, minute=minute, timezone=server_timezone)
scheduler.start()


if __name__ == "__main__":
    asyncio.get_event_loop().run_forever()
