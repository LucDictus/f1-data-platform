# F1 Data Platform

A learning project that downloads Formula 1 data from the [Jolpica API](https://api.jolpi.ca/ergast/f1), stores the raw JSON, and transforms it with SQL in DuckDB.

## Installation

You only need **Git** and **Python 3.12 or newer**. Everything else is installed into a virtual environment inside the project folder.

### 1. Check the prerequisites

```bash
git --version
```

```bash
python3 --version
```

If either is missing on Ubuntu/Debian:

```bash
sudo apt install git python3 python3-venv
```

### 2. Clone the repo

```bash
git clone https://github.com/LucDictus/f1-data-platform.git
```

```bash
cd f1-data-platform
```

### 3. Create and activate a virtual environment

A virtual environment (`.venv/`) keeps this project's packages separate from the rest of your system.

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Your prompt now starts with `(.venv)`. **Run `source .venv/bin/activate` again every time you open a new terminal.**

### 4. Install the project

```bash
pip install -e ".[dev]"
```

This installs `requests`, `duckdb` and `dbt-duckdb` (needed to run the pipeline) and `pytest`, `ruff` and `responses` (needed for development). `-e` means "editable": your code changes take effect without reinstalling.

### 5. Check that it works

```bash
pytest
```

All tests should pass.

## Usage

Run every command from the repo root, because the scripts use paths relative to it.

**Download the raw data** for one season, or a range of seasons (2018 up to the current season):

```bash
python src/f1_pipeline/ingest/jolpica.py --season 2024
```

```bash
python src/f1_pipeline/ingest/jolpica.py --from 2018 --to 2025
```

This downloads race results, and per race the pit stops and lap times. The API allows 500 requests per hour, so the script waits 7.2 seconds before every request. Lap times are large (about 12 requests per race), so a first full download of all seasons takes about 5 hours. You can stop it at any time: the next run skips what is already on disk.

Past seasons that are already on disk are skipped. The current season is always downloaded again, because races are still being added.

The JSON files are written to `data/raw/`. Git ignores this folder.

**Transform the data with dbt.** The dbt project lives in `transform/` and builds into the DuckDB database `data/f1.duckdb`:

| Folder | Schema | What it holds |
|---|---|---|
| `transform/models/staging/` | `staging` | One view per raw source: flatten, cast and rename only. `_sources.yml` points to the raw JSON |
| `transform/models/marts/` | `marts` | Star schema: `dim_*` tables (one row per thing) and `fct_*` tables (one row per event). The grain is the first line of each file. `_marts.yml` holds the single-column tests |
| `transform/seeds/` | `main` | Small hand-written CSV tables, loaded by `dbt build`. `team_lineage.csv` maps every `constructor_id` to its team across renames (for example Toro Rosso, AlphaTauri and RB are all `racing_bulls`). Add a row when a new team appears; a test fails until you do |
| `transform/tests/` | none | Tests on several columns. Each one returns the bad rows, so 0 rows means it passes |
| `sql/analyses/` | none | Ad-hoc queries that read from the marts |

**Build and test** everything in one command. Run it after every new download, or after changing a model. dbt works out the order from the `ref()` and `source()` calls:

```bash
dbt build --project-dir transform --profiles-dir transform
```

Every line should say `OK` or `PASS`. A failing test stops the models that depend on it.

`fct_lap_times` is **incremental**: after the first build, dbt only adds races that are not in the table yet. When you change its SQL, rebuild it from scratch:

```bash
dbt build --project-dir transform --profiles-dir transform --full-refresh
```

**Run an analysis**, for example:

```bash
python scripts/run_sql.py sql/analyses/06_constructor_pitstops.sql
```

The database holds no data of its own, so you can delete it and rebuild it at any time. Do this after renaming or removing a model, so that stale views and tables can't hide mistakes:

```bash
rm data/f1.duckdb
```

```bash
dbt build --project-dir transform --profiles-dir transform
```

## Orchestration (Dagster)

Dagster runs the download and `dbt build` as one pipeline, in the right order. The pipeline is defined in `src/f1_pipeline/definitions.py`. Start the web interface from the repo root:

```bash
dagster dev -m f1_pipeline.definitions
```

Then open http://localhost:3000:

- **Assets → View lineage** shows the whole graph, from the raw JSON to the marts.
- **Materialize all** runs the pipeline now: pick one or more seasons, Dagster downloads them, then builds and tests every dbt model. Each season is a partition: **Assets → jolpica/results** shows which seasons are loaded, and a missing season can be backfilled from there.
- **Automation → `weekly_schedule`** refreshes the current season every Monday at 06:00 (Amsterdam time). Schedules start switched off, so turn it on here. It only runs while `dagster dev` is running.

Failed downloads are retried 3 times, 30 seconds apart. The dbt test `season_completeness_dim_race` fails if a season from 2018 to now has no races.

## Development

Run these before you push. CI runs the same checks on every pull request:

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
