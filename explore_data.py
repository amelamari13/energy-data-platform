import pandas as pd


def small_exploration(path):
    energy_df = pd.read_csv(path, sep=";")
    headers = energy_df.columns
    print(headers)

    # Line and column number
    print(energy_df.shape[0])
    print(len(headers))

    # Column type
    # print(energy_df.dtypes) -> shows mixed types for some columns
    energy_l1 = energy_df.iloc[0, :]
    print(energy_l1)
    for i in range(len(energy_l1)):
        print(headers[i] + " : " + str(type(energy_l1[i])))

    # All regions
    regions = set(energy_df.loc[:, 'Région'])
    print(regions)

    # Covered period
    energy_df_sorted = energy_df.sort_values(by=["Date"])
    period_start = energy_df_sorted.iloc[0]['Date']
    period_end = energy_df_sorted.iloc[-1]['Date']
    print(period_start + " -> " + period_end)

