from src.extract import *
from explore_data import *


def main():
    path_raw_file = "data/raw/eco2mix-regional-cons-def.csv"
    # small_exploration(path_raw_file)

    energy_df = load_raw_csv(path_raw_file)

    energy_df = create_working_sample(energy_df)

    path_sample_file = "data/sample/energy_2024_two_regions.csv"
    save_working_sample(energy_df, path_sample_file)


if __name__ == "__main__":
    main()
