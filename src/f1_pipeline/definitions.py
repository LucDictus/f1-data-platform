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


@dg.multi_asset(specs=[dg.AssetSpec(["jolpica", "results"]), dg.AssetSpec(["jolpica", "pitstops"])])
def raw_jolpica():
    with requests.Session() as s:
        jolpica.ingest_season(s, jolpica.CURRENT_SEASON)
    yield dg.MaterializeResult(asset_key=["jolpica", "results"])
    yield dg.MaterializeResult(asset_key=["jolpica", "pitstops"])


@dbt_assets(manifest=project.manifest_path)
def f1_dbt(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


weekly_job = dg.define_asset_job("weekly_refresh", selection=dg.AssetSelection.all())

weekly_schedule = dg.ScheduleDefinition(
    job=weekly_job,
    cron_schedule="0 6 * * 1",
    execution_timezone="Europe/Amsterdam",
)


defs = dg.Definitions(
    assets=[raw_jolpica, f1_dbt],
    schedules=[weekly_schedule],
    resources={"dbt": DbtCliResource(project_dir=project)},
)
