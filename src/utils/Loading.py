import os
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_community.document_loaders import WebBaseLoader


BASE_URL = "https://www.gainwelltechnologies.com/solutions/medicaid-enterprise/"
OUTPUT_FILE = "data/raw/gainwell_text.json"
MAX_PAGES = 150
DELAY = 1.5  


def is_valid_url(url):
    """Check if URL is internal to Gainwell site."""
    parsed = urlparse(url)
    return "gainwelltechnologies.com" in parsed.netloc and parsed.scheme in ["http", "https"]


def extract_links(url):
    """Return all internal links from a page."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [
            urljoin(url, a["href"])
            for a in soup.find_all("a", href=True)
        ]
        return [l for l in links if is_valid_url(l)]
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def crawl_and_load(base_url, max_pages=150, delay=1.5, output_file=None):
    """Recursively crawl and load pages using LangChain’s WebBaseLoader."""
    visited = set()
    to_visit = [base_url]
    all_docs = []

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        print(f"Crawling ({len(visited)+1}/{max_pages}): {url}")
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            all_docs.extend(docs)
            visited.add(url)

            # extract links for deeper crawl
            for link in extract_links(url):
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

        except Exception as e:
            print(f" Error on {url}: {e}")

        time.sleep(delay)

    # Save everything as a JSON file
    data = [{"url": d.metadata.get("source", ""), "text": d.page_content} for d in all_docs]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n Done! Scraped {len(visited)} pages and saved to {output_file}")


if __name__ == "__main__":
    crawl_and_load(BASE_URL, MAX_PAGES, DELAY, OUTPUT_FILE)
