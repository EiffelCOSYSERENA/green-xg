import requests
import datetime
import pandas as pd

PROM_URL = "http://localhost:9090/api/v1/query_range"

def fetch_metric(metric, pod_name, start, end, step="5s"):
    query = f'{metric}{{pod_name="{pod_name}"}}'
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": step
    }
    r = requests.get(PROM_URL, params=params)
    r.raise_for_status()
    data = r.json()["data"]["result"]

    # Chaque série correspond à un label différent (ex: zone=dram, zone=package)
    series = {}
    for s in data:
        label = s["metric"].get("zone", "total")  # ex: dram, package
        values = [(datetime.datetime.fromtimestamp(int(ts)), float(val)) for ts, val in s["values"]]
        series[label] = pd.Series(
            [v for _, v in values],
            index=[t for t, _ in values],
            name=label
        )
    return pd.DataFrame(series)


if __name__ == "__main__":
    # Exemple plage horaire : même que ton curl
    start = 1758529800
    end   = 1758531900
    pod   = "oai-du-65f96b7b7b-hfv5s"

    df = fetch_metric("kepler_pod_cpu_watts", pod, start, end)
    print(df.head(20))   # afficher 20 premières lignes
    df.to_csv("watts.csv")   # export CSV
