from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from dotenv import load_dotenv

import asyncio
import os
import random

from logger import app_logger


load_dotenv()


async def get_page_list(products):
    p_server = os.getenv("P_SERVER")
    p_user_server = os.getenv("P_USER_SERVER")
    p_ps_server = os.getenv("P_PS_SERVER")
    semaphore = asyncio.Semaphore(5)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            proxy={
                "server": f"{p_server}",
                "username": f"{p_user_server}",
                "password": f"{p_ps_server}",
            }
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            extra_http_headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        )
        results = await asyncio.gather(*[fetcher_hub(semaphore, product, context) for product in products])

        for i in range(len(products)):
            products[i]["result"] = results[i]

        await context.close()
        await browser.close()
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
            await asyncio.sleep(random.uniform(page_interval, page_interval + 3))

        return results


async def ranking_fetcher(browser, url):
    page_loading_time = int(os.getenv("PAGE_LOADING_TIME"))
    timeout_time = int(os.getenv("TIMEOUT_TIME"))
    page = await browser.new_page()

    await page.goto(url, timeout=timeout_time)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    await asyncio.sleep(page_loading_time)

    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")
    await page.close()

    return soup.find("div", class_="basicList_list_basis__uNBZx")


def html_parsing(products):
    ad_cnt = 0
    for product in products:
        htmls = product["result"]

        cnt = 1

        for j, html in enumerate(htmls):
            p_list = html.find_all("div", class_="product_item__MDtDF")
            if not p_list:
                app_logger("Access Denied, html_parsing")
                ad_cnt += 1
                product["result"][j] = None
            else:
                one_page = []

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
    return [products, ad_cnt]


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
