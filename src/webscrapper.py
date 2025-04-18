import os
import json
import time
import random
import requests
import urllib3
from collections import Counter
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse
from datetime import date

# === CONFIG ===
INPUT_HTML_FILE  = "newDoc.txt"
PROXIES_JSON     = "proxies.json"
WORKING_JSON     = "proxy.json"
TARGET_URLS = {
    #📰 National & International News (India‑focused + major global)
    "national_international_news": [
        "https://www.indiatoday.in/",
        "https://www.thehindu.com/",
        "https://www.thehindu.com/sci-tech/science/india-s-first-space-station-to-be-launched-in-2025/article3193852.ece",
        "https://news.abplive.com/",
        "https://www.thehindu.com/todays-paper/",
        "https://www.bbc.com/news",
        "https://edition.cnn.com/",
        "https://www.reuters.com/",
        "https://www.aljazeera.com/news/",
        "https://www.ndtv.com/",
        "https://www.hindustantimes.com/",
        "https://timesofindia.indiatimes.com/",
        "https://www.deccanherald.com/",
        "https://www.livemint.com/",
        "https://scroll.in/"
    ],

    # 🌐 News Aggregators & Readers
    "news_aggregators_readers": [
        "https://news.google.com",
        "https://www.newsnow.co.uk",
        "https://flipboard.com",
        "https://feedly.com",
        "https://www.inoreader.com"
    ],

    # 📰 Major International Outlets
    "major_international_outlets": [
        "https://www.bbc.com/news",
        "https://www.reuters.com",
        "https://www.aljazeera.com/news",
        "https://www.theguardian.com/international",
        "https://www.dw.com/en/top-stories/s-9097"
    ],

    # 🧠 Tech, Science & Innovation
    "tech_science_innovation": [
        "https://techcrunch.com/",
        "https://www.wired.com/",
        "https://thenextweb.com/",
        "https://www.theverge.com/",
        "https://www.sciencemag.org/",
        "https://www.nature.com/news",
        "https://www.space.com/news",
        "https://spectrum.ieee.org/",        # IEEE Spectrum
        "https://arstechnica.com/"          # Ars Technica
    ],

    # 📈 Business & Finance
    "business_finance": [
        "https://www.bloomberg.com/",
        "https://www.cnbc.com/world/",
        "https://www.moneycontrol.com/",
        "https://economictimes.indiatimes.com/",
        "https://www.business-standard.com/",
        "https://www.wsj.com/",             # Wall Street Journal
        "https://www.ft.com/"               # Financial Times
    ],

    # 📊 Data Portals & Analysis
    "data_portals_analysis": [
        "https://ourworldindata.org",
        "https://data.worldbank.org",
        "https://data.un.org",
        "https://www.gapminder.org",
        "https://www.worldometers.info",
        "https://www.cia.gov/the-world-factbook/",  # CIA World Factbook
    ],

    # 💬 Community & Social News
    "community_social_news": [
        "https://www.reddit.com/r/worldnews/",
        "https://news.ycombinator.com/",
        "https://www.allsides.com",
        "https://slate.com/",                       # Opinion & analysis
        "https://medium.com/topic/news"             # Medium news section
    ],

    # 📡 Regional News
    "regional_news": [
        "https://www.africanews.com/",              # Africa
        "https://www.france24.com/en/",             # Europe
        "https://www.laprensalatina.com/",          # Latin America (in English/Spanish)
        "https://www.asianews.network/",            # Asia-focused
        "https://www.australiannews.com.au/"        # Australia
    ],

    # 🌍 Travel, Culture & Lifestyle
    "travel_lifestyle_culture": [
        "https://www.lonelyplanet.com/news",
        "https://www.nationalgeographic.com/travel",
        "https://www.reddit.com/r/travel/",
        "https://www.reddit.com/r/AskIndia/",
        "https://www.reddit.com/r/IndianLifestyle/",
        "https://www.cntraveler.com/",              # Condé Nast Traveler
        "https://www.vogue.com/"                    # Vogue (culture & lifestyle)
    ],

    # ⚽ Sports
    "sports": [
        "https://www.espn.in/",
        "https://www.sportstar.thehindu.com/",
        "https://www.cricbuzz.com/",
        "https://www.reddit.com/r/sports/",
        "https://www.reddit.com/r/Cricket/",
        "https://www.skysports.com/",                # Sky Sports
        "https://www.foxsports.com/"                 # Fox Sports
    ],

    # 🔬 Health & Medicine
    "health_medicine": [
        "https://www.who.int/",
        "https://www.healthdata.org/",
        "https://www.nih.gov/news-events",           # NIH news
        "https://www.medicalnewstoday.com/",
        "https://www.webmd.com/"
    ],

    # 🏛️ Government & Policy
    "government_policy": [
        "https://www.un.org/en/news/",
        "https://www.oecd.org/newsroom/",
        "https://data.europa.eu/en",                 # EU open data
        "https://www.india.gov.in/news"              # India government news
    ],

    # 🎧 Podcasts & Multimedia
    "podcasts_multimedia": [
        "https://podcasts.apple.com/",
        "https://open.spotify.com/genre-podcasts-page",
        "https://www.npr.org/podcasts/",
        "https://www.bbc.co.uk/sounds/category/news"
    ],

    # 📉 Markets & Crypto
    "markets_crypto": [
        "https://www.coindesk.com/",
        "https://cointelegraph.com/",
        "https://www.investing.com/",
        "https://www.marketwatch.com/"
    ],

    # ✔️ Fact‑Checking & Verification
    "fact_checking": [
        "https://www.politifact.com/",
        "https://www.factcheck.org/",
        "https://fullfact.org/",
        "https://www.snopes.com/"
    ],

    # 🧵 Reddit‑specific Topics
    "reddit_topics": [
        "https://www.reddit.com/t/stories_and_confessions",
        "https://www.reddit.com/t/artificial_intelligence_and_machine_learning/",
        "https://www.reddit.com/t/tech_news_and_discussion/",
        "https://www.reddit.com/t/virtual_and_augmented_reality/",
        "https://www.reddit.com/t/tv_news_and_discussion/",
        "https://www.reddit.com/t/celebrities/",
        "https://www.reddit.com/t/creators_and_influencers/",
        "https://www.reddit.com/t/business/",
        "https://www.reddit.com/t/humanities_and_law/",
        "https://www.reddit.com/t/news_and_politics/",
        "https://www.reddit.com/t/places_and_travel/",
        "https://www.reddit.com/t/sports/",
        "https://www.reddit.com/t/science/",
        "https://www.reddit.com/t/vehicles/",
        "https://www.reddit.com/r/technology/",
        "https://www.reddit.com/r/Futurology/",
        "https://www.reddit.com/r/science/",
        "https://www.reddit.com/r/movies/",
        "https://www.reddit.com/r/television/",
        "https://www.reddit.com/r/India/"
    ]
}

