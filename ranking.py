from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

import aiohttp
import asyncio


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

        results = await asyncio.gather(*[fetcher_hub(product, browser) for product in products])
        # product 별로 한 페이지 html 요소 5개를 가진 list 를 묶은 list 가 반환 된다.
        # results = [ [의자1html, 의자2html, 의자3html...], [바지1html, 바지2html,...] ... ]

        for i in range(len(products)):
            products[i]["result"] = results[i]

        return products
        # products = [
        #               {
        #                   "user_id": 1,
        #                   "upk_id": 1,
        #                   "p_url": "item.com",
        #                   "p_user_name": "item",
        #                   "keyword": "word1",
        #                   "m_url": "item_market.com",
        #                   "m_name": "item_market",
        #                   "p_name": "item",
        #                   "result": [],
        #                   "html": [의자1html, 의자2html, 의자3html, ...],
        #               }, ...
        #            ]


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

    return soup.find("div", class_="basicList_list_basis__uNBZx")
