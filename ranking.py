from connection import db
from bs4 import BeautifulSoup

import aiohttp
import asyncio


def get_conditions():
    # sql = ("SELECT upk.user_id, upk.id, p.product_url, p.product_name, k.keyword "
    #        "FROM user_product_keyword as upk "
    #        "JOIN product_keyword pk ON upk.product_keyword_id = pk.id "
    #        "JOIN product p ON pk.product_id = p.id "
    #        "JOIN keyword k ON pk.keyword_id = k.id "
    #        "ORDER BY upk.user_id ASC;")

    sql = ("SELECT upk.user_id, upk.id, p.product_url, p.product_name, k.keyword "
           "FROM user_product_keyword as upk "
           "JOIN product_keyword pk ON upk.product_keyword_id = pk.id "
           "JOIN product p ON pk.product_id = p.id "
           "JOIN keyword k ON pk.keyword_id = k.id "
           "WHERE upk.user_id = 1 "
           "ORDER BY upk.user_id ASC;")
    cursor = db.cursor()
    cursor.execute(sql)
    p_list = cursor.fetchall()

    product_list = []
    for item in p_list:
        data = {
            "user_id": item[0],
            "upk_id": item[1],
            "p_url": item[2],
            "p_user_name": item[3],
            "keyword": item[4],
            "m_url": "",
            "m_name": "",
            "p_name": "",
            "result": "",
        }
        product_list.append(data)
    return product_list


# ===========================================================================================

def get_market_url(p_list):
    for p in p_list:
        p_url = p["p_url"]
        m_profile = "profile?cp=1"
        p["m_url"] = f"{p_url.split('products')[0]}{m_profile}"
    return p_list


async def get_market_name(products):
    async with aiohttp.ClientSession() as session:
        m_url_results = await asyncio.gather(
            *[condition_fetcher(session, product) for product in products]
        )
        return m_url_results


async def condition_fetcher(session, product):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    async with session.get(product["m_url"], headers=headers, ssl=False) as response:
        if response.status == 200:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            product["m_name"] = soup.find("strong", class_="name").text
    async with session.get(product["p_url"], headers=headers, ssl=False) as response:
        if response.status == 200:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            product["p_name"] = soup.find("h3", class_="_22kNQuEXmb _copyable").text
            return product
