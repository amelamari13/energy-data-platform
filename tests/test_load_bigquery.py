import pandas as pd

from google.cloud import bigquery

from src.config import GCP_PROJECT_ID
from src.load_bigquery import (
    get_bigquery_client,
    build_table_id,
    load_dataframe,
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
        "Timestamp": [
            pd.Timestamp("2024-01-01 00:00:00")
        ],
        "Region": [
            "Île-de-France"
        ],
        "Consumption": [
            7843.0
        ],
        "Thermal": [
            197.0
        ],
        "Nuclear": [
            0.0
        ],
        "Wind": [
            126
        ],
        "Solar": [
            0.0
        ],
        "Hydro": [
            1.0
        ],
        "Bioenergy": [
            142.0
        ],
        "Total_Production": [
            466.0
        ],
        "Renewable_production": [
            269.0
        ],
        "Renewable_Share": [
            0.5772532188841202
        ],
    })

    fake_client = mocker.create_autospec(
        bigquery.Client,
        instance=True,
    )

    fake_job = mocker.Mock()

    fake_client.load_table_from_dataframe.return_value = fake_job

    mocker.patch(
        "src.load_bigquery.get_bigquery_client",
        return_value=fake_client,
    )

    mocker.patch(
        "src.load_bigquery.build_table_id",
        return_value="energy-project.energy.clean_energy",
    )

    load_dataframe(df)

    fake_client.load_table_from_dataframe.assert_called_once()

    args, kwargs = (
        fake_client
        .load_table_from_dataframe
        .call_args
    )

    pd.testing.assert_frame_equal(
        args[0],
        df,
    )

    assert args[1] == "energy-project.energy.clean_energy"

    fake_job.result.assert_called_once()
