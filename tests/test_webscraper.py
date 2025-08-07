import shutil
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.webscraper import fetch_headlines, save_headlines

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
    headlines = fetch_headlines("http://example.com", "h2")
    assert headlines == ["First Headline", "Second Headline"]


def test_save_headlines(tmp_path, monkeypatch):
    import requests

    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(HTML))
    results_dir = tmp_path / "results"
    save_headlines("http://example.com", "h2", results_dir)

    output_file = results_dir / "example.com.txt"
    assert output_file.exists()
    assert output_file.read_text() == "First Headline\nSecond Headline"

    shutil.rmtree(results_dir)
    assert not results_dir.exists()

