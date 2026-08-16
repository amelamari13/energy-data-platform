import pandas as pd

from src.extract import (
    load_raw_csv,
    create_working_sample,
    save_working_sample,
)

RAW_PATH = "data/tests/eco2mix_test_sample_exact.csv"


def test_load_raw_csv():
    result = load_raw_csv(RAW_PATH)

    assert len(result) == 8
    assert len(result.columns) == 32
    assert set(result["Région"]) == {
        "Île-de-France",
        "Hauts-de-France",
        "Grand Est",
        "Auvergne-Rhône-Alpes",
    }

    assert result.iloc[0]["Région"] == "Île-de-France"
    assert result.iloc[0]["Consommation (MW)"] == 7800

    assert result["Consommation (MW)"].head(3).sum() == 20900


def test_create_working_sample():
    raw_df = pd.read_csv(RAW_PATH, sep=";")

    result = create_working_sample(raw_df)

    result_dates = pd.to_datetime(
        result["Date"],
        dayfirst=True,
        errors="coerce",
    )

    assert len(result) == 4
    assert set(result["Région"]) == {
        "Île-de-France",
        "Hauts-de-France",
    }
    assert set(result_dates.dt.year) == {2024}
    assert list(result.columns) == list(raw_df.columns)


def test_save_working_sample(tmp_path):
    raw_df = pd.read_csv(RAW_PATH, sep=";")
    sample = create_working_sample(raw_df)

    output_path = tmp_path / "energy_2024_two_regions.csv"

    save_working_sample(sample, output_path)

    assert output_path.exists()

    reloaded = pd.read_csv(output_path)

    assert len(reloaded) == 4
    assert reloaded.iloc[0]["Région"] == "Île-de-France"
    assert reloaded.iloc[0]["Date"] == "2024-01-01"
    assert reloaded.iloc[0]["Consommation (MW)"] == 7800
    assert reloaded.iloc[0]["Eolien (MW)"] == 120