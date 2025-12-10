from fastapi import FastAPI, Query
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Backend OK", "service": "AI Search BD", "version": "1.0"}

# ---------------------------
# 1) Wikipedia Search (Bangla + English)
# ---------------------------
@app.get("/wiki")
def wiki_search(q: str, lang: str = "bn"):
    try:
        wiki_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&utf8=&format=json"
        res = requests.get(wiki_url, timeout=10)
        data = res.json()
        results = []
        for item in data.get("query", {}).get("search", []):
            results.append({
                "title": item["title"],
                "url": f"https://{lang}.wikipedia.org/wiki/{item['title']}",
                "snippet": item["snippet"].replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                "source": f"wikipedia-{lang}"
            })
        return {"query": q, "results": results}
    except Exception as e:
        return {"error": str(e)}

# ---------------------------
# 2) BD GOV Scraper
# ---------------------------
@app.get("/gov")
def gov_scrape(url: str):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
        headings = [h.get_text(strip=True) for h in soup.find_all("h1")]
        officers = [t.get_text(strip=True) for t in soup.find_all("td")]
        return {"page_title": title, "h1": headings, "td": officers[:50]}
    except Exception as e:
        return {"error": str(e)}

# ---------------------------
# 3) News (Example using Google News RSS)
# ---------------------------
@app.get("/news")
def news_search(q: str):
    try:
        rss_url = f"https://news.google.com/rss/search?q={q}+site:bd"
        res = requests.get(rss_url, timeout=10)
        soup = BeautifulSoup(res.text, "xml")
        items = soup.find_all("item")[:15]
        results = []
        for i in items:
            results.append({
                "title": i.title.text,
                "url": i.link.text,
                "snippet": i.description.text if i.description else "",
                "source": "google-news"
            })
        return {"query": q, "results": results}
    except Exception as e:
        return {"error": str(e)}
