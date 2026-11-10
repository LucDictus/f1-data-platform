import json
from datetime import date, timedelta
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


def test_parse_single_season(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jolpica.py", "--season", "2023"])

    assert jolpica.parse_args() == [2023]


def test_parse_season_range(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jolpica.py", "--from", "2018", "--to", "2024"])

    assert jolpica.parse_args() == list(range(2018, 2025))


def test_parse_single_year_range(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jolpica.py", "--from", "2020", "--to", "2020"])

    assert jolpica.parse_args() == [2020]


def test_parse_invalid_season(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jolpica.py", "--season", str(jolpica.CURRENT_SEASON + 1)])

    with pytest.raises(SystemExit):
        jolpica.parse_args()


def test_parse_invalid_range(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jolpica.py", "--from", "2024", "--to", "2018"])

    with pytest.raises(SystemExit):
        jolpica.parse_args()


def test_parse_missing_to(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jolpica.py", "--from", "2018"])

    with pytest.raises(SystemExit):
        jolpica.parse_args()


# --- saving and skipping ------------------------------------------------------


def test_save_raw_writes_file_without_leftover_tmp(monkeypatch, tmp_path):
    monkeypatch.setattr(jolpica, "RAW_DIR", tmp_path)

    out = jolpica.save_raw(2024, "laps", [make_page(1)], round_=3)

    assert out == tmp_path / "laps" / "season=2024" / "round=03" / "data.json"
    assert json.loads(out.read_text()) == [make_page(1)]
    assert list(out.parent.iterdir()) == [out]


def test_ingest_season_fetches_settled_rounds_only_once(monkeypatch, tmp_path):
    monkeypatch.setattr(jolpica, "RAW_DIR", tmp_path)
    old, recent = date.today() - timedelta(days=30), date.today() - timedelta(days=2)
    monkeypatch.setattr(jolpica, "get_rounds", lambda session, season: [(1, old), (2, recent)])
    fetched = []

    def fake_fetch_all(session, path):
        fetched.append(path)
        return [make_page(0)]

    monkeypatch.setattr(jolpica, "fetch_all", fake_fetch_all)
    season = jolpica.CURRENT_SEASON

    jolpica.ingest_season(None, season)
    fetched.clear()
    jolpica.ingest_season(None, season)

    # Round 1 is on disk and settled; round 2 is on disk but recent, so it is fetched again.
    assert fetched == [
        f"{season}/results",
        f"{season}/sprint",
        f"{season}/2/pitstops",
        f"{season}/2/laps",
    ]
