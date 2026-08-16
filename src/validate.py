import logging

REQUIRED_COLUMNS = [
    "Timestamp",
    "Region",
    "Consumption",
    "Thermal",
    "Nuclear",
    "Wind",
    "Solar",
    "Hydro",
    "Bioenergy",
    "Total_Production",
    "Renewable_production",
    "Renewable_Share",
]


def check_required_columns(df):
    columns = df.columns

    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in columns:
            missing_columns.append(column)

    if not missing_columns:
        logging.info("All columns are present")
    else:
        logging.warning("Columns are missing!")
    return missing_columns


def count_duplicate_keys(df):
    return df.duplicated(subset=["Timestamp", "Region"]).sum()


def check_null_rates(df):
    return {
        column: df[column].isna().mean()
        for column in df.columns
    }


def count_numeric_errors(df):
    return {
        "negative_consumption": (df["Consumption"] < 0).sum(),
        "negative_total_production": (df["Total_Production"] < 0).sum(),
        "negative_renewable_production": (df["Renewable_production"] < 0).sum(),
        "invalid_renewable_share": ((df["Renewable_Share"] < 0) | (df["Renewable_Share"] > 1)).sum()
    }


def build_quality_report(df):
    return {
        "row_count": df.shape[0],
        "regions": df["Region"].unique().tolist(),
        "start_timestamp": df["Timestamp"].min(),
        "end_timestamp": df["Timestamp"].max(),
        "missing_columns": check_required_columns(df),
        "duplicate_count": count_duplicate_keys(df),
        "null_rates": check_null_rates(df),
        "numeric_errors": count_numeric_errors(df)
    }


def validate_or_raise(df):
    missing_columns = check_required_columns(df)

    if missing_columns:
        raise ValueError("Missing required columns")

    report = build_quality_report(df)

    if report["duplicate_count"] > 0:
        raise ValueError("Duplicate business keys")

    if any(report["numeric_errors"].values()):
        raise ValueError("Invalid numeric values")

    return report
