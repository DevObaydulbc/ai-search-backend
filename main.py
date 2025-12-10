from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Backend OK", "service": "AI Search BD", "version": "1.0"}

# ---------------------------
# Wikipedia Search (bn + en)
# ---------------------------
@app.get("/search/wiki")
def wiki_search(q: str, lang: str = "bn"):
    wiki_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&utf8=&format=json"

    res = requests.get(wiki_url)
    data = res.json()

    results = []
    for item in data.get("query", {}).get("search", []):
        results.append({
            "title": item["title"],
            "url": f"https://{lang}.wikipedia.org/wiki/{item['title']}",
            "snippet": item["snippet"],
            "source": f"wikipedia-{lang}"
        })
    return {"query": q, "results": results}


# ---------------------------
# BD GOV Scraper
# ---------------------------
@app.get("/search/gov")
def gov_scrape(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
    headings = [h.get_text(strip=True) for h in soup.find_all("h1")]
    officers = [t.get_text(strip=True) for t in soup.find_all("td")]

    return {
        "page_title": title,
        "h1": headings,
        "td": officers[:50]  # limit
    }


# ---------------------------
# News RSS Search
# ---------------------------
@app.get("/search/news")
def news_search(q: str):
    rss_feeds = [
        "https://www.prothomalo.com/rss",
        "https://bdnews24.com/rss"
    ]
    results = []

    for feed in rss_feeds:
        res = requests.get(feed)
        soup = BeautifulSoup(res.text, "xml")
        items = soup.find_all("item")
        for item in items:
            if q.lower() in item.title.text.lower():
                results.append({
                    "title": item.title.text,
                    "url": item.link.text,
                    "source": feed,
                    "snippet": item.description.text if item.description else ""
                })
    return {"query": q, "results": results[:20]}
