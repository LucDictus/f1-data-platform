FROM python:3.12-slim

# Run as a normal user with the same id as you, so files written to data/ stay yours.
RUN useradd --create-home --uid 1000 f1
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY transform ./transform
COPY dashboard ./dashboard
RUN pip install --no-cache-dir -e ".[dev]" && chown -R f1 /app

USER f1
ENV F1_DATA_DIR=/app/data DAGSTER_HOME=/app/data/dagster_home
# DAGSTER_HOME lives in the mounted data/ folder, so create it at start-up.
CMD ["sh", "-c", "mkdir -p \"$DAGSTER_HOME\" && exec dagster dev -m f1_pipeline.definitions -h 0.0.0.0 -p 3000"]
