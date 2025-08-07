import requests
from bs4 import BeautifulSoup
import argparse

def fetch_headlines(url: str, selector: str):
    """
    Fetches and returns a list of text headlines matching the CSS selector.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    elements = soup.select(selector)
    return [el.get_text(strip=True) for el in elements]

def main():
    parser = argparse.ArgumentParser(description="Simple headline scraper")
    parser.add_argument("url", help="Page URL to scrape")
    parser.add_argument(
        "--selector", 
        default="h2", 
        help="CSS selector for headlines (default: h2)"
    )
    args = parser.parse_args()

    try:
        headlines = fetch_headlines(args.url, args.selector)
        if not headlines:
            print("No headlines found with that selector.")
        else:
            print("\n".join(f"{i+1}. {hl}" for i, hl in enumerate(headlines)))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()