# file: crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import trafilatura
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

def crawl_website(start_url: str, max_pages: int = 20) -> str:
    """
    Crawls a website starting from a URL, follows internal links,
    and returns the combined text content of all visited pages.
    """
    # 1. This is your "list for webpages to browse" (the queue).
    to_visit_queue = [start_url]
    
    # 2. This tracks webpages we have visited so we don't browse them again.
    # A 'set' is faster than a list for checking if an item exists.
    visited_urls = set()
    
    # 3. This is your "list that stores the data of the webpages browsed."
    all_text_data = []
    
    # Get the base domain to ensure we only crawl pages on the same site.
    base_domain = urlparse(start_url).netloc
    print(f"Starting crawl at {start_url} for domain {base_domain}")

    # 4. The main loop: keep browsing as long as there are pages in our queue.
    while to_visit_queue and len(visited_urls) < max_pages:
        # Get the next URL from the front of the queue.
        current_url = to_visit_queue.pop(0)

        # 5. Do not go through the visited webpage again.
        if current_url in visited_urls:
            continue
 
        try:
            print(f"Crawling: {current_url}")
            response = requests.get(current_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            # Mark the page as visited.
            visited_urls.add(current_url)

            # 6. Extract clean text and add it to our data list.
            page_text = trafilatura.extract(response.text, include_comments=False, include_tables=False)
            if page_text:
                all_text_data.append(page_text)

            # 7. Find all new links on the page.
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(start_url, href).split('#')[0] # Create absolute URL and remove fragments

                # 8. Add other webpages under the same domain to our "to visit" list.
                if (urlparse(full_url).netloc == base_domain and 
                        full_url not in visited_urls and 
                        full_url not in to_visit_queue):
                    to_visit_queue.append(full_url)
            
            # Be a good web citizen and wait a bit between requests.
            time.sleep(0.5)
        
        except requests.RequestException as e:
            print(f"Could not fetch {current_url}: {e}")
            continue

    print(f"Crawl finished. Visited {len(visited_urls)} pages and collected data.")
    # Combine all the collected text into one large corpus.
    return "\n\n".join(all_text_data), visited_urls