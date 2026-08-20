from google.cloud import bigquery

from src.config import *


def get_bigquery_client():
    return bigquery.Client(project=GCP_PROJECT_ID)


def build_table_id(project_id, dataset_id, table_id):
    return f"{project_id}.{dataset_id}.{table_id}"


def load_dataframe(client, df, full_table_id):
    job = client.load_table_from_dataframe(df, full_table_id)

    job.result()


def merge_staging_to_target(client, staging_table, target_table):
    query = f"""
    MERGE `{target_table}` AS target
    USING `{staging_table}` AS staging
    ON target.Timestamp = staging.Timestamp
    AND target.Region = staging.Region
    
    WHEN MATCHED THEN 
    UPDATE SET
        Consumption = staging.Consumption,
        Thermal = staging.Thermal,
        Nuclear = staging.Nuclear,
        Wind = staging.Wind,
        Solar = staging.Solar,
        Hydro = staging.Hydro,
        Bioenergy = staging.Bioenergy,
        Total_Production = staging.Total_Production,
        Renewable_production = staging.Renewable_production,
        Renewable_Share = staging.Renewable_Share
    
    WHEN NOT MATCHED THEN
    INSERT (
        Timestamp,
        Region,
        Consumption,
        Thermal,
        Nuclear,
        Wind,
        Solar,
        Hydro,
        Bioenergy,
        Total_Production,
        Renewable_production,
        Renewable_Share
    )
    VALUES (
        staging.Timestamp,
        staging.Region,
        staging.Consumption,
        staging.Thermal,
        staging.Nuclear,
        staging.Wind,
        staging.Solar,
        staging.Hydro,
        staging.Bioenergy,
        staging.Total_Production,
        staging.Renewable_production,
        staging.Renewable_Share
    )
    """

    job = client.query(query)
    job.result()

    client.delete_table(staging_table)
