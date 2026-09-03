from google.cloud import bigquery

from src.config import BQ_DAILY_SUMMARY_TABLE_FULL_ID
from src.load_bigquery import get_bigquery_client


def fetch_regions():
    client = get_bigquery_client()
    query = f"""
        SELECT DISTINCT Region
        FROM `{BQ_DAILY_SUMMARY_TABLE_FULL_ID}`
    """
    result = client.query(query).result()
    return [row["Region"] for row in result]


def fetch_region_summary(region, start_date, end_date):
    client = get_bigquery_client()
    query = f"""
        SELECT *
        FROM `{BQ_DAILY_SUMMARY_TABLE_FULL_ID}`
        WHERE Region = @region
        AND date BETWEEN @start_date AND @end_date 
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("region", "STRING", region),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date)
        ]
    )

    result = client.query(query, job_config=job_config).result()

    return [dict(row) for row in result]

