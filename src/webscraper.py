import requests
from bs4 import BeautifulSoup
import argparse
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse, urljoin


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


def download_favicon(url: str, favicons_dir: Path):
    """Download the favicon for the given URL into favicons_dir."""
    favicons_dir = Path(favicons_dir)
    favicons_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    favicon_url = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    resp = requests.get(favicon_url)
    resp.raise_for_status()
    file_path = favicons_dir / f"{parsed.netloc}.ico"
    file_path.write_bytes(resp.content)
    return file_path


def collect_subpages(url: str) -> List[Tuple[str, str]]:
    """Return a list of tuples with subpage URLs and their titles."""
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    base_domain = urlparse(url).netloc
    visited = set()
    results: List[Tuple[str, str]] = []
    for tag in soup.find_all("a", href=True):
        link = urljoin(url, tag["href"])
        if urlparse(link).netloc != base_domain:
            continue
        if link in visited:
            continue
        visited.add(link)
        try:
            page = requests.get(link)
            page.raise_for_status()
            page_soup = BeautifulSoup(page.text, "html.parser")
            title_tag = page_soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""
            results.append((link, title))
        except Exception:
            continue
    return results


def save_subpages(url: str, results_dir: Path):
    """Save subpage URLs and titles for a domain into results_dir."""
    subpages = collect_subpages(url)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    domain = urlparse(url).netloc
    file_path = results_dir / f"subpages_{domain}.txt"
    lines = [f"{link}\t{title}" for link, title in subpages]
    file_path.write_text("\n".join(lines), encoding="utf-8")
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
DEFAULT_FAVICONS_DIR = BASE_DIR / "favicons"


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
    parser.add_argument(
        "--favicons-dir",
        default=DEFAULT_FAVICONS_DIR,
        type=Path,
        help="Directory to store favicons (default: favicons)",
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
            favicon_file = download_favicon(url, args.favicons_dir)
            print(f"Saved favicon from {url} to {favicon_file}")
            subpages_file = save_subpages(url, args.results_dir)
            print(f"Saved subpages from {url} to {subpages_file}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")


if __name__ == "__main__":
    main()

