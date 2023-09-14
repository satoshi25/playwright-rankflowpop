from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from dotenv import load_dotenv

import asyncio
import os


load_dotenv()


async def get_page_list(products):
    semaphore = asyncio.Semaphore(5)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()

        results = await asyncio.gather(*[fetcher_hub(semaphore, product, browser) for product in products])

        for i in range(len(products)):
            products[i]["result"] = results[i]

        return products


async def fetcher_hub(semaphore, product, browser):
    limit_page = int(os.getenv("LIMIT_PAGE")) + 1
    page_interval = int(os.getenv("PAGE_INTERVAL"))
    page_list_cnt = int(os.getenv("PAGE_LIST_CNT"))

    async with semaphore:
        keyword, pagesize = product.get("keyword"), page_list_cnt
        url_list = []
        for page in range(1, limit_page):
            shopping_url = (f"https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}"
                            f"&pagingIndex={page}&pagingSize={pagesize}&productSet=total&query={keyword}"
                            f"&sort=rel&timestamp=&viewType=list")
            url_list.append(shopping_url)
        results = []
        for url in url_list:
            result = await ranking_fetcher(browser, url)
            results.append(result)
            await asyncio.sleep(page_interval)

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
    for product in products:
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
        product_ranking = get_match_product(product["result"], product["p_name"], product["s_name"])

        product["ranking"] = product_ranking

        del product["result"]

    return products


def get_match_product(market_list, p_name, m_name):
    p_ranking = -1
    for page in market_list:
        for market in page:
            if p_name == market["li_p_name"]:
                for m in market["li_m_list"]:
                    if m_name == m:
                        p_ranking = market["li_p_ranking"]
                        return p_ranking

    return p_ranking
