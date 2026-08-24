from src.extract import create_working_sample, load_raw_csv
from src.load_bigquery import (
    get_bigquery_client,
    load_staging_table,
    merge_staging_to_target
)
from src.transform import transform_energy_data
from src.validate import validate_or_raise


def run_pipeline(raw_path):
    raw_energy_df = load_raw_csv(raw_path)

    energy_df = create_working_sample(raw_energy_df)

    energy_df = transform_energy_data(energy_df)

    validate_or_raise(energy_df)

    client = get_bigquery_client()

    load_staging_table(client, energy_df)

    merge_staging_to_target(client)
