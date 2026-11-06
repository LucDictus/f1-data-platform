import os
from pathlib import Path

import dagster as dg
import requests
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from f1_pipeline.ingest import jolpica

# dagster-dbt runs dbt from transform/, so give dbt an absolute data path.
os.environ.setdefault("F1_DATA_DIR", str(Path("data").resolve()))

project = DbtProject(project_dir=Path("transform"), profiles_dir=Path("transform"))
project.prepare_if_dev()


season_partitions = dg.StaticPartitionsDefinition(
    [str(y) for y in range(2018, jolpica.CURRENT_SEASON + 1)]
)


@dg.multi_asset(
    specs=[dg.AssetSpec(["jolpica", "results"]), dg.AssetSpec(["jolpica", "pitstops"])],
    partitions_def=season_partitions,
    retry_policy=dg.RetryPolicy(max_retries=3, delay=30),
)
def raw_jolpica(context: dg.AssetExecutionContext):
    season = int(context.partition_key)
    with requests.Session() as s:
        jolpica.ingest_season(s, season)
    yield dg.MaterializeResult(asset_key=["jolpica", "results"])
    yield dg.MaterializeResult(asset_key=["jolpica", "pitstops"])


@dbt_assets(manifest=project.manifest_path)
def f1_dbt(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


weekly_job = dg.define_asset_job("weekly_refresh", selection=dg.AssetSelection.all())


# The job is partitioned, so each tick must say which season to refresh.
@dg.schedule(job=weekly_job, cron_schedule="0 6 * * 1", execution_timezone="Europe/Amsterdam")
def weekly_schedule():
    return dg.RunRequest(partition_key=str(jolpica.CURRENT_SEASON))


defs = dg.Definitions(
    assets=[raw_jolpica, f1_dbt],
    schedules=[weekly_schedule],
    resources={"dbt": DbtCliResource(project_dir=project)},
)
