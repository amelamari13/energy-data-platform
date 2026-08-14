import pandas as pd

NUMERIC_COLUMNS = [
    "Consumption",
    "Thermal",
    "Nuclear",
    "Wind",
    "Solar",
    "Hydro",
    "Bioenergy",
]

COLUMN_RENAME_MAP = {
    "Date - Heure": "Timestamp",
    "Région": "Region",
    "Consommation (MW)": "Consumption",
    "Thermique (MW)": "Thermal",
    "Nucléaire (MW)": "Nuclear",
    "Eolien (MW)": "Wind",
    "Solaire (MW)": "Solar",
    "Hydraulique (MW)": "Hydro",
    "Bioénergies (MW)": "Bioenergy",
}


def select_columns(df):
    df = df[list(COLUMN_RENAME_MAP.keys())].copy()
    df = df.rename(columns=COLUMN_RENAME_MAP)
    return df


def parse_datetime_columns(df):
    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.tz_convert("Europe/Paris").dt.tz_localize(None)
    return df


def convert_numeric_columns(df, columns):
    for column in columns:
        df[column] = pd.to_numeric(df[column])
    return df


def remove_duplicate_rows(df):
    df = df.drop_duplicates(
        subset=["Timestamp", "Region"]
    )
    return df


def add_business_columns(df):
    df["Total_Production"] = (
            df["Thermal"]
            + df["Nuclear"]
            + df["Wind"]
            + df["Solar"]
            + df["Hydro"]
            + df["Bioenergy"]
    )

    df["Renewable_production"] = (
            df["Wind"]
            + df["Solar"]
            + df["Hydro"]
            + df["Bioenergy"]
    )

    df["Renewable_Share"] = (
            df["Renewable_production"]
            / df["Total_Production"]
    )

    return df


def transform_energy_data(df):
    df = select_columns(df)
    df = parse_datetime_columns(df)
    df = convert_numeric_columns(df, NUMERIC_COLUMNS)
    df = remove_duplicate_rows(df)
    df = add_business_columns(df)
    return df
