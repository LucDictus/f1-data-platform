import json
import time
from pathlib import Path

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
RAW_DIR = Path("data/raw")


def fetch_page(session: requests.Session, path: str, limit: int = 100, offset: int = 0) -> dict:
    url = f"{BASE_URL}/{path}.json"
    for attempt in range(5):
        resp = session.get(url, params={"limit": limit, "offset": offset}, timeout=30)
        if resp.status_code == 429:
            time.sleep(2 ** attempt)  # exponential backoff
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Gave up on {url} after retries")


def fetch_all(session: requests.Session, path: str, limit: int = 100) -> list[dict]:
    pages, offset = [], 0
    while True:
        page = fetch_page(session, path, limit, offset)
        pages.append(page)
        total = int(page["MRData"]["total"])
        offset += limit
        if offset >= total:
            return pages
        time.sleep(0.5)  # be polite


def save_raw(season: int, endpoint: str, pages: list[dict]) -> Path:
    out = RAW_DIR / endpoint / f"season={season}" / "data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pages))
    return out


def get_rounds(session: requests.Session, season: int) -> list[int]:
    pages = fetch_all(session, f"{season}/races")
    races = [r for page in pages for r in page["MRData"]["RaceTable"]["Races"]]
    return [int(r["round"]) for r in races]


def save_raw_round(season: int, endpoint: str, round_: int, pages: list[dict]) -> Path:
    out = RAW_DIR / endpoint / f"season={season}" / f"round={round_:02d}" / "data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pages))
    return out


if __name__ == "__main__":
    season = 2024
    with requests.Session() as s:
        # Season-level endpoints
        pages = fetch_all(s, f"{season}/results")
        print(save_raw(season, "results", pages))

        # Round-level endpoints
        for round_ in get_rounds(s, season):
            pages = fetch_all(s, f"{season}/{round_}/pitstops")
            print(save_raw_round(season, "pitstops", round_, pages))
            time.sleep(0.5)