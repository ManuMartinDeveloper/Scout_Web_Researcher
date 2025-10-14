# file: crawler.py
import trafilatura
import requests

# We add a browser-like header to our request to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

def fetch_website_text(url: str) -> str:
    """
    Fetches and extracts the main text content from a single URL
    by making a request with browser-like headers.
    """
    print(f"Fetching content from: {url}")
    try:
        # We use requests to download with our header, then pass the content to trafilatura
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)
        
        # Now, we use trafilatura to extract the main content from the HTML we downloaded
        main_text = trafilatura.extract(response.text, include_comments=False, include_tables=False)
        
        if main_text is None:
            print(f"Failed to extract main text from {url}, but content was downloaded.")
            return ""
            
        return main_text
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to download content from {url}. Error: {e}")
        return ""

# You can test this file by running it directly
if __name__ == '__main__':
    test_url = "https://www.mongodb.com/who-we-are"
    text = fetch_website_text(test_url)
    if text:
        print("\n--- Extracted Text (First 500 Chars) ---")
        print(text[:500])