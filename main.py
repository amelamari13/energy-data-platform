from api.repository import fetch_regions, fetch_region_summary
from src.pipeline import run_pipeline


def main():
    path_raw_file = "data/raw/eco2mix-regional-cons-def.csv"
    # small_exploration(path_raw_file)

    # run_pipeline(path_raw_file)

    print(fetch_regions())
    print(fetch_region_summary("Île-de-France", "2024-01-01", "2024-01-01"))


if __name__ == "__main__":
    main()
