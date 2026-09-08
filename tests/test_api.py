from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

REAL_DAILY_SUMMARY = {
    "Date": "2024-01-01",
    "Region": "Île-de-France",
    "Average_Consumption": 7793.291666666667,
    "Max_Consumption": 8767.0,
    "Total_Production": 21825.0,
    "Renewable_production": 11972.0,
    "Average_Renewable_Share": 0.5474191547555117,
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_regions_endpoint(mocker):
    fake_result = ["Île-de-France", "Hauts-de-France"]
    mocker.patch(
        "api.main.get_regions",
        return_value=fake_result,
    )
    response = client.get("/regions")
    assert response.status_code == 200
    assert response.json() == fake_result


def test_summary_endpoint(mocker):
    fake_result = [REAL_DAILY_SUMMARY]
    mocker.patch(
        "api.main.get_region_summary",
        return_value=fake_result,
    )
    response = client.get(
        "/summary/Île-de-France",
        params={"start_date": "2024-01-01", "end_date": "2024-01-01"},
    )
    assert response.status_code == 200
    assert response.json() == fake_result


def test_anomalies_endpoint(mocker):
    fake_result = [{"Date": "2024-01-04", "Average_Consumption": 15000}]
    mocker.patch(
        "api.main.get_region_anomalies",
        return_value=fake_result,
    )
    response = client.get(
        "/summary/Île-de-France/anomalies",
        params={"start_date": "2024-01-01", "end_date": "2024-01-04"},
    )
    assert response.status_code == 200
    assert response.json() == fake_result


def test_regions_compare_endpoint(mocker):
    fake_result = [
        {"region": "Île-de-France", "average_renewable_share": 0.55},
        {"region": "Hauts-de-France", "average_renewable_share": 0.35},
    ]
    mocker.patch(
        "api.main.compare_regions",
        return_value=fake_result,
    )
    response = client.get(
        "/regions/compare",
        params={"start_date": "2024-01-01", "end_date": "2024-01-02"},
    )
    assert response.status_code == 200
    assert response.json() == fake_result


def test_consumption_trend_endpoint(mocker):
    fake_result = "increasing"
    mocker.patch(
        "api.main.get_consumption_trend",
        return_value=fake_result,
    )
    response = client.get(
        "/summary/Île-de-France/trend",
        params={"start_date": "2024-01-01", "end_date": "2024-01-04"},
    )
    assert response.status_code == 200
    assert response.json() == fake_result


def test_internal_run_pipeline(mocker):
    pipeline_mock = mocker.patch(
        "api.main.run_pipeline",
        return_value={
            "status": "success",
            "sample_row_count": 35136,
            "final_row_count": 35132,
        },
    )
    response = client.post("/internal/run-pipeline")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "sample_row_count": 35136,
        "final_row_count": 35132,
    }
    pipeline_mock.assert_called_once()