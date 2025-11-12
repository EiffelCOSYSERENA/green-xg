import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt

PROM_URL = "http://localhost:9090/api/v1/query_range"
STEP = 5  # secondes

def fetch_pod_metric_sum(metric, pod_regex, start, end, step=f"{STEP}s"):
    """Récupère un métrique Prometheus (Kepler), filtre par pod regex,
    somme les zones (dram+package) et tous les pods correspondants."""
    query = f'{metric}{{pod_name=~"{pod_regex}"}}'
    params = {"query": query, "start": start, "end": end, "step": step}
    r = requests.get(PROM_URL, params=params)
    r.raise_for_status()
    data = r.json()["data"]["result"]

    if not data:
        return pd.Series(dtype=float)

    df = pd.DataFrame()
    for s in data:
        values = [(datetime.datetime.fromtimestamp(int(ts)), float(val))
                  for ts, val in s["values"]]
        serie = pd.Series({t: v for t, v in values})
        df[s["metric"].get("zone", "total")] = serie

    summed = df.sum(axis=1).sort_index()
    summed.name = metric
    return summed


def fetch_shelly_power(shelly_metric, start, end, step=f"{STEP}s"):
    """Récupère la puissance Shelly (W) et calcule l'énergie cumulée (J)."""
    params = {"query": shelly_metric, "start": start, "end": end, "step": step}
    r = requests.get(PROM_URL, params=params)
    r.raise_for_status()
    data = r.json()["data"]["result"]

    if not data:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    values = [(datetime.datetime.fromtimestamp(int(ts)), float(val))
              for ts, val in data[0]["values"]]
    power = pd.Series({t: v for t, v in values}).sort_index()
    # Énergie cumulée = somme(P * Δt)
    energy = (power * STEP).cumsum()
    energy.name = shelly_metric.replace("power_watts", "energy_joules")
    return power, energy


def build_cell_data(cu_regex, du_regex, shelly_metric, start, end):
    # CU
    cu_watts = fetch_pod_metric_sum("kepler_pod_cpu_watts", cu_regex, start, end)
    cu_joules = fetch_pod_metric_sum("kepler_pod_cpu_joules_total", cu_regex, start, end)

    # DU
    du_watts = fetch_pod_metric_sum("kepler_pod_cpu_watts", du_regex, start, end)
    du_joules = fetch_pod_metric_sum("kepler_pod_cpu_joules_total", du_regex, start, end)

    # RU (Shelly)
    ru_watts, ru_joules = fetch_shelly_power(shelly_metric, start, end)

    # Fusion dans un DataFrame
    df = pd.concat([cu_watts, du_watts, ru_watts, cu_joules, du_joules, ru_joules], axis=1)
    df.columns = ["cu_watts", "du_watts", "ru_watts",
                  "cu_joules", "du_joules", "ru_joules"]

    # Totaux
    df["total_watts"] = df[["cu_watts", "du_watts", "ru_watts"]].sum(axis=1)
    df["total_joules"] = df[["cu_joules", "du_joules", "ru_joules"]].sum(axis=1)

    return df


def plot_cell(df, cell_name, filename_prefix):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(5, 1, figsize=(14, 18), sharex=True)

    # 1. CU Power
    axes[0].plot(df.index, df["cu_watts"], label="CU Power (W)", color="tab:blue")
    axes[0].set_ylabel("Watts"); axes[0].set_title(f"{cell_name} CU Power Consumption")
    axes[0].legend(); axes[0].grid(True, linestyle="--", linewidth=0.5)

    # 2. DU Power
    axes[1].plot(df.index, df["du_watts"], label="DU Power (W)", color="tab:orange")
    axes[1].set_ylabel("Watts"); axes[1].set_title(f"{cell_name} DU Power Consumption")
    axes[1].legend(); axes[1].grid(True, linestyle="--", linewidth=0.5)

    # 3. RU Power
    axes[2].plot(df.index, df["ru_watts"], label="RU Power (W)", color="tab:green")
    axes[2].set_ylabel("Watts"); axes[2].set_title(f"{cell_name} RU Power Consumption")
    axes[2].legend(); axes[2].grid(True, linestyle="--", linewidth=0.5)

    # 4. Total Power
    axes[3].plot(df.index, df["total_watts"], label="Total Power (W)", color="black", linewidth=2)
    axes[3].set_ylabel("Watts"); axes[3].set_title(f"{cell_name} Total Power Consumption")
    axes[3].legend(); axes[3].grid(True, linestyle="--", linewidth=0.5)

    # 5. Total Energy
    axes[4].plot(df.index, df["total_joules"], label="Total Energy (J)", color="black", linewidth=2)
    axes[4].set_ylabel("Joules"); axes[4].set_xlabel("Time")
    axes[4].set_title(f"{cell_name} Total Energy Consumption")
    axes[4].legend(); axes[4].grid(True, linestyle="--", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(f"{filename_prefix}.png", dpi=300)
    plt.savefig(f"{filename_prefix}.pdf")
    plt.close()
    print(f"✅ Figure sauvegardée : {filename_prefix}.png & {filename_prefix}.pdf")


def plot_comparison(df1, df2):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # --- Total Power ---
    axes[0].plot(df1.index, df1["total_watts"], label="Cell 1 Total Power (W)", color="tab:blue")
    axes[0].plot(df2.index, df2["total_watts"], label="Cell 2 Total Power (W)", color="tab:orange")
    axes[0].set_ylabel("Watts"); axes[0].set_title("Comparison: Total Power Consumption")
    axes[0].legend(); axes[0].grid(True, linestyle="--", linewidth=0.5)

    # --- Total Energy ---
    axes[1].plot(df1.index, df1["total_joules"], label="Cell 1 Total Energy (J)", color="tab:blue")
    axes[1].plot(df2.index, df2["total_joules"], label="Cell 2 Total Energy (J)", color="tab:orange")
    axes[1].set_ylabel("Joules"); axes[1].set_xlabel("Time")
    axes[1].set_title("Comparison: Total Energy Consumption")
    axes[1].legend(); axes[1].grid(True, linestyle="--", linewidth=0.5)

    plt.tight_layout()
    plt.savefig("comparison_cells.png", dpi=300)
    plt.savefig("comparison_cells.pdf")
    plt.close()
    print("✅ Figure sauvegardée : comparison_cells.png & comparison_cells.pdf")


if __name__ == "__main__":
    # Paramètres (à adapter)
    start = int(datetime.datetime(2025, 9, 29, 8, 48).timestamp())
    end   = int(datetime.datetime(2025, 9, 29, 9, 48).timestamp())

    # Cell 1
    df1 = build_cell_data(
        cu_regex="oai-cu-75bdd66ddf-625t2",
        du_regex="oai-du1-68694b85b7-7fg6v",
        shelly_metric="shelly1_power_watts",
        start=start, end=end
    )
    df1.to_csv("cell1_metrics.csv")
    plot_cell(df1, "Cell 1", "cell1_fig")

    # Cell 2
    df2 = build_cell_data(
        cu_regex="oai-cu-75bdd66ddf-625t2",
        du_regex="oai-du2-6d9598fc9d-.+",  # regex correct
        shelly_metric="shelly2_power_watts",
        start=start, end=end
    )
    df2.to_csv("cell2_metrics.csv")
    plot_cell(df2, "Cell 2", "cell2_fig")

    # Figure comparative
    plot_comparison(df1, df2)
