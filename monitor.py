import requests
import io
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()

def search_ebay(keyword, exclude, price_max=210.0):
    headers = {'User-Agent': ua.random}
    query = keyword.replace(" ", "+")
    url = f"https://www.ebay.ca/sch/i.html?_nkw={query}&_sop=15&_pgn=1&_dcat=139973&Region%2520Code=%21%7CRegion%2520Free%7CNTSC%252DU%252FC%2520%2528US%252FCanada%2529%7CPAL&LH_BIN=1&_sop=15"  # Sort by Price + Shipping: Lowest First

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for item in soup.select(".s-item"):
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        link = item.select_one(".s-item__link")

        if title and price and link:
            for query_to_exclude in exclude:
                if query_to_exclude in title:
                    continue

            try:
                price_str = price.get_text().replace("C $", "").replace(",", "").strip()
                price = float(price_str.split(" ")[0])  # às vezes o preço vem com 'to'
                
                if price <= price_max:
                    results.append({
                        "title": title.get_text(),
                        "price": price,
                        "url": link["href"]
                    })
            except Exception as exception:
                print(exception)
                continue

    return results




queries = [
    {
        "query": "pokemon emerald",
        "price_max": 220,
        "exclude": ["japan", "japanese", "no game", "manual only"]
    },
    {
        "query": "pokemon soul silver",
        "price_max": 200,
        "exclude": ["japan", "japanese", "no game", "manual only", "walker"]
    },
    {
        "query": "pokemon heart gold",
        "price_max": 200,
        "exclude": ["japan", "japanese", "no game", "manual only", "walker"]
    }
]

listings = {}

for query in queries:
    results = search_ebay(query['query'], query["exclude"], query["price_max"])
    listings[query["query"]] = results


listings_in_json = json.dumps(listings)

with io.open("./docs/ebay-listing.json", "w+") as file:
    file.write(listings_in_json)