BASE_SCRAPE_DIR  = "scrapped"
CONNECT_TEST_URL = "https://httpbin.org/ip"  # endpoint to test CONNECT

# suppress InsecureRequestWarning for verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
ua = UserAgent()

# --- STEP 1: Parse raw HTML table into proxies.json ---
def parse_proxies_to_json():
    with open(INPUT_HTML_FILE, "r", encoding="utf-8") as f:
        html = "<table>" + f.read() + "</table>"
    soup = BeautifulSoup(html, "html.parser")

    proxies = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 8:
            continue
        proxies.append({
            "ip":           tds[0].get_text(strip=True),
            "port":         tds[1].get_text(strip=True),
            "country_code": tds[2].get_text(strip=True),
            "country":      tds[3].get_text(strip=True),
            "anonymity":    tds[4].get_text(strip=True),
            "google":       tds[5].get_text(strip=True),
            "https":        tds[6].get_text(strip=True).lower(),
            "last_checked": tds[7].get_text(strip=True),
        })
    with open(PROXIES_JSON, "w", encoding="utf-8") as f:
        json.dump(proxies, f, indent=2)
    print(f"Parsed {len(proxies)} proxies -> {PROXIES_JSON}")

# --- STEP 2: Load proxies.json, filter HTTPS-capable ---
def load_https_proxies():
    with open(PROXIES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    https_caps = [p for p in data if p["https"] == "yes"]
    print(f"Total proxies: {len(data)}")
    print(f"Claim HTTPS support: {len(https_caps)}")
    return https_caps

# --- STEP 3: Test proxy via CONNECT to httpbin.org/ip ---
def test_connect(proxy_url):
    try:
        resp = session.get(
            CONNECT_TEST_URL,
            proxies={"https": proxy_url},
            timeout=5,
            verify=False
        )
        return resp.status_code == 200
    except:
        return False

# --- STEP 4: Build working_proxies.json & working_urls list ---
def build_working_proxies(https_caps):
    working = []
    print("Testing HTTPS-capable proxies with CONNECT…")
    for p in https_caps:
        url = f"http://{p['ip']}:{p['port']}"
        if test_connect(url):
            working.append(p)
    print(f"Verified working HTTPS proxies: {len(working)}")
    with open(WORKING_JSON, "w", encoding="utf-8") as f:
        json.dump(working, f, indent=2)
    return [f"http://{p['ip']}:{p['port']}" for p in working]

# --- STEP 5: Fetch direct and via first proxy for a target ---
def fetch_and_save_direct_and_via_proxy(target_url, working_urls, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    # direct fetch
    direct_html = session.get(
        target_url,
        headers={"User-Agent": ua.random},
        timeout=10,
        verify=False
    ).text
    with open(os.path.join(output_folder, "direct.html"), "w", encoding="utf-8") as f:
        f.write(direct_html)
    print("  Saved direct fetch -> direct.html")

    # via first working proxy
    if working_urls:
        proxy = working_urls[0]
        try:
            via_html = session.get(
                target_url,
                headers={"User-Agent": ua.random, "Host": urlparse(target_url).netloc},
                proxies={"https": proxy},
                timeout=10,
                verify=False
            ).text
            with open(os.path.join(output_folder, "via_proxy.html"), "w", encoding="utf-8") as f:
                f.write(via_html)
            print("  Saved via-proxy fetch -> via_proxy.html")
        except Exception as e:
            print("  Via-proxy fetch failed:", type(e).__name__)

# --- STEP 6: Final rotate scrape for a target ---
def final_rotate_scrape(target_url, working_urls, output_folder):
    def get_proxy():
        url = random.choice(working_urls)
        return {"http": url, "https": url}

    html = None
    for attempt in range(1, 6):
        proxy = get_proxy()
        print(f"  [{attempt}] Proxy {proxy['https']}", end=" ")
        try:
            r = session.get(
                target_url,
                headers={"User-Agent": ua.random, "Host": urlparse(target_url).netloc},
                proxies=proxy,
                timeout=10,
                verify=False
            )
            if r.status_code == 200:
                print("200 OK")
                html = r.text
                break
            else:
                print(f"HTTP {r.status_code}")
        except Exception as e:
            print(type(e).__name__)
        time.sleep(1)

    if html:
        with open(os.path.join(output_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("  Saved final scrape -> index.html")

        soup = BeautifulSoup(html, "html.parser")
        titles = [t.get_text() for t in soup.find_all("title")]
        with open(os.path.join(output_folder, "titles.html"), "w", encoding="utf-8") as f:
            f.write("<html><body><h1>Titles Found</h1><ul>\n")
            if titles:
                for t in titles:
                    f.write(f"<li>{t}</li>\n")
            else:
                f.write("<li><em>No <code>&lt;title&gt;</code> tags found</em></li>\n")
            f.write("</ul></body></html>")
        print("  Saved titles summary -> titles.html")
    else:
        print("  Final scrape failed after retries.")

# === MAIN ===
if __name__ == "__main__":
    # Parse and build proxy lists (only run once or when input changes)
    # parse_proxies_to_json()
    # https_caps = load_https_proxies()
    # working_urls = build_working_proxies(https_caps)
    with open(WORKING_JSON, "r", encoding="utf-8") as f:
        working_urls = json.load(f)
    working_urls = [f"http://{p['ip']}:{p['port']}" for p in working_urls]
    # Date-based folder
    today_str = date.today().isoformat()  # e.g. "2025-04-17"
    date_folder = os.path.join(BASE_SCRAPE_DIR, today_str)
    os.makedirs(date_folder, exist_ok=True)

    # Quick stats
    # with open(WORKING_JSON, "r", encoding="utf-8") as f:
    #     working_meta = json.load(f)
    # top5 = Counter(p["country"] for p in working_meta).most_common(5)
    # print("Top 5 countries (working proxies):", top5)

    # Process each target URL
for category, urls in TARGET_URLS.items():
    for target in urls:
        host = urlparse(target).netloc.replace(":", "_")
        target_folder = os.path.join(date_folder, category, host)
        print(f"\nProcessing {target} -> folder {target_folder}")
        fetch_and_save_direct_and_via_proxy(target, working_urls, target_folder)
        final_rotate_scrape(target, working_urls, target_folder)

print("\nAll done. Check the folders under:", date_folder)
