from datetime import datetime
from pathlib import Path

from airflow.decorators import dag
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping


DBT_PROJECT_PATH = Path("/usr/local/airflow/include/dbt/ecommerce")
DBT_EXECUTABLE = Path("/usr/local/airflow/dbt_venv/bin/dbt")


profile_config = ProfileConfig(
    profile_name="ecommerce",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="postgres_ecommerce",
        profile_args={"schema": "bronze"}
    )
)

project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH,
)

execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXECUTABLE,
)


@dag(
    dag_id="dbt_pipeline",
    schedule=None,              # ← disparada pelo sensor, não por cron
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["dbt", "silver", "gold"]
)
def dbt_pipeline():
    DbtTaskGroup(
        group_id="transformations",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
    )


dbt_pipeline()