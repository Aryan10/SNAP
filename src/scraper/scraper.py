import os
from urllib.parse import urlparse
from .config import DATE_FOLDER
from .proxies import load_working_proxies
from .fetcher import fetch_and_save_direct_and_via_proxy, final_rotate_scrape

working_urls = load_working_proxies()

def scrape_target(target_url, category="default"):
    host = urlparse(target_url).netloc.replace(":", "_")
    target_folder = os.path.join(DATE_FOLDER, category, host)
    print(f"\nScraping {target_url} -> {target_folder}")
    fetch_and_save_direct_and_via_proxy(target_url, working_urls, target_folder)
    final_rotate_scrape(target_url, working_urls, target_folder)
