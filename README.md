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

This installs `requests` and `duckdb` (needed to run the pipeline) and `pytest`, `ruff` and `responses` (needed for development). `-e` means "editable": your code changes take effect without reinstalling.

### 5. Check that it works

```bash
pytest
```

All tests should pass.

## Usage

Run every command from the repo root, because the scripts use paths relative to it.

**Download the raw data** (the 2024 season, takes about a minute):

```bash
python src/f1_pipeline/ingest/jolpica.py
```

The JSON files are written to `data/raw/`. Git ignores this folder.

**Run SQL files** against the DuckDB database `data/f1.duckdb`. The files run in the order you pass them, and the result of the last one is printed:

```bash
python scripts/run_sql.py sql/01_results_flat.sql sql/03_running_points.sql
```

Because the database is saved to a file, a view created in one run is still there in the next one.

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
