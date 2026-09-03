import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

from src.pipeline import run_pipeline

RAW_PATH = "/opt/airflow/data/raw/eco2mix-regional-cons-def.csv"


def check_file():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"File Not Found : {RAW_PATH}")


with DAG(
        dag_id="energy_pipeline",
        start_date=datetime(2026, 9, 3),
        schedule=None,
        catchup=False
) as dag:
    check_file_task = PythonOperator(
        task_id="check_file",
        python_callable=check_file,
        retries=1
    )
    run_pipeline_task = PythonOperator(
        task_id="run_pipeline",
        python_callable=run_pipeline,
        op_kwargs={"raw_path": RAW_PATH},
        retries=1
    )
    dbt_run_task = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt_energy && dbt run",
        retries=1
    )
    dbt_test_task = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt_energy && dbt test",
        retries=1
    )

    check_file_task >> run_pipeline_task >> dbt_run_task >> dbt_test_task