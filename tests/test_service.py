import pytest

from api.service import get_regions, get_region_summary, get_region_anomalies, compare_regions, get_consumption_trend

REAL_DAILY_SUMMARY = {
    "Date": "2024-01-01",
    "Region": "Île-de-France",
    "Average_Consumption": 7793.291666666667,
    "Max_Consumption": 8767.0,
    "Total_Production": 21825.0,
    "Renewable_production": 11972.0,
    "Average_Renewable_Share": 0.5474191547555117,
}


def test_get_regions(mocker):
    repository_result = [
        "Île-de-France",
        "Hauts-de-France",
    ]
    mocker.patch(
        "api.service.fetch_regions",
        return_value=repository_result,
    )
    result = get_regions()
    assert result == repository_result


def test_get_region_summary(mocker):
    repository_result = [
        REAL_DAILY_SUMMARY
    ]
    mocker.patch(
        "api.service.fetch_region_summary",
        return_value=repository_result,
    )
    result = get_region_summary(
        region="Île-de-France",
        start_date="2024-01-01",
        end_date="2024-01-01",
    )
    assert result == repository_result


def test_get_region_anomalies(mocker):
    fake_data = [
        {"Date": "2024-01-01", "Average_Consumption": 7800},
        {"Date": "2024-01-02", "Average_Consumption": 7900},
        {"Date": "2024-01-03", "Average_Consumption": 8000},
        {"Date": "2024-01-04", "Average_Consumption": 7850},
        {"Date": "2024-01-05", "Average_Consumption": 7950},
        {"Date": "2024-01-06", "Average_Consumption": 25000},
    ]
    mocker.patch(
        "api.service.fetch_region_summary",
        return_value=fake_data,
    )
    result = get_region_anomalies("Île-de-France", "2024-01-01", "2024-01-06")
    assert len(result) == 1
    assert result[0]["Date"] == "2024-01-06"


def test_compare_regions(mocker):
    def fake_fetch_region_summary(region, start_date, end_date):
        if region == "Île-de-France":
            return [
                {"Average_Renewable_Share": 0.6},
                {"Average_Renewable_Share": 0.5},
            ]
        return [
            {"Average_Renewable_Share": 0.3},
            {"Average_Renewable_Share": 0.4},
        ]

    mocker.patch(
        "api.service.fetch_regions",
        return_value=["Île-de-France", "Hauts-de-France"],
    )
    mocker.patch(
        "api.service.fetch_region_summary",
        side_effect=fake_fetch_region_summary,
    )

    result = compare_regions("2024-01-01", "2024-01-02")

    assert result[0]["region"] == "Île-de-France"
    assert result[0]["average_renewable_share"] == pytest.approx(0.55)
    assert result[1]["region"] == "Hauts-de-France"
    assert result[1]["average_renewable_share"] == pytest.approx(0.35)


def test_get_consumption_trend_increasing(mocker):
    mocker.patch(
        "api.service.fetch_region_summary",
        return_value=[
            {"Average_Consumption": 7000},
            {"Average_Consumption": 7100},
            {"Average_Consumption": 8500},
            {"Average_Consumption": 8600},
        ],
    )
    result = get_consumption_trend("Île-de-France", "2024-01-01", "2024-01-04")
    assert result == "increasing"


def test_get_consumption_trend_stable(mocker):
    mocker.patch(
        "api.service.fetch_region_summary",
        return_value=[
            {"Average_Consumption": 7000},
            {"Average_Consumption": 7050},
            {"Average_Consumption": 7020},
            {"Average_Consumption": 7010},
        ],
    )
    result = get_consumption_trend("Île-de-France", "2024-01-01", "2024-01-04")
    assert result == "stable"


def test_get_consumption_trend_insufficient_data(mocker):
    mocker.patch(
        "api.service.fetch_region_summary",
        return_value=[{"Average_Consumption": 7000}],
    )
    result = get_consumption_trend("Île-de-France", "2024-01-01", "2024-01-01")
    assert result == "insufficient_data"