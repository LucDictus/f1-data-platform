import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
RAW_DIR = Path("data/raw")

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
CURRENT_SEASON = datetime.now().year


def fetch_page(session: requests.Session, path: str, limit: int = 100, offset: int = 0) -> dict:
    url = f"{BASE_URL}/{path}.json"
    for attempt in range(5):
        resp = session.get(url, params={"limit": limit, "offset": offset}, timeout=30)
        if resp.status_code in RETRYABLE_STATUS:
            time.sleep(2**attempt)  # exponential backoff
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
    # Idempotency: use a deterministic file path and overwrite existing data
    # instead of appending, so repeated ingestion does not create duplicates.
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


def raw_exists(season: int, endpoint: str, round_: int | None = None) -> bool:
    if round_ is None:
        path = RAW_DIR / endpoint / f"season={season}" / "data.json"
    else:
        path = RAW_DIR / endpoint / f"season={season}" / f"round={round_:02d}" / "data.json"
    return path.exists()


def parse_args():
    parser = argparse.ArgumentParser(description="F1 data ingestion pipeline")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--season",
        type=int,
        help=f"Load a single season ({2018}-{CURRENT_SEASON})",
    )

    group.add_argument(
        "--from",
        dest="start_season",
        type=int,
        help=f"First season to load ({2018}-{CURRENT_SEASON})",
    )

    parser.add_argument(
        "--to",
        dest="end_season",
        type=int,
        help=f"Last season to load ({2018}-{CURRENT_SEASON})",
    )

    args = parser.parse_args()

    if args.season is not None:
        if not 2018 <= args.season <= CURRENT_SEASON:
            parser.error(f"--season must be between 2018 and {CURRENT_SEASON}")
        return [args.season]

    if args.start_season is None or args.end_season is None:
        parser.error("--from and --to must be provided together")

    if not 2018 <= args.start_season <= CURRENT_SEASON:
        parser.error(f"--from must be between 2018 and {CURRENT_SEASON}")

    if not 2018 <= args.end_season <= CURRENT_SEASON:
        parser.error(f"--to must be between 2018 and {CURRENT_SEASON}")

    if args.start_season > args.end_season:
        parser.error("--from cannot be greater than --to")

    return list(range(args.start_season, args.end_season + 1))


if __name__ == "__main__":
    seasons = parse_args()

    with requests.Session() as s:
        for season in seasons:
            print(f"\nLoading season {season}...")

            # Season-level endpoints
            if raw_exists(season, "results") and season < CURRENT_SEASON:
                print(f"Skipping {season} results (already exists)")
            else:
                pages = fetch_all(s, f"{season}/results")
                print(save_raw(season, "results", pages))

            # Round-level endpoints
            for round_ in get_rounds(s, season):
                if raw_exists(season, "pitstops", round_):
                    print(f"Skipping {season} round {round_} pitstops (already exists)")
                    continue

                pages = fetch_all(s, f"{season}/{round_}/pitstops")
                print(save_raw_round(season, "pitstops", round_, pages))
                time.sleep(0.5)
