from src.extract import *
from explore_data import *
from src.transform import transform_energy_data
from src.validate import validate_or_raise
from src.load_bigquery import load_dataframe


def main():
    path_raw_file = "data/raw/eco2mix-regional-cons-def.csv"
    # small_exploration(path_raw_file)

    energy_df = load_raw_csv(path_raw_file)

    energy_df = create_working_sample(energy_df)

    path_sample_file = "data/sample/energy_2024_two_regions.csv"
    save_working_sample(energy_df, path_sample_file)

    energy_df = transform_energy_data(energy_df)

    report = validate_or_raise(energy_df)
    print("REPORT")
    print(report)

    load_dataframe(energy_df)


if __name__ == "__main__":
    main()
