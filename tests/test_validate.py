import pandas as pd

from src.transform import (
    NUMERIC_COLUMNS,
    select_columns,
    parse_datetime_columns,
    convert_numeric_columns,
    remove_duplicate_rows,
    add_business_columns,
)

from src.validate import (
    check_required_columns,
    count_duplicate_keys,
    check_null_rates,
    count_numeric_errors,
    build_quality_report,
    validate_or_raise,
)


def load_real_pre_dedup_data():
    sample = pd.read_csv(
        "data/sample/energy_2024_two_regions.csv"
    )
    df = select_columns(sample)
    df = parse_datetime_columns(df)
    df = convert_numeric_columns(df, NUMERIC_COLUMNS)
    df = add_business_columns(df)
    return df


def load_real_valid_data():
    df = load_real_pre_dedup_data()
    df = remove_duplicate_rows(df)
    return df


def test_check_required_columns():
    df = load_real_valid_data()
    result = check_required_columns(df)
    assert result == []


def test_count_duplicate_keys():
    df = load_real_pre_dedup_data()
    assert count_duplicate_keys(df) == 4
    clean_df = remove_duplicate_rows(df)
    assert count_duplicate_keys(clean_df) == 0


def test_check_null_rates():
    df = load_real_valid_data()
    result = check_null_rates(df)
    
    assert result == {
        "Timestamp": 0.0,
        "Region": 0.0,
        "Consumption": 0.0,
        "Thermal": 0.0,
        "Nuclear": 0.0,
        "Wind": 0.0,
        "Solar": 0.0,
        "Hydro": 0.0,
        "Bioenergy": 0.0,
        "Total_Production": 0.0,
        "Renewable_production": 0.0,
        "Renewable_Share": 0.0,
    }


def test_count_numeric_errors():
    df = load_real_valid_data()
    result = count_numeric_errors(df)
    
    assert result == {
        "negative_consumption": 0,
        "negative_total_production": 0,
        "negative_renewable_production": 0,
        "invalid_renewable_share": 0,
    }
    
    assert df["Consumption"].min() == 2133.0
    assert df["Consumption"].max() == 13947.0
    assert df["Total_Production"].min() == 105.0
    assert df["Total_Production"].max() == 10699.0
    assert df["Renewable_production"].min() == 99.0
    assert df["Renewable_production"].max() == 5854.0
    assert df["Renewable_Share"].min() == 0.025384615384615384
    assert df["Renewable_Share"].max() == 1.0


def test_build_quality_report():
    df = load_real_valid_data()
    report = build_quality_report(df)
    assert report["row_count"] == 35132
    assert set(report["regions"]) == {
        "Île-de-France",
        "Hauts-de-France",
    }
    assert report["start_timestamp"] == pd.Timestamp("2024-01-01 00:00:00+00:00")
    assert report["end_timestamp"] == pd.Timestamp("2024-12-31 23:30:00+00:00")
    assert report["missing_columns"] == []
    assert report["duplicate_count"] == 0
    assert report["null_rates"] == {
        "Timestamp": 0.0,
        "Region": 0.0,
        "Consumption": 0.0,
        "Thermal": 0.0,
        "Nuclear": 0.0,
        "Wind": 0.0,
        "Solar": 0.0,
        "Hydro": 0.0,
        "Bioenergy": 0.0,
        "Total_Production": 0.0,
        "Renewable_production": 0.0,
        "Renewable_Share": 0.0,
    }
    assert report["numeric_errors"] == {
        "negative_consumption": 0,
        "negative_total_production": 0,
        "negative_renewable_production": 0,
        "invalid_renewable_share": 0,
    }


def test_validate_or_raise():
    df = load_real_valid_data()
    report = validate_or_raise(df)
    assert report["row_count"] == 35132
    assert report["missing_columns"] == []
    assert report["duplicate_count"] == 0
    assert all(
        value == 0
        for value in report[
            "numeric_errors"
        ].values()
    )
