import requests
import io
import json
import re
import time
import math
import random

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


ITEMS_PER_PAGE = 240


def search_ebay(keyword, exclude, page=1):
    headers = {'User-Agent': ua.random}
    query = keyword.replace(" ", "+")
    # Sort by Price + Shipping: Lowest First
    url = f"https://www.ebay.ca/sch/i.html?_nkw={query}&_sop=15&_pgn=1&_dcat=139973&Region%2520Code=%21%7CRegion%2520Free%7CNTSC%252DU%252FC%2520%2528US%252FCanada%2529%7CPAL&LH_BIN=1&_sop=15&_ipg={ITEMS_PER_PAGE}&_pgn={page}"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    
    results_count = 0
    try:
        count_heading = soup.select(".result-count__count-heading")
        print('count_heading', count_heading)
        if len(count_heading):
            results_count = count_heading[0].get_text()
            match = re.search(r"(\d[\d,]*)", results_count)
            if match:
                results_count = int(match.group(1).replace(",", ""))
            
        else:
            raise Exception("Something went wrong.")    

    except Exception as exception:
        print(exception)
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        

    print('results_count', results_count)

    for item in soup.select(".s-item"):
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        link = item.select_one(".s-item__link")
        image_url = item.select_one(".s-item__image-wrapper.image-treatment img")["src"].replace("s-l50", "s-l300")
        if image_url == "https://ir.ebaystatic.com/cr/v/c1/s_1x2.gif":
            image_url = item.select_one(
                ".s-item__image-wrapper.image-treatment img")["data-src"].replace("s-l50", "s-l300")

        if title and price and link:
            title_text = title.get_text().lower()
            if any(word in title_text for word in exclude):
                continue

            try:
                price_str = price.get_text().replace("C $", "").replace("$", "").replace(",", "").strip()
                price = float(price_str.split(" ")[0])  # às vezes o preço vem com 'to'

                results.append({
                    "title": title.get_text(),
                    "price": price,
                    "url": link["href"],
                    "image_url": image_url
                })
            except Exception as exception:
                print(exception)
                continue

    return {
        "results": results,
        "count": results_count
    }


queries = [
    {
        "query": "pokemon yellow",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon red",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon leaf green",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon silver",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon gold",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon ruby",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon sapphire",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon emerald",
        "exclude": ["japan", "japanese", "no game", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon soul silver",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon heart gold",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon black",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon white",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon diamond",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon pearl",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
    {
        "query": "pokemon platinum",
        "exclude": ["japan", "japanese", "no game", "walker", "case & manual only", "case and manual only", "- manual only"]
    },
]

listings = {}

for query in queries:
    results = search_ebay(query['query'], query["exclude"], 1)
    if results["count"] > ITEMS_PER_PAGE:
        for page in range(2, math.ceil(results["count"] / ITEMS_PER_PAGE)):
            page_results = search_ebay(query['query'], query["exclude"], page)
            results["results"].extend(page_results["results"])
            time.sleep(random.uniform(2, 9))

    listings[query["query"]] = results["results"]
    time.sleep(random.uniform(2, 9))


listings_in_json = json.dumps(listings)

with io.open("./ebay-listing.json", "w+") as file:
    file.write(listings_in_json)
