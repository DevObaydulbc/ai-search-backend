from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="AI Search BD", version="1.0")

# ---------------------------
# 0) Health Check
# ---------------------------
@app.get("/")
def root():
    return {"status": "Backend OK", "service": "AI Search BD", "version": "1.0"}

# ---------------------------
# 1) DuckDuckGo Lite Search
# ---------------------------
@app.get("/search/ddg")
def search_ddg(q: str = Query(..., description="Search query")):
    url = "https://lite.duckduckgo.com/lite/"
    payload = f"q={q}&kl=bd-bn"

    try:
        res = requests.post(url, data=payload, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0"
        }, timeout=10)
        res.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    soup = BeautifulSoup(res.text, "html.parser")
    anchors = soup.find_all("a", class_="result-link")

    results = []
    for a in anchors[:15]:
        results.append({
            "title": a.get_text(strip=True),
            "url": a.get("href"),
            "snippet": "Web result (DuckDuckGo Lite)",
            "source": "ddg-lite"
        })

    return {"query": q, "results": results}

# ---------------------------
# 2) Wikipedia Search (BN + EN)
# ---------------------------
@app.get("/search/wiki")
def wiki_search(q: str = Query(...), lang: str = Query("bn")):
    wiki_url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": q,
        "utf8": "",
        "format": "json",
        "origin": "*"
    }
    try:
        res = requests.get(wiki_url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    results = []
    for item in data.get("query", {}).get("search", []):
        results.append({
            "title": item["title"],
            "url": f"https://{lang}.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
            "snippet": BeautifulSoup(item["snippet"], "html.parser").get_text(),
            "source": f"wikipedia-{lang}"
        })

    return {"query": q, "results": results}

# ---------------------------
# 3) GOV Scraper Example
# ---------------------------
@app.get("/search/gov")
def gov_scrape(url: str = Query(...)):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
    headings = [h.get_text(strip=True) for h in soup.find_all("h1")]
    # Officer list parsing example (page specific)
    officers = [t.get_text(strip=True) for t in soup.find_all("td")][:50]

    return {"page_title": title, "h1": headings, "td": officers}
