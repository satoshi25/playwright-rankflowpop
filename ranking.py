from connection import db
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

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


# ===========================================================================================


async def get_ranking(products):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        result = await asyncio.gather(*[fetcher_hub(product, browser) for product in products])
        return result


async def fetcher_hub(product, browser):
    keyword, pagesize = product.get("keyword"), 40
    url_list = []
    for page in range(1, 6):
        shopping_url = (f"https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}"
                        f"&pagingIndex={page}&pagingSize={pagesize}&productSet=total&query={keyword}"
                        f"&sort=rel&timestamp=&viewType=list")
        url_list.append(shopping_url)
    results = []
    for url in url_list:
        result = await ranking_fetcher(browser, url)
        results.append(result)
        await asyncio.sleep(3)

    return results


async def ranking_fetcher(browser, url):
    page = await browser.new_page()

    await page.goto(url)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    await asyncio.sleep(3)

    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")

    return soup.find("a", class_="product_link__TrAac linkAnchor").text
    # result = []
    # s_p_list = soup.find_all("div", class_="product_item__MDtDF")
    # for s_p in s_p_list:
    #     product_name = s_p.find("a", class_="product_link__TrAac linkAnchor").text
    #     m_list = s_p.find("a", class_="product_mall_list__RU42O")
    #     market_list = []
    #     if not m_list:
    #         market_name = s_p.find("a", class_="product_mall__hPiEH linkAnchor").text
    #         market_list.append(market_name)
    #     else:
    #         for m in m_list:
    #             m_name = m.find_all("span", class_="product_mall_name__MbUf3").text
    #             market_list.append(m_name)
    #     product = {
    #         "p_name": product_name,
    #         "m_list": market_list
    #     }
    #     result.append(product)
    #
    # return result
