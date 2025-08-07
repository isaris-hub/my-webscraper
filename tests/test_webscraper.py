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
    def __init__(self, text="", content=b""):
        self.text = text
        self.content = content

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


def test_download_favicon(tmp_path, monkeypatch):
    import requests

    favicons_dir = tmp_path / "favicons"

    def fake_get(url):
        return DummyResponse(content=b"ICO")

    monkeypatch.setattr(requests, "get", fake_get)

    file_path = webscraper.download_favicon("http://example.com", favicons_dir)

    assert file_path.exists()
    assert file_path.read_bytes() == b"ICO"


def test_collect_subpages(monkeypatch):
    import requests

    MAIN_HTML = """
    <html><body>
      <a href="/a">A</a>
      <a href="http://other.com/b">B</a>
      <a href="/a">A again</a>
    </body></html>
    """

    SUB_HTML = """
    <html><head><title>Sub Title</title></head></html>
    """

    def fake_get(url):
        if url == "http://example.com":
            return DummyResponse(MAIN_HTML)
        if url == "http://example.com/a":
            return DummyResponse(SUB_HTML)
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr(requests, "get", fake_get)

    results = webscraper.collect_subpages("http://example.com")
    assert results == [("http://example.com/a", "Sub Title")]


def test_save_subpages(tmp_path, monkeypatch):
    import requests

    MAIN_HTML = """
    <html><body>
      <a href="/a">A</a>
      <a href="/b">B</a>
    </body></html>
    """
    SUB_HTML_A = "<html><head><title>Title A</title></head></html>"
    SUB_HTML_B = "<html><head><title>Title B</title></head></html>"

    def fake_get(url):
        if url == "http://example.com":
            return DummyResponse(MAIN_HTML)
        if url == "http://example.com/a":
            return DummyResponse(SUB_HTML_A)
        if url == "http://example.com/b":
            return DummyResponse(SUB_HTML_B)
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr(requests, "get", fake_get)

    results_dir = tmp_path / "results"
    file_path = webscraper.save_subpages("http://example.com", results_dir)

    output_file = results_dir / "subpages_example.com.txt"
    expected = (
        "http://example.com/a\tTitle A\n"
        "http://example.com/b\tTitle B"
    )
    assert file_path == output_file
    assert output_file.exists()
    assert output_file.read_text() == expected

    shutil.rmtree(results_dir)
    assert not results_dir.exists()


def test_main_scrapes_urls_from_file(tmp_path, monkeypatch):
    import requests
    from urllib.parse import urlparse

    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("http://example.com\nhttp://example.org\n", encoding="utf-8")
    results_dir = tmp_path / "results"
    favicons_dir = tmp_path / "favicons"

    def fake_get(url):
        if url.endswith("favicon.ico"):
            return DummyResponse(content=b"ICO")
        return DummyResponse(HTML)

    monkeypatch.setattr(requests, "get", fake_get)

    def fake_collect(url):
        domain = urlparse(url).netloc
        return [(f"http://{domain}/sub", "Sub Title")]

    monkeypatch.setattr(webscraper, "collect_subpages", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "webscraper",
            "--urls-file",
            str(urls_file),
            "--results-dir",
            str(results_dir),
            "--favicons-dir",
            str(favicons_dir),
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

    favicon1 = favicons_dir / "example.com.ico"
    favicon2 = favicons_dir / "example.org.ico"
    assert favicon1.exists()
    assert favicon2.exists()
    assert favicon1.read_bytes() == b"ICO"
    assert favicon2.read_bytes() == b"ICO"

    sub1 = results_dir / "subpages_example.com.txt"
    sub2 = results_dir / "subpages_example.org.txt"
    assert sub1.exists()
    assert sub2.exists()
    assert sub1.read_text() == "http://example.com/sub\tSub Title"
    assert sub2.read_text() == "http://example.org/sub\tSub Title"

    shutil.rmtree(results_dir)
    shutil.rmtree(favicons_dir)
    assert not results_dir.exists()
    assert not favicons_dir.exists()


def test_main_saves_results_without_favicon(tmp_path, monkeypatch):
    import requests
    from urllib.parse import urlparse

    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("http://example.com\n", encoding="utf-8")
    results_dir = tmp_path / "results"
    favicons_dir = tmp_path / "favicons"

    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(HTML))

    def fake_collect(url):
        domain = urlparse(url).netloc
        return [(f"http://{domain}/sub", "Sub Title")]

    monkeypatch.setattr(webscraper, "collect_subpages", fake_collect)

    def fake_download(url, fav_dir):
        raise Exception("favicon missing")

    monkeypatch.setattr(webscraper, "download_favicon", fake_download)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "webscraper",
            "--urls-file",
            str(urls_file),
            "--results-dir",
            str(results_dir),
            "--favicons-dir",
            str(favicons_dir),
        ],
    )

    webscraper.main()

    output_file = results_dir / "example.com.txt"
    subpages_file = results_dir / "subpages_example.com.txt"
    assert output_file.exists()
    assert subpages_file.exists()
    assert output_file.read_text() == "First Headline\nSecond Headline"
    assert subpages_file.read_text() == "http://example.com/sub\tSub Title"
    assert not (favicons_dir / "example.com.ico").exists()

    shutil.rmtree(results_dir)
    assert not results_dir.exists()
    if favicons_dir.exists():
        shutil.rmtree(favicons_dir)
        assert not favicons_dir.exists()

