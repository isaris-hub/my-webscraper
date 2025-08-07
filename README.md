# My Web Scraper

A simple CLI tool to fetch and display headlines from any webpage.

## Installation

```bash
git clone git@github.com:your-username/my-webscraper.git
cd my-webscraper
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Collecting subpages and titles

The scraper can crawl each provided URL, follow links to its subpages, and
record the `<title>` of every subpage. The collected data is written to
`results/subpages_<domein>.txt`, where `<domein>` is the host name of the
original URL. Each line of the file contains a subpage URL followed by its
title.

### CLI-voorbeeld

```bash
python src/webscraper.py --collect-subpages https://example.com
```

