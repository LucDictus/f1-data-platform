from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses

from f1_pipeline.ingest import jolpica

URL = f"{jolpica.BASE_URL}/2024/results.json"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Skip real waiting so the retry tests run instantly."""
    monkeypatch.setattr(jolpica.time, "sleep", lambda _: None)


def make_page(total: int) -> dict:
    return {"MRData": {"total": str(total)}}


def offsets_requested() -> list[int]:
    return [
        int(parse_qs(urlparse(call.request.url).query)["offset"][0]) for call in responses.calls
    ]


# --- fetch_page ---------------------------------------------------------------


@responses.activate
def test_fetch_page_returns_parsed_json():
    responses.add(responses.GET, URL, json=make_page(1))

    with requests.Session() as s:
        assert jolpica.fetch_page(s, "2024/results") == make_page(1)


@responses.activate
@pytest.mark.parametrize("status", sorted(jolpica.RETRYABLE_STATUS))
def test_fetch_page_retries_then_succeeds(status):
    responses.add(responses.GET, URL, status=status)
    responses.add(responses.GET, URL, json=make_page(1))

    with requests.Session() as s:
        result = jolpica.fetch_page(s, "2024/results")

    assert result == make_page(1)
    assert len(responses.calls) == 2


@responses.activate
def test_fetch_page_gives_up_after_five_attempts():
    responses.add(responses.GET, URL, status=429)

    with requests.Session() as s, pytest.raises(RuntimeError):
        jolpica.fetch_page(s, "2024/results")

    assert len(responses.calls) == 5


@responses.activate
def test_fetch_page_does_not_retry_on_400():
    responses.add(responses.GET, URL, status=400)

    with requests.Session() as s, pytest.raises(requests.HTTPError):
        jolpica.fetch_page(s, "2024/results")

    assert len(responses.calls) == 1


# --- fetch_all ----------------------------------------------------------------


@responses.activate
def test_fetch_all_single_page():
    responses.add(responses.GET, URL, json=make_page(50))

    with requests.Session() as s:
        pages = jolpica.fetch_all(s, "2024/results", limit=100)

    assert len(pages) == 1


@responses.activate
def test_fetch_all_follows_pagination():
    for _ in range(3):
        responses.add(responses.GET, URL, json=make_page(250))

    with requests.Session() as s:
        pages = jolpica.fetch_all(s, "2024/results", limit=100)

    assert len(pages) == 3
    assert offsets_requested() == [0, 100, 200]


@responses.activate
def test_fetch_all_exact_multiple_does_not_fetch_extra_page():
    for _ in range(2):
        responses.add(responses.GET, URL, json=make_page(200))

    with requests.Session() as s:
        pages = jolpica.fetch_all(s, "2024/results", limit=100)

    assert len(pages) == 2
