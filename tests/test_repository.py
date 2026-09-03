from google.cloud import bigquery

from api.repository import fetch_region_summary, fetch_regions

REAL_DAILY_SUMMARY = {
    "Date": "2024-01-01",
    "Region": "Île-de-France",
    "Average_Consumption": 7793.291666666667,
    "Max_Consumption": 8767.0,
    "Total_Production": 21825.0,
    "Renewable_production": 11972.0,
    "Average_Renewable_Share": 0.5474191547555117,
}


def test_fetch_regions(mocker):
    fake_client = mocker.create_autospec(
        bigquery.Client,
        instance=True,
    )
    fake_client.query.return_value.result.return_value = [
        {"Region": "Île-de-France"},
        {"Region": "Hauts-de-France"},
    ]
    mocker.patch(
        "api.repository.get_bigquery_client",
        return_value=fake_client,
    )
    result = fetch_regions()
    assert set(result) == {
        "Île-de-France",
        "Hauts-de-France",
    }


def test_fetch_region_summary(mocker):
    fake_client = mocker.create_autospec(
        bigquery.Client,
        instance=True,
    )
    fake_client.query.return_value.result.return_value = [REAL_DAILY_SUMMARY]
    mocker.patch(
        "api.repository.get_bigquery_client",
        return_value=fake_client,
    )
    result = fetch_region_summary(
        "Île-de-France",
        "2024-01-01",
        "2024-01-01",
    )
    assert result == [REAL_DAILY_SUMMARY]
