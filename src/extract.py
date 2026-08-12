import pandas as pd


def load_raw_csv(path):
    try:
        energy_df = pd.read_csv(path, sep=";")
        return energy_df
    except FileNotFoundError as exc:
        raise FileNotFoundError("The path is incorrect or the file doesn't exist") from exc


def create_working_sample(df):
    df["Date"] = pd.to_datetime(df["Date"])

    df_filtered = df[
        df["Date"].between("2024-01-01", "2024-12-31")
        & df["Région"].isin(["Île-de-France", "Hauts-de-France"])
        ]

    return df_filtered.copy()


def save_working_sample(df, path):
    df.to_csv(path, index=False)
