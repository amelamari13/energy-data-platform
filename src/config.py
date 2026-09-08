import os

from dotenv import load_dotenv
load_dotenv()


def get_required_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Variable d'environnement manquante : {name}"
        )
    return value


GCP_PROJECT_ID = get_required_env("GCP_PROJECT_ID")
BQ_DATASET_ID = get_required_env("BQ_DATASET_ID")
BQ_CLEAN_TABLE_ID = get_required_env("BQ_CLEAN_TABLE_ID")
BQ_STAGING_TABLE_ID = get_required_env("BQ_STAGING_TABLE_ID")
BQ_DAILY_SUMMARY_TABLE_ID = get_required_env("BQ_DAILY_SUMMARY_TABLE_ID")

BQ_STAGING_TABLE_FULL_ID = (
    f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_STAGING_TABLE_ID}"
)

BQ_CLEAN_TABLE_FULL_ID = (
    f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_CLEAN_TABLE_ID}"
)

BQ_DAILY_SUMMARY_TABLE_FULL_ID = (
    f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_DAILY_SUMMARY_TABLE_ID}"
)