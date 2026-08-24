from src.pipeline import run_pipeline


def main():
    path_raw_file = "data/raw/eco2mix-regional-cons-def.csv"
    # small_exploration(path_raw_file)

    run_pipeline(path_raw_file)


if __name__ == "__main__":
    main()
