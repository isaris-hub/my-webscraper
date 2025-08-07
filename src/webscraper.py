import requests
from bs4 import BeautifulSoup
import argparse
from pathlib import Path
from urllib.parse import urlparse

def fetch_headlines(url: str, selector: str):
    """
    Fetches and returns a list of text headlines matching the CSS selector.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    elements = soup.select(selector)
    return [el.get_text(strip=True) for el in elements]


def save_headlines(url: str, selector: str, results_dir: Path):
    """Fetch headlines and save them to a domain-named file in results_dir."""
    headlines = fetch_headlines(url, selector)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    domain = urlparse(url).netloc
    file_path = results_dir / f"{domain}.txt"
    file_path.write_text("\n".join(headlines), encoding="utf-8")
    return file_path

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
