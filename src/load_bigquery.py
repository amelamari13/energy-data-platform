from google.cloud import bigquery

from src.config import *


def get_bigquery_client():
    return bigquery.Client(project=GCP_PROJECT_ID)


def load_staging_table(client, df):
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_dataframe(df, BQ_STAGING_TABLE_FULL_ID, job_config=job_config)

    job.result()


def merge_staging_to_target(client):
    query = f"""
    MERGE `{BQ_CLEAN_TABLE_FULL_ID}` AS target
    USING `{BQ_STAGING_TABLE_FULL_ID}` AS staging
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
