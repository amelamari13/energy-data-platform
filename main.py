from src.config import *
from src.extract import *
from explore_data import *
from src.transform import transform_energy_data
from src.validate import validate_or_raise
from src.load_bigquery import load_dataframe, build_table_id, get_bigquery_client


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

    target_table = build_table_id(
        GCP_PROJECT_ID,
        BQ_DATASET_ID,
        BQ_CLEAN_TABLE_ID,
    )

    staging_table = build_table_id(
        GCP_PROJECT_ID,
        BQ_DATASET_ID,
        BQ_STAGING_TABLE_ID,
    )

    client = get_bigquery_client()

    load_dataframe(client, energy_df, staging_table)


if __name__ == "__main__":
    main()
