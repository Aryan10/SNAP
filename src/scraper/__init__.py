import json
from scraper.scraper import scrape_target
from scraper.config import TARGET_URLS_JSON

with open(TARGET_URLS_JSON, "r", encoding="utf-8") as f:
    targets = json.load(f)

for category, urls in targets.items():
    for url in urls:
        scrape_target(url, category)
