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


async def get_page_list(products):
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


# ===========================================================================================


def html_parsing(products):

    # product 는 하나의 product, keyword
    for i, product in enumerate(products):
        htmls = product["result"]

        cnt = 1

        # 하나의 html 페이지 parsing
        for j, html in enumerate(htmls):
            p_list = html.find_all("div", class_="product_item__MDtDF")

            one_page = []

            # p_list 는 한 페이지 에 있는 40개의 product 목록
            # p 는 40개 랭킹 판매 목록 중 하나
            for p in p_list:
                product_info = {}
                product_name = p.find("a", class_="product_link__TrAac linkAnchor").text
                m_list = p.find("ul", class_="product_mall_list__RU42O")
                market_list = []
                if not m_list:
                    market = p.find("a", class_="product_mall__hPiEH linkAnchor")
                    market_alter = market.find("img")
                    if not market_alter:
                        market_name = market.text
                        market_list.append(market_name)
                    else:
                        alt_name = market_alter.get("alt")
                        if not alt_name:
                            market_list.append("None")
                        else:
                            market_list.append(alt_name)
                else:
                    for m in m_list:
                        m_name = m.find("span", class_="product_mall_name__MbUf3").text
                        market_list.append(m_name)

                product_info["li_p_ranking"] = cnt
                product_info["li_p_name"] = product_name
                product_info["li_m_list"] = market_list
                cnt += 1
                one_page.append(product_info)
            product["result"][j] = one_page
    return products


# ===========================================================================================


def calculate_ranking(products):

    for product in products:
        product_ranking = get_match_product(product["result"], product["p_name"], product["m_name"])

        product["ranking"] = product_ranking

        del product["result"]

    return products


def get_match_product(market_list, p_name, m_name):
    p_ranking = 201
    for page in market_list:
        for market in page:
            if p_name == market["li_p_name"]:
                for m in market["li_m_list"]:
                    if m_name == m:
                        p_ranking = market["li_p_ranking"]
                        return p_ranking

    return p_ranking
