import pandas as pd

from google.cloud import bigquery

from src.config import *
from src.load_bigquery import (
    get_bigquery_client,
    load_staging_table,
    merge_staging_to_target,
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


def test_load_staging_table(mocker):
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

    load_staging_table(fake_client, df)

    args, kwargs = fake_client.load_table_from_dataframe.call_args

    pd.testing.assert_frame_equal(args[0], df)
    assert args[1] == BQ_STAGING_TABLE_FULL_ID
    assert kwargs["job_config"].write_disposition == "WRITE_TRUNCATE"

    fake_job.result.assert_called_once_with()


def test_merge_staging_to_target(mocker):
    fake_client = mocker.create_autospec(
        bigquery.Client,
        instance=True,
    )

    fake_job = mocker.Mock()
    fake_client.query.return_value = fake_job

    merge_staging_to_target(fake_client)

    sql = fake_client.query.call_args.args[0]

    assert f"MERGE `{BQ_CLEAN_TABLE_FULL_ID}` AS target" in sql
    assert f"USING `{BQ_STAGING_TABLE_FULL_ID}` AS staging" in sql
    assert "target.Timestamp = staging.Timestamp" in sql
    assert "target.Region = staging.Region" in sql
    assert "WHEN MATCHED THEN" in sql
    assert "WHEN NOT MATCHED THEN" in sql

    fake_job.result.assert_called_once_with()
