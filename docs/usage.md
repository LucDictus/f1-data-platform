# Usage

Day-to-day commands, once the platform is set up (see [setup.md](setup.md)). Run every command from the repo root, with the virtual environment active.

## Downloading data

Download one season, or a range of seasons (2018 up to the current season):

```bash
python src/f1_pipeline/ingest/jolpica.py --season 2024
```

```bash
python src/f1_pipeline/ingest/jolpica.py --from 2018 --to 2025
```

This downloads race results, and per race the pit stops and lap times. The JSON files are written to `data/raw/`, which Git ignores.

- **Rate limit:** the API allows 500 requests per hour, so the script waits 7.2 seconds before every request. Lap times are large (about 12 requests per race), so a first full download of all seasons takes about 5 hours.
- **Skipping:** past seasons that are already on disk are skipped. The current season is always downloaded again, because races are still being added.
- **Stopping:** you can stop the script at any time. A race is only written once all its pages are in, so the next run continues where it stopped.

## Transforming with dbt

The dbt project lives in `transform/`. Staging is written as Parquet files to the `f1-lake` bucket, and the marts are built into the DuckDB database `data/f1.duckdb`:

| Folder | Schema | What it holds |
|---|---|---|
| `transform/models/staging/` | `staging` | One Parquet file per raw source, at `s3://f1-lake/staging/<model>.parquet`: flatten, cast and rename only. `_sources.yml` points to the raw JSON. DuckDB has a view on each file, so `ref()` works as usual |
| `transform/models/marts/` | `marts` | Star schema: `dim_*` tables (one row per thing) and `fct_*` tables (one row per event). The grain is the first line of each file. `_marts.yml` holds the single-column tests |
| `transform/seeds/` | `main` | Small hand-written CSV tables, loaded by `dbt build`. `team_lineage.csv` maps every `constructor_id` to its team across renames (for example Toro Rosso, AlphaTauri and RB are all `racing_bulls`). Add a row when a new team appears; a test fails until you do |
| `transform/tests/` | none | Tests on several columns. Each one returns the bad rows, so 0 rows means it passes |
| `sql/analyses/` | none | Ad-hoc queries that read from the marts |

dbt needs the storage keys from `.env`, and the storage must be running (`docker compose up -d`). Load the keys into your terminal; do this again in every new terminal:

```bash
set -a && source .env && set +a
```

**Build and test** everything in one command. Run it after every new download, or after changing a model. dbt works out the order from the `ref()` and `source()` calls:

```bash
dbt build --project-dir transform --profiles-dir transform
```

Every line should say `OK` or `PASS`. A failing test stops the models that depend on it.

`fct_lap_times` is **incremental**: after the first build, dbt only adds races that are not in the table yet. When you change its SQL, rebuild it from scratch:

```bash
dbt build --project-dir transform --profiles-dir transform --full-refresh
```

The database and the Parquet files hold no data of their own, so you can delete them and rebuild them at any time. Do this after renaming or removing a model, so that stale views and tables can't hide mistakes:

```bash
rm data/f1.duckdb
```

```bash
dbt build --project-dir transform --profiles-dir transform
```

**Run an analysis**, for example:

```bash
python scripts/run_sql.py sql/analyses/06_constructor_pitstops.sql
```

## Orchestration (Dagster)

Dagster runs the download and `dbt build` as one pipeline, in the right order. The pipeline is defined in `src/f1_pipeline/definitions.py`.

It runs in the `dagster` container, which `docker compose up -d --build` starts. The container gets the keys from `.env`, and reaches the storage at `s3:9000`: inside Docker, containers find each other by service name, not via `localhost`. It reads and writes your local `data/` folder, so raw data, the database and Dagster's run history (`data/dagster_home/`) stay on your laptop. Follow its log with:

```bash
docker compose logs -f dagster
```

To run Dagster outside Docker instead (for example while changing `definitions.py`), stop the container first, because both use port 3000:

```bash
docker compose stop dagster
```

```bash
dagster dev -m f1_pipeline.definitions
```

Open http://localhost:3000:

- **Assets → View lineage** shows the whole graph, from the raw JSON to the marts.
- **Materialize all** runs the pipeline now: pick one or more seasons, Dagster downloads them, then builds and tests every dbt model. Each season is a partition: **Assets → jolpica/results** shows which seasons are loaded, and a missing season can be backfilled from there.
- **Automation → `weekly_schedule`** refreshes the current season every Monday at 06:00 (Amsterdam time). Schedules start switched off, so turn it on here. It only runs while Dagster is running.

To rebuild only the dbt models, without downloading, select the `staging/` and `marts/` assets and click **Materialize selected**. Never start a download in Dagster while the download script is running in a terminal: together they exceed the API limit of 500 requests per hour.

Failed downloads are retried 3 times, 30 seconds apart. The dbt test `season_completeness_dim_race` fails if a season from 2018 to now has no races.

## Dashboard

`dashboard/app.py` is a [Streamlit](https://streamlit.io) app that reads the marts from `data/f1.duckdb`. It shows:

- points per team per season, using `team_lineage`, so renamed teams stay one line
- the average pit stop per team, for the season you pick. Stops over 60 seconds (`is_long_stop` in `fct_pit_stops`: cars waiting in the pit lane during a red flag) are left out
- lap times per driver in one race. Laps slower than 1.2 × the race median (safety car, red flag) are left out, so the chart doesn't flatten

The `dashboard` container serves it on http://localhost:8501. To run it outside Docker instead (for example while changing `app.py`), stop the container first, because both use port 8501:

```bash
docker compose stop dashboard
```

```bash
streamlit run dashboard/app.py
```

The dashboard opens the database for each query and closes it straight away. DuckDB allows only one process to write to a database file, and while any connection is open, even a read-only one, `dbt build` fails with `Could not set lock on file`. Query results are cached for 10 minutes, so after a new `dbt build` the charts can take up to 10 minutes to update.

## Development

Run these before you push:

```bash
ruff check .
```

```bash
ruff format --check .
```

```bash
pytest
```

Run `ruff format .` to fix formatting automatically.

CI (`.github/workflows/ci.yml`) runs the same checks on every pull request, plus `dbt build` on a small set of real data in `tests/fixtures/data/` (one season of results, one race of pit stops and lap times). CI has no S3 storage, so it uses the `ci` target in `transform/profiles.yml`, which writes the Parquet files to a local folder. To run that step locally:

```bash
mkdir -p tests/fixtures/data/lake
```

```bash
F1_DATA_DIR=tests/fixtures/data dbt build --project-dir transform --profiles-dir transform --target ci --exclude season_completeness_dim_race
```

The completeness test is left out because the fixture data holds one season, not all of them.
