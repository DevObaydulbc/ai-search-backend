from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Backend OK", "service": "AI Search BD", "version": "1.0"}

# ---------------------------
# 1. DuckDuckGo Lite Search
# ---------------------------
@app.get("/search")
def search_ddg(q: str):
    try:
        url = "https://lite.duckduckgo.com/lite/"
        payload = f"q={q}&kl=bd-bn"

        res = requests.post(url, data=payload, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0"
        }, timeout=10)

        soup = BeautifulSoup(res.text, "html.parser")
        anchors = soup.find_all("a", class_="result-link")

        results = [{
            "title": a.get_text(strip=True),
            "url": a.get("href"),
            "snippet": "Web result (DuckDuckGo Lite)",
            "source": "ddg-lite"
        } for a in anchors[:15]]

        return {"query": q, "results": results}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------
# 2. Bangla Wikipedia Search
# ---------------------------
@app.get("/wiki")
def wiki_search(q: str):
    try:
        wiki_url = f"https://bn.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&utf8=&format=json"

        res = requests.get(wiki_url, timeout=10)
        data = res.json()

        results = [{
            "title": item["title"],
            "url": f"https://bn.wikipedia.org/wiki/{item['title']}",
            "snippet": item["snippet"],
            "source": "wikipedia-bn"
        } for item in data["query"]["search"]]

        return {"query": q, "results": results}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------
# 3. BD Gov Website Scraper
# ---------------------------
@app.get("/gov")
def gov_scrape(url: str):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find("title").get_text(strip=True) if soup.find("title") else "No title"

        headings = [h.get_text(strip=True) for h in soup.find_all("h1")]
        officers = [t.get_text(strip=True) for t in soup.find_all("td")]

        return {
            "page_title": title,
            "h1": headings[:20],
            "td": officers[:50]
        }

    except Exception as e:
        return {"error": str(e)}
