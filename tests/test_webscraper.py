import shutil
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import src.webscraper as webscraper

HTML = """
<html><body>
  <h2>First Headline</h2>
  <h2>Second Headline</h2>
</body></html>
"""


class DummyResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_fetch_headlines(monkeypatch):
    import requests

    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(HTML))
    headlines = webscraper.fetch_headlines("http://example.com", "h2")
    assert headlines == ["First Headline", "Second Headline"]


def test_save_headlines(tmp_path, monkeypatch):
    import requests

    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(HTML))
    results_dir = tmp_path / "results"
    webscraper.save_headlines("http://example.com", "h2", results_dir)

    output_file = results_dir / "example.com.txt"
    assert output_file.exists()
    assert output_file.read_text() == "First Headline\nSecond Headline"

    shutil.rmtree(results_dir)
    assert not results_dir.exists()


def test_main_scrapes_urls_from_file(tmp_path, monkeypatch):
    import requests

    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("http://example.com\nhttp://example.org\n", encoding="utf-8")
    results_dir = tmp_path / "results"

    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(HTML))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "webscraper",
            "--urls-file",
            str(urls_file),
            "--results-dir",
            str(results_dir),
        ],
    )

    webscraper.main()

    output_file1 = results_dir / "example.com.txt"
    output_file2 = results_dir / "example.org.txt"
    assert output_file1.exists()
    assert output_file2.exists()
    expected = "First Headline\nSecond Headline"
    assert output_file1.read_text() == expected
    assert output_file2.read_text() == expected

    shutil.rmtree(results_dir)
    assert not results_dir.exists()

