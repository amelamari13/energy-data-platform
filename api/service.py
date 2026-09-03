from api.repository import fetch_regions, fetch_region_summary


def get_regions():
    return fetch_regions()


def get_region_summary(region, start_date, end_date):
    return fetch_region_summary(region, start_date, end_date)


def get_region_anomalies(region, start_date, end_date):
    data = fetch_region_summary(region, start_date, end_date)

    if len(data) < 2:
        return []

    consumptions = [day["Average_Consumption"] for day in data]
    mean = sum(consumptions) / len(consumptions)
    std_dev = (sum((x - mean) ** 2 for x in consumptions) / len(consumptions)) ** 0.5

    anomalies = []
    for day in data:
        if abs(day["Average_Consumption"] - mean) > 2 * std_dev:
            anomalies.append(day)

    return anomalies


def compare_regions(start_date, end_date):
    regions = fetch_regions()
    comparison = []

    for region in regions:
        data = fetch_region_summary(region, start_date, end_date)
        if not data:
            continue
        avg_share = sum(d["Average_Renewable_Share"] for d in data) / len(data)
        comparison.append({"region": region, "average_renewable_share": avg_share})

    return sorted(comparison, key=lambda r: r["average_renewable_share"], reverse=True)


def get_consumption_trend(region, start_date, end_date):
    data = fetch_region_summary(region, start_date, end_date)
    if len(data) < 2:
        return "insufficient_data"

    first_half = data[: len(data) // 2]
    second_half = data[len(data) // 2 :]

    avg_first = sum(d["Average_Consumption"] for d in first_half) / len(first_half)
    avg_second = sum(d["Average_Consumption"] for d in second_half) / len(second_half)

    if avg_second > avg_first * 1.05:
        return "increasing"
    elif avg_second < avg_first * 0.95:
        return "decreasing"
    return "stable"