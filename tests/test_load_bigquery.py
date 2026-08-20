import pandas as pd

from google.cloud import bigquery

from src.config import GCP_PROJECT_ID
from src.load_bigquery import (
    get_bigquery_client,
    build_table_id,
    load_dataframe, merge_staging_to_target,
)


def test_get_bigquery_client(mocker):
    fake_client = mocker.create_autospec(
        bigquery.Client,
        instance=True,
    )

    constructor = mocker.patch(
        "src.load_bigquery.bigquery.Client",
        autospec=True,
        return_value=fake_client,
    )

    result = get_bigquery_client()

    constructor.assert_called_once_with(
        project=GCP_PROJECT_ID
    )

    assert result is fake_client


def test_build_table_id():
    result = build_table_id(
        "energy-project",
        "energy",
        "clean_energy",
    )

    assert result == "energy-project.energy.clean_energy"

    def test_load_dataframe(mocker):
        df = pd.DataFrame({
            "Timestamp": [pd.Timestamp("2024-01-01 00:00:00")],
            "Region": ["Île-de-France"],
            "Consumption": [7843.0],
            "Thermal": [197.0],
            "Nuclear": [0.0],
            "Wind": [126],
            "Solar": [0.0],
            "Hydro": [1.0],
            "Bioenergy": [142.0],
            "Total_Production": [466.0],
            "Renewable_production": [269.0],
            "Renewable_Share": [0.5772532188841202],
        })

        fake_client = mocker.create_autospec(
            bigquery.Client,
            instance=True,
        )

        fake_job = mocker.Mock()

        fake_client.load_table_from_dataframe.return_value = fake_job

        full_table_id = "energy-project.energy.clean_energy"

        load_dataframe(
            fake_client,
            df,
            full_table_id,
        )

        fake_client.load_table_from_dataframe.assert_called_once_with(
            df,
            full_table_id,
        )

        fake_job.result.assert_called_once_with()


def test_merge_staging_to_target(mocker):
    fake_client = mocker.create_autospec(
        bigquery.Client,
        instance=True,
    )

    fake_job = mocker.Mock()
    fake_client.query.return_value = fake_job

    staging_table = "energy-project.energy.clean_energy_staging"
    target_table = "energy-project.energy.clean_energy"

    merge_staging_to_target(
        fake_client,
        staging_table,
        target_table,
    )

    fake_client.query.assert_called_once()

    sql = fake_client.query.call_args.args[0]

    assert f"MERGE `{target_table}` AS target" in sql
    assert f"USING `{staging_table}` AS staging" in sql
    assert "target.Timestamp = staging.Timestamp" in sql
    assert "target.Region = staging.Region" in sql
    assert "WHEN MATCHED THEN" in sql
    assert "WHEN NOT MATCHED THEN" in sql

    fake_job.result.assert_called_once_with()

    fake_client.delete_table.assert_called_once_with(
        staging_table
    )