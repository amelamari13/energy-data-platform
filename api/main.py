from fastapi import FastAPI

from api.service import get_regions, get_region_summary, get_region_anomalies, compare_regions, get_consumption_trend

app = FastAPI(
    title="Energy Data Platform API",
    description="API exposing regional energy consumption and production data (RTE source, aggregated via dbt)."
)


@app.get("/health")
def health():
    """Check that the API is running."""
    return {"status": "ok"}


@app.get("/regions")
def regions():
    """Return the list of available regions."""
    return get_regions()


@app.get("/summary/{region}")
def summary_region(region:str, start_date:str, end_date:str):
    """Return the daily summary for a given region and date range."""
    return get_region_summary(region, start_date, end_date)


@app.get("/summary/{region}/anomalies")
def anomalies(region: str, start_date: str, end_date: str):
    """Detect days where average consumption significantly deviates
    from the mean over the given period (standard deviation method,
    2-sigma threshold)."""
    return get_region_anomalies(region, start_date, end_date)

@app.get("/regions/compare")
def regions_compare(start_date: str, end_date: str):
    """Compare all regions by their average renewable energy share
    over the given period, ranked from highest to lowest."""
    return compare_regions(start_date, end_date)


@app.get("/summary/{region}/trend")
def consumption_trend(region: str, start_date: str, end_date: str):
    """Return the consumption trend (increasing, decreasing, or stable)
    for a given region over the given period."""
    return get_consumption_trend(region, start_date, end_date)