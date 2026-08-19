from google.cloud import bigquery

from src.config import *


def get_bigquery_client():
    return bigquery.Client(project=GCP_PROJECT_ID)


def build_table_id(project_id, dataset_id, table_id):
    return f"{project_id}.{dataset_id}.{table_id}"


def load_dataframe(df):
    client = get_bigquery_client()
    table_id = build_table_id(GCP_PROJECT_ID, BQ_DATASET_ID, BQ_CLEAN_TABLE_ID)

    job = client.load_table_from_dataframe(df, table_id)

    job.result()