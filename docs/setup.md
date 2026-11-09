# Setup

This guide takes you from a clean machine to a running platform with data in the dashboard. For day-to-day commands, see [usage.md](usage.md).

## 1. Check the prerequisites

You need **Git**, **Python 3.12 or newer** and **Docker** (with Docker Compose). Everything else is installed into a virtual environment inside the project folder, or runs in a container.

```bash
git --version
```

```bash
python3 --version
```

```bash
docker compose version
```

If Git or Python is missing on Ubuntu/Debian:

```bash
sudo apt install git python3 python3-venv
```

For Docker, follow the [official install guide](https://docs.docker.com/engine/install/).

## 2. Clone the repo

```bash
git clone https://github.com/LucDictus/f1-data-platform.git
```

```bash
cd f1-data-platform
```

Run every command in these docs from the repo root, because the scripts use paths relative to it.

## 3. Create and activate a virtual environment

A virtual environment (`.venv/`) keeps this project's packages separate from the rest of your system.

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Your prompt now starts with `(.venv)`. **Run `source .venv/bin/activate` again every time you open a new terminal.**

## 4. Install the project

```bash
pip install -e ".[dev]"
```

This installs the pipeline packages (`requests`, `duckdb`, `dbt-duckdb`, `dagster`, `dagster-dbt` and `streamlit`) and the development tools (`pytest`, `ruff`, `responses` and `dagster-webserver`). `-e` means "editable": your code changes take effect without reinstalling.

## 5. Start the containers

The staging models are written as Parquet files to an S3 bucket. Locally that bucket lives in [RustFS](https://rustfs.com), an S3-compatible server that runs in Docker. It works the same way as AWS S3, so in the cloud only the address and the keys would change.

Create your own settings file from the example. Git ignores `.env`, so your keys never end up on GitHub:

```bash
cp .env.example .env
```

Open `.env` and fill in both values: a username and a password you make up. They are only used on your own machine. Then build and start everything:

```bash
docker compose up -d --build
```

This starts four containers. Their ports are bound to `127.0.0.1`, so only your own machine can reach them, not others on the same network:

| Container | What it does |
|---|---|
| `s3` | The storage server, on port 9000. Its data is kept in a Docker volume, so it survives a restart |
| `createbucket` | Creates the bucket `f1-lake`, then stops |
| `dagster` | The pipeline and its web interface, on http://localhost:3000. See [Orchestration](usage.md#orchestration-dagster) |
| `dashboard` | The Streamlit dashboard, on http://localhost:8501. See [Dashboard](usage.md#dashboard) |

`dagster` and `dashboard` use the same image, built from the `Dockerfile`, but each runs a different command. `--build` rebuilds that image, so your latest code changes are included. The first build takes about a minute.

Stop everything with `docker compose down`. Adding `-v` also deletes the stored Parquet files. Containers don't start again by themselves after your laptop restarts, so run `docker compose up -d` again.

## 6. Check that it works

```bash
pytest
```

All tests should pass.

## 7. Load the data

The platform starts empty. Download the seasons you want (2018 up to the current season):

```bash
python src/f1_pipeline/ingest/jolpica.py --from 2018 --to 2026
```

The API allows 500 requests per hour, so a first full download takes about 5 hours. You can stop it at any time: the next run skips what is already on disk. To keep it running after you close the terminal, start it with `nohup` instead:

```bash
nohup python src/f1_pipeline/ingest/jolpica.py --from 2018 --to 2026 > /tmp/f1-ingest.log 2>&1 &
```

Then load the storage keys into your terminal and build the models:

```bash
set -a && source .env && set +a
```

```bash
dbt build --project-dir transform --profiles-dir transform
```

Every line should say `OK` or `PASS`. Open the dashboard on http://localhost:8501 to see the result.
