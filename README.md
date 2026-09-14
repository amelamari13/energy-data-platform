# energy-data-platform

Pipeline for French electricity consumption and production data, from raw CSV extraction to an API deployed in production on Google Cloud Run.

## Table of Contents

- [Data Source](#data-source)
- [Working Sample](#working-sample)
- [Columns](#columns)
- [Architecture](#architecture)
- [Python Pipeline](#python-pipeline-extract--transform--validate)
- [BigQuery, Staging, and MERGE](#bigquery-staging-and-merge)
- [dbt Modeling](#dbt-modeling)
- [Airflow Orchestration](#airflow-orchestration)
- [FastAPI](#fastapi)
- [Docker](#docker)
- [Cloud Run](#cloud-run)
- [Cloud Scheduler](#cloud-scheduler)
- [Tests](#tests)
- [Running the Project Locally](#running-the-project-locally)
- [Project Limitations](#project-limitations)

## Data Source

The data comes from **RTE** (Réseau de Transport d'Électricité, the French electricity transmission system operator), via the file `eco2mix-regional-cons-def.csv`: regional electricity consumption and production, at half-hourly intervals, `;`-separated.

## Working Sample

The pipeline works on a subset of the raw file:

- year **2024** only;
- two regions: **Île-de-France** and **Hauts-de-France**;
- period covered: `2024-01-01 00:00:00` → `2024-12-31 23:30:00`.

Before deduplication: **35,136 rows**, 4 duplicates on the `(Timestamp, Region)` key.
After deduplication: **35,132 rows**, 0 duplicates.

## Columns

Mapping from the source CSV (French) to the names used throughout the project:

| Source column (CSV) | Python column |
|---|---|
| `Date - Heure` | `Timestamp` |
| `Région` | `Region` |
| `Consommation (MW)` | `Consumption` |
| `Thermique (MW)` | `Thermal` |
| `Nucléaire (MW)` | `Nuclear` |
| `Eolien (MW)` | `Wind` |
| `Solaire (MW)` | `Solar` |
| `Hydraulique (MW)` | `Hydro` |
| `Bioénergies (MW)` | `Bioenergy` |

Computed business columns: `Total_Production`, `Renewable_production`, `Renewable_Share`.

## Architecture

```
Raw RTE CSV
    ↓
extract.py
    ↓
transform.py
    ↓
validate.py
    ↓
BigQuery staging
    ↓
MERGE into clean table
    ↓
dbt staging
    ↓
dbt daily mart (daily_region_summary)
    ↓
FastAPI
    ↓
Cloud Run
```

Airflow orchestrates the pipeline + dbt sequence. Cloud Scheduler triggers the internal endpoint in production.

```
energy-data-platform/
├── airflow/dags/energy_pipeline.py
├── api/
│   ├── main.py
│   ├── repository.py
│   ├── service.py
│   └── static/          # web interface (index.html)
├── data/
│   ├── raw/             
│   ├── sample/
│   └── tests/
├── dbt_energy/
│   └── models/
│       ├── staging/
│       └── marts/
├── docker/Dockerfile
├── src/
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load_bigquery.py
│   └── pipeline.py
└── tests/
```

## Python Pipeline (extract / transform / validate)

- **`extract.py`**: reads the raw CSV, filters the sample (year + regions), saves a working CSV.
- **`transform.py`**: selects and renames columns, converts types (dates, numerics), removes duplicates on `(Timestamp, Region)`, computes business columns (`Total_Production`, `Renewable_production`, `Renewable_Share`).
- **`validate.py`**: quality checks without modifying the data — missing columns, residual duplicates, null-value rate, inconsistent numeric values (negative consumption, renewable share outside `[0, 1]`). `validate_or_raise()` halts the pipeline if an issue is deemed critical.

Principle: **transform** changes the data to make it correct, then **validate** checks that it actually is.

## BigQuery, Staging, and MERGE

Loading is **idempotent**: new data is first loaded into a temporary staging table, then merged into the final table via a SQL `MERGE` statement, on the `(Timestamp, Region)` key. Re-running the pipeline multiple times on the same data never creates duplicates — verified under real conditions when setting up Cloud Scheduler.

## dbt Modeling

- **Staging** (`stg_energy`): minimal cleaning, no business logic.
- **Mart** (`daily_region_summary`): one row per day and per region, with average/max consumption, total production, renewable production, and average renewable share.
- dbt tests: `not_null`, `unique` (combination of `Date` + `Region`), `accepted_values` on regions.

## Airflow Orchestration

`energy_pipeline` DAG (Docker Compose, local): `check_file → run_pipeline → dbt_run → dbt_test`. Retries configured, `catchup=False`.

## FastAPI

Exposed routes (from the `daily_region_summary` mart, except `/health` and `/internal/run-pipeline`):

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Checks that the API is responding |
| GET | `/regions` | Lists available regions |
| GET | `/summary/{region}` | Daily summary (consumption, production, renewable share) |
| GET | `/summary/{region}/anomalies` | Days where consumption deviates strongly from the average (standard-deviation method, 2σ threshold) |
| GET | `/regions/compare` | Ranking of regions by average renewable share |
| GET | `/summary/{region}/trend` | Consumption trend (increasing / decreasing / stable) |
| POST | `/internal/run-pipeline` | Triggers a full pipeline run (called by Cloud Scheduler) |

A minimal web interface (`/ui`) lets you test all these endpoints from a browser, without going through Swagger or Postman — forms, results in JSON.

## Docker

Image based on `python:3.11-slim`, runs the API via Uvicorn on port `8080`. Built and pushed to **Artifact Registry** (`europe-west9`).

## Cloud Run

The API is deployed on **Cloud Run**, a containerized hosting service that automatically scales to zero instances when there is no traffic. Configuration (`GCP_PROJECT_ID`, `BQ_DATASET_ID`, etc.) is injected via environment variables — never hardcoded (see [Limitations](#project-limitations)).

The Cloud Run service account has the `BigQuery Data Viewer` and `BigQuery Job User` IAM roles, needed for the API to read the mart in production.

## Cloud Scheduler

A scheduled job (`energy-monthly-run`) calls `POST /internal/run-pipeline` once a month, demonstrating automated triggering in production without running Airflow continuously in the cloud. See [Limitations](#project-limitations) for a note on the actual relevance of this frequency for this project.

## Tests

```bash
pytest --ignore=tests/test_airflow_dag.py
```

`test_airflow_dag.py` only runs inside the Airflow container (Airflow is not natively supported on Windows, but was still properly tested on my end):

```bash
docker compose exec -u root airflow-scheduler python -m pip install pytest
docker compose cp ../tests/test_airflow_dag.py airflow-scheduler:/tmp/test_airflow_dag.py
docker compose exec airflow-scheduler python -m pytest /tmp/test_airflow_dag.py
```

Extraction and transformation functions are tested with real values from the source CSV. Validation tests combine real data with deliberately crafted edge cases (null values, negative values) to cover error scenarios. Service and infrastructure layers (API, BigQuery) are tested with mocks and synthetic data, following standard practice for this type of code.

## Running the Project Locally

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8080
```

Then open `http://127.0.0.1:8080/ui`.

## Project Limitations

- **Configuration management**: sensitive variables (`GCP_PROJECT_ID`, `BQ_DATASET_ID`, etc.) are injected via `.env` files, never hardcoded, following the *12-factor apps* principle. Known limitation: these values are duplicated across two separate `.env` files (local and Airflow) rather than centralized in a single source. In production, a secrets manager (GCP Secret Manager) or a shared `.env` file between the two services would be preferable.
- **Full in-memory processing**: the pipeline loads the entire CSV into memory with Pandas rather than processing it in batches (*chunks*). For this project (~450 MB), this required increasing the memory allocated to Cloud Run to 4 Gi. This approach would not scale to a significantly larger data volume. The best practice for larger volumes would be to process the file in batches using Pandas' `chunksize` parameter (`pd.read_csv(..., chunksize=10000)`): each batch is transformed and written independently, keeping memory footprint stable and predictable regardless of source file size, rather than a spike proportional to its total size.
- **Cloud Scheduler on static data**: the source dataset is a fixed snapshot (year 2024, never updated). An automated monthly pipeline run therefore has no real functional purpose here — the idempotent `MERGE` simply guarantees no data is duplicated. This job was set up to demonstrate mastery of the mechanism (decoupling scheduling from orchestration), not to meet a genuine business need for this specific project.
- **No rich frontend layer**: the `/ui` interface is deliberately minimal (HTML/CSS/JS without a framework), designed to test the API rather than serve as an advanced visualization tool.
- **Airflow not natively testable on Windows**: requires Docker Compose and running tests inside the container (see Tests section).
