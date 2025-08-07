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
    soup = BeautifulSoup(resp.text, "html.parser")
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


def read_urls(file_path: Path):
    """Return a list of URLs read from a text file, ignoring blank lines."""
    file_path = Path(file_path)
    return [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_URLS_FILE = BASE_DIR / "input" / "urls.txt"
DEFAULT_RESULTS_DIR = BASE_DIR / "results"


def main():
    parser = argparse.ArgumentParser(description="Simple headline scraper")
    parser.add_argument(
        "--selector",
        default="h2",
        help="CSS selector for headlines (default: h2)",
    )
    parser.add_argument(
        "--urls-file",
        default=DEFAULT_URLS_FILE,
        type=Path,
        help="Path to a file containing URLs to scrape (default: input/urls.txt)",
    )
    parser.add_argument(
        "--results-dir",
        default=DEFAULT_RESULTS_DIR,
        type=Path,
        help="Directory to store results (default: results)",
    )
    args = parser.parse_args()

    try:
        urls = read_urls(args.urls_file)
    except Exception as e:
        print(f"Error reading URLs file: {e}")
        return

    for url in urls:
        try:
            output_file = save_headlines(url, args.selector, args.results_dir)
            print(f"Saved headlines from {url} to {output_file}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")


if __name__ == "__main__":
    main()

