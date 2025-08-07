import pytest
from src.webscraper import fetch_headlines

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

def monkeypatch_get(url):
    return DummyResponse(HTML)

def test_fetch_headlines(monkeypatch):
    import requests
    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(HTML))
    headlines = fetch_headlines("http://example.com", "h2")
    assert headlines == ["First Headline", "Second Headline"]