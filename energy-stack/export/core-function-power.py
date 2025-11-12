import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PROM_URL = "http://localhost:9090/api/v1/query_range"
STEP = 5  # secondes

PODS = [
    "oai-upf-6df59cc797-4tmqm",
    "oai-nrf-7cfb6f4847-7fnwq",
    "oai-ausf-fc586c7cc-kff9l",
    "f1-split2-mysql-54b8c94855-jhblq",
    "oai-smf-647b847c77-5kp54",
    "oai-udm-7c4dbf9db8-mp9l9",
    "oai-udr-7bb8b9c657-j5db8",
    "oai-amf-85555b75ff-nz2m6"
]

def fetch_pod_metric_sum(metric, pod_name, start, end, step=f"{STEP}s"):
    """Récupère et somme dram+package pour un pod donné."""
    query = f'{metric}{{pod_name="{pod_name}"}}'
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

    return df.sum(axis=1).sort_index()


def build_core_data(pods, start, end):
    watts_total = pd.Series(dtype=float)
    joules_total = pd.Series(dtype=float)

    for pod in pods:
        w = fetch_pod_metric_sum("kepler_pod_cpu_watts", pod, start, end)
        j = fetch_pod_metric_sum("kepler_pod_cpu_joules_total", pod, start, end)

        watts_total = watts_total.add(w, fill_value=0)
        joules_total = joules_total.add(j, fill_value=0)

    df = pd.concat([watts_total, joules_total], axis=1)
    df.columns = ["total_watts", "total_joules"]
    return df


def format_xaxis(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

def plot_core(df, filename_prefix):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # --- Power ---
    axes[0].plot(df.index, df["total_watts"], label="Total Power (W)", color="tab:red", linewidth=2)
    axes[0].set_ylabel("Watts")
    axes[0].set_ylim(0, 5)   # ✅ échelle fixe 0-5 W
    axes[0].set_title("Total 5G Core Functions Power Consumption")
    axes[0].legend(); axes[0].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[0])

    # --- Energy ---
    axes[1].plot(df.index, df["total_joules"], label="Total Energy (J)", color="black", linewidth=2)
    axes[1].set_ylabel("Joules"); axes[1].set_xlabel("Time")
    axes[1].set_title("Total 5G Core Functions Energy Consumption")
    axes[1].legend(); axes[1].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[1])

    # --- Titre global ---
    fig.suptitle("Total 5G Core Functions Power/Energy Consumption (Watts)", fontsize=16, fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f"{filename_prefix}.png", dpi=300)
    plt.savefig(f"{filename_prefix}.pdf")
    plt.close()
    print(f"✅ Figures sauvegardées : {filename_prefix}.png & {filename_prefix}.pdf")
    
def plot_core1(df, filename_prefix):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    axes[0].plot(df.index, df["total_watts"], label="Total Power (W)", color="tab:red", linewidth=2)
    axes[0].set_ylabel("Watts")
    axes[0].set_title("Total 5G Core Functions Power Consumption")
    axes[0].legend(); axes[0].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[0])

    axes[1].plot(df.index, df["total_joules"], label="Total Energy (J)", color="black", linewidth=2)
    axes[1].set_ylabel("Joules"); axes[1].set_xlabel("Time")
    axes[1].set_title("Total 5G Core Functions Energy Consumption")
    axes[1].legend(); axes[1].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[1])

    fig.suptitle("Total 5G Core Functions Power/Energy Consumption (Watts)", fontsize=16, fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f"{filename_prefix}.png", dpi=300)
    plt.savefig(f"{filename_prefix}.pdf")
    plt.close()
    print(f"✅ Figures sauvegardées : {filename_prefix}.png & {filename_prefix}.pdf")


if __name__ == "__main__":
    # Exemple : 20 minutes entre 09:00 et 09:20
    start = int(datetime.datetime(2025, 9, 29, 15, 15).timestamp())
    end   = int(datetime.datetime(2025, 9, 29, 15, 46).timestamp())

    df = build_core_data(PODS, start, end)
    df.to_csv("core_metrics-15h15.csv")
    plot_core(df, "core_fig-15h15")
    print("✅ Données exportées dans core_metrics.csv")
