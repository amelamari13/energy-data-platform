import pandas as pd
import pytest

from src.transform import (
    NUMERIC_COLUMNS,
    select_columns,
    parse_datetime_columns,
    convert_numeric_columns,
    remove_duplicate_rows,
    add_business_columns,
    transform_energy_data,
)


SAMPLE_PATH = "data/sample/energy_2024_two_regions.csv"


def test_select_columns():
    sample = pd.read_csv(SAMPLE_PATH)

    real_row = sample.iloc[[0]]

    result = select_columns(real_row)

    assert list(result.columns) == [
        "Timestamp",
        "Region",
        "Consumption",
        "Thermal",
        "Nuclear",
        "Wind",
        "Solar",
        "Hydro",
        "Bioenergy",
    ]

    assert result.iloc[0]["Timestamp"] == real_row.iloc[0]["Date - Heure"]
    assert result.iloc[0]["Region"] == real_row.iloc[0]["Région"]
    assert result.iloc[0]["Consumption"] == real_row.iloc[0]["Consommation (MW)"]
    assert result.iloc[0]["Thermal"] == real_row.iloc[0]["Thermique (MW)"]
    assert result.iloc[0]["Nuclear"] == real_row.iloc[0]["Nucléaire (MW)"]
    assert result.iloc[0]["Wind"] == real_row.iloc[0]["Eolien (MW)"]
    assert result.iloc[0]["Solar"] == real_row.iloc[0]["Solaire (MW)"]
    assert result.iloc[0]["Hydro"] == real_row.iloc[0]["Hydraulique (MW)"]
    assert result.iloc[0]["Bioenergy"] == real_row.iloc[0]["Bioénergies (MW)"]


def test_parse_datetime_columns():
    sample = pd.read_csv(SAMPLE_PATH)
    selected = select_columns(sample.iloc[[0]])

    result = parse_datetime_columns(selected)

    assert result.iloc[0]["Timestamp"] == pd.Timestamp("2024-01-01 00:00:00")
    assert pd.api.types.is_datetime64_any_dtype(result["Timestamp"])

def test_convert_numeric_columns():
    sample = pd.read_csv(SAMPLE_PATH)
    selected = select_columns(sample.iloc[[0]])

    result = convert_numeric_columns(selected, NUMERIC_COLUMNS)

    assert result.iloc[0]["Consumption"] == 7843.0
    assert result.iloc[0]["Thermal"] == 197.0
    assert result.iloc[0]["Nuclear"] == 0.0
    assert result.iloc[0]["Wind"] == 126
    assert result.iloc[0]["Solar"] == 0.0
    assert result.iloc[0]["Hydro"] == 1.0
    assert result.iloc[0]["Bioenergy"] == 142.0

    for column in NUMERIC_COLUMNS:
        assert pd.api.types.is_numeric_dtype(result[column])


def test_remove_duplicate_rows():
    df = pd.DataFrame({
        "Timestamp": [
            pd.Timestamp("2024-03-31 03:00:00"),
            pd.Timestamp("2024-03-31 03:00:00"),
            pd.Timestamp("2024-03-31 03:30:00"),
        ],
        "Region": [
            "Île-de-France",
            "Île-de-France",
            "Île-de-France",
        ],
        "Consumption": [
            6762.0,
            6762.0,
            6669.0,
        ],
        "Thermal": [
            160.0,
            160.0,
            160.0,
        ],
        "Nuclear": [
            0.0,
            0.0,
            0.0,
        ],
        "Wind": [
            39,
            39,
            41,
        ],
        "Solar": [
            0.0,
            0.0,
            0.0,
        ],
        "Hydro": [
            3.0,
            3.0,
            3.0,
        ],
        "Bioenergy": [
            143.0,
            143.0,
            144.0,
        ],
    })

    result = remove_duplicate_rows(df)

    assert len(result) == 2

    assert result.duplicated(
        subset=["Timestamp", "Region"]
    ).sum() == 0


def test_add_business_columns():
    df = pd.DataFrame({
        "Timestamp": [
            pd.Timestamp("2024-01-01 00:00:00"),
            pd.Timestamp("2024-01-01 00:00:00"),
        ],
        "Region": [
            "Île-de-France",
            "Hauts-de-France",
        ],
        "Consumption": [
            7843.0,
            5497.0,
        ],
        "Thermal": [
            197.0,
            398.0,
        ],
        "Nuclear": [
            0.0,
            3349.0,
        ],
        "Wind": [
            126,
            5445,
        ],
        "Solar": [
            0.0,
            0.0,
        ],
        "Hydro": [
            1.0,
            2.0,
        ],
        "Bioenergy": [
            142.0,
            126.0,
        ],
    })

    result = add_business_columns(df)

    assert result.iloc[0]["Total_Production"] == 466.0
    assert result.iloc[0]["Renewable_production"] == 269.0
    assert result.iloc[0]["Renewable_Share"] == pytest.approx(
        0.5772532188841202
    )

    assert result.iloc[1]["Total_Production"] == 9320.0
    assert result.iloc[1]["Renewable_production"] == 5573.0
    assert result.iloc[1]["Renewable_Share"] == pytest.approx(
        0.597961373390558
    )


def test_transform_energy_data():
    sample = pd.read_csv(SAMPLE_PATH)

    result = transform_energy_data(sample)

    assert len(sample) == 35136
    assert len(result) == 35132

    assert result.duplicated(
        subset=["Timestamp", "Region"]
    ).sum() == 0

    assert set(result["Region"]) == {
        "Île-de-France",
        "Hauts-de-France",
    }

    assert result["Timestamp"].min() == pd.Timestamp(
        "2024-01-01 00:00:00"
    )

    assert result["Timestamp"].max() == pd.Timestamp(
        "2024-12-31 23:30:00"
    )