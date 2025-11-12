import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PROM_URL = "http://localhost:9090/api/v1/query_range"
STEP = 5  # secondes

def fetch_pod_metric_sum(metric, pod_regex, start, end, step=f"{STEP}s"):
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
    params = {"query": shelly_metric, "start": start, "end": end, "step": step}
    r = requests.get(PROM_URL, params=params)
    r.raise_for_status()
    data = r.json()["data"]["result"]

    if not data:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    values = [(datetime.datetime.fromtimestamp(int(ts)), float(val))
              for ts, val in data[0]["values"]]
    power = pd.Series({t: v for t, v in values}).sort_index()
    energy = (power * STEP).cumsum()
    energy.name = shelly_metric.replace("power_watts", "energy_joules")
    return power, energy


def build_cell_data(cu_regex, du_regex, shelly_metric, start, end):
    cu_watts = fetch_pod_metric_sum("kepler_pod_cpu_watts", cu_regex, start, end)
    cu_joules = fetch_pod_metric_sum("kepler_pod_cpu_joules_total", cu_regex, start, end)

    du_watts = fetch_pod_metric_sum("kepler_pod_cpu_watts", du_regex, start, end)
    du_joules = fetch_pod_metric_sum("kepler_pod_cpu_joules_total", du_regex, start, end)

    ru_watts, ru_joules = fetch_shelly_power(shelly_metric, start, end)

    df = pd.concat([cu_watts, du_watts, ru_watts, cu_joules, du_joules, ru_joules], axis=1)
    df.columns = ["cu_watts", "du_watts", "ru_watts",
                  "cu_joules", "du_joules", "ru_joules"]

    df["total_watts"] = df[["cu_watts", "du_watts", "ru_watts"]].sum(axis=1)
    df["total_joules"] = df[["cu_joules", "du_joules", "ru_joules"]].sum(axis=1)

    return df


def format_xaxis(ax):
    """Formatage lisible des dates sur l’axe x"""
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

def plot_cell(df, cell_name, filename_prefix):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(5, 1, figsize=(14, 18), sharex=True)

    # 1. CU Power
    axes[0].plot(df.index, df["cu_watts"], label="CU Power (W)", color="tab:blue")
    axes[0].set_ylabel("Watts"); axes[0].set_title(f"{cell_name} CU Power Consumption")
    axes[0].set_ylim(0, 1.5)   # ✅ échelle fixe
    axes[0].legend(); axes[0].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[0])

    # 2. DU Power
    axes[1].plot(df.index, df["du_watts"], label="DU Power (W)", color="tab:orange")
    axes[1].set_ylabel("Watts"); axes[1].set_title(f"{cell_name} DU Power Consumption")
    axes[1].set_ylim(0, 25)    # ✅ échelle fixe
    axes[1].legend(); axes[1].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[1])

    # 3. RU Power
    axes[2].plot(df.index, df["ru_watts"], label="RU Power (W)", color="tab:green")
    axes[2].set_ylabel("Watts"); axes[2].set_title(f"{cell_name} RU Power Consumption")
    axes[2].set_ylim(0, 60)    # ✅ échelle fixe
    axes[2].legend(); axes[2].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[2])

    # 4. Total Power
    axes[3].plot(df.index, df["total_watts"], label="Total Power (W)", color="black", linewidth=2)
    axes[3].set_ylabel("Watts"); axes[3].set_title(f"{cell_name} Total Power Consumption")
    axes[3].set_ylim(0, 80)    # ✅ échelle fixe
    axes[3].legend(); axes[3].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[3])

    # 5. Total Energy
    axes[4].plot(df.index, df["total_joules"], label="Total Energy (J)", color="black", linewidth=2)
    axes[4].set_ylabel("Joules"); axes[4].set_xlabel("Time")
    axes[4].set_title(f"{cell_name} Total Energy Consumption")
    axes[4].legend(); axes[4].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[4])

    plt.tight_layout()
    plt.savefig(f"{filename_prefix}.png", dpi=300)
    plt.savefig(f"{filename_prefix}.pdf")
    plt.close()

def plot_cell1(df, cell_name, filename_prefix):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(5, 1, figsize=(14, 18), sharex=True)

    axes[0].plot(df.index, df["cu_watts"], label="CU Power (W)", color="tab:blue")
    axes[0].set_ylabel("Watts"); axes[0].set_title(f"{cell_name} CU Power Consumption")
    axes[0].legend(); axes[0].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[0])

    axes[1].plot(df.index, df["du_watts"], label="DU Power (W)", color="tab:orange")
    axes[1].set_ylabel("Watts"); axes[1].set_title(f"{cell_name} DU Power Consumption")
    axes[1].legend(); axes[1].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[1])

    axes[2].plot(df.index, df["ru_watts"], label="RU Power (W)", color="tab:green")
    axes[2].set_ylabel("Watts"); axes[2].set_title(f"{cell_name} RU Power Consumption")
    axes[2].legend(); axes[2].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[2])

    axes[3].plot(df.index, df["total_watts"], label="Total Power (W)", color="black", linewidth=2)
    axes[3].set_ylabel("Watts"); axes[3].set_title(f"{cell_name} Total Power Consumption")
    axes[3].legend(); axes[3].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[3])

    axes[4].plot(df.index, df["total_joules"], label="Total Energy (J)", color="black", linewidth=2)
    axes[4].set_ylabel("Joules"); axes[4].set_xlabel("Time")
    axes[4].set_title(f"{cell_name} Total Energy Consumption")
    axes[4].legend(); axes[4].grid(True, linestyle="--", linewidth=0.5)
    format_xaxis(axes[4])

    plt.tight_layout()
    plt.savefig(f"{filename_prefix}.png", dpi=300)
    plt.savefig(f"{filename_prefix}.pdf")
    plt.close()

def plot_comparison(df1, df2):
    plt.style.use("seaborn-v0_8-whitegrid")

    # 🔹 Taille globale des polices
    plt.rcParams.update({
        "font.size": 13,
        "axes.titlesize": 15,
        "axes.labelsize": 14,
        "legend.fontsize": 12,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
    })

    # Vérifications avant de tracer
    if df1.empty or df2.empty:
        print("⚠️ Attention : au moins un des DataFrames est vide. Vérifie la période ou les métriques Prometheus.")
        print(f"  ➤ df1 vide : {df1.empty}, df2 vide : {df2.empty}")
        return

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # --- Power ---
    axes[0].plot(df1.index, df1["total_watts"], label="Cell 1 Total Power (W)", color="tab:blue", linewidth=2)
    axes[0].plot(df2.index, df2["total_watts"], label="Cell 2 Total Power (W)", color="tab:orange", linewidth=2)
    axes[0].set_ylabel("Power (Watts)", fontsize=14)
    axes[0].set_title("Comparison: Total Power Consumption", fontsize=15, fontweight="bold")
    axes[0].legend(loc="upper right")
    axes[0].grid(True, linestyle="--", linewidth=0.6)
    format_xaxis(axes[0])

    # --- Energy ---
    axes[1].plot(df1.index, df1["total_joules"], label="Cell 1 Total Energy (J)", color="tab:blue", linewidth=2)
    axes[1].plot(df2.index, df2["total_joules"], label="Cell 2 Total Energy (J)", color="tab:orange", linewidth=2)
    axes[1].set_ylabel("Energy (Joules)", fontsize=14)
    axes[1].set_xlabel("Time", fontsize=14)
    axes[1].set_title("Comparison: Total Energy Consumption", fontsize=15, fontweight="bold")
    axes[1].legend(loc="upper left")
    axes[1].grid(True, linestyle="--", linewidth=0.6)
    format_xaxis(axes[1])

    # --- Annotations finales (protégées) ---
    try:
        if not df1["total_joules"].empty:
            e1 = df1["total_joules"].iloc[-1]
            t1 = df1.index[-1]
            t_str1 = t1.strftime("%Y-%m-%d %H:%M:%S")
            axes[1].annotate(f"{e1:.0f} J\n{t_str1}", xy=(t1, e1), xytext=(10, 0),
                             textcoords="offset points", color="tab:blue", fontsize=12,
                             arrowprops=dict(arrowstyle="->", color="tab:blue", lw=1.2))

        if not df2["total_joules"].empty:
            e2 = df2["total_joules"].iloc[-1]
            t2 = df2.index[-1]
            t_str2 = t2.strftime("%Y-%m-%d %H:%M:%S")
            axes[1].annotate(f"{e2:.0f} J\n{t_str2}", xy=(t2, e2), xytext=(10, -30),
                             textcoords="offset points", color="tab:orange", fontsize=12,
                             arrowprops=dict(arrowstyle="->", color="tab:orange", lw=1.2))
    except Exception as e:
        print(f"⚠️ Erreur lors des annotations : {e}")

    # --- Titre global ---
    fig.suptitle("Comparison of Cell 1 & Cell 2 Total Power/Energy Consumption",
                 fontsize=17, fontweight="bold", y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("comparison_cells-15h15.png", dpi=300)
    plt.savefig("comparison_cells-15h15.pdf")
    plt.close()

    print("✅ Figures sauvegardées : comparison_cells-15h15.png & comparison_cells-15h15.pdf")


def dplot_comparison(df1, df2):
    plt.style.use("seaborn-v0_8-whitegrid")

    # 🔹 Taille globale des polices
    plt.rcParams.update({
        "font.size": 13,              # taille de base
        "axes.titlesize": 15,         # titres des sous-graphes
        "axes.labelsize": 14,         # labels d’axes
        "legend.fontsize": 12,        # légendes
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
    })

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # --- Power ---
    axes[0].plot(df1.index, df1["total_watts"], label="Cell 1 Total Power (W)", color="tab:blue", linewidth=2)
    axes[0].plot(df2.index, df2["total_watts"], label="Cell 2 Total Power (W)", color="tab:orange", linewidth=2)
    axes[0].set_ylabel("Power (Watts)", fontsize=14)
    axes[0].set_title("Comparison: Total Power Consumption", fontsize=15, fontweight="bold")
    axes[0].legend(loc="upper right")
    axes[0].grid(True, linestyle="--", linewidth=0.6)
    format_xaxis(axes[0])

    # --- Energy ---
    axes[1].plot(df1.index, df1["total_joules"], label="Cell 1 Total Energy (J)", color="tab:blue", linewidth=2)
    axes[1].plot(df2.index, df2["total_joules"], label="Cell 2 Total Energy (J)", color="tab:orange", linewidth=2)
    axes[1].set_ylabel("Energy (Joules)", fontsize=14)
    axes[1].set_xlabel("Time", fontsize=14)
    axes[1].set_title("Comparison: Total Energy Consumption", fontsize=15, fontweight="bold")
    axes[1].legend(loc="upper left")
    axes[1].grid(True, linestyle="--", linewidth=0.6)
    format_xaxis(axes[1])

    # --- Annotations finales ---
    e1 = df1["total_joules"].iloc[-1]
    e2 = df2["total_joules"].iloc[-1]
    t_end = df1.index[-1] if len(df1) > len(df2) else df2.index[-1]
    t_str = t_end.strftime("%Y-%m-%d %H:%M:%S")

    axes[1].annotate(f"{e1:.0f} J\n{t_str}", xy=(t_end, e1), xytext=(10, 0),
                     textcoords="offset points", color="tab:blue", fontsize=12,
                     arrowprops=dict(arrowstyle="->", color="tab:blue", lw=1.2))
    axes[1].annotate(f"{e2:.0f} J\n{t_str}", xy=(t_end, e2), xytext=(10, -30),
                     textcoords="offset points", color="tab:orange", fontsize=12,
                     arrowprops=dict(arrowstyle="->", color="tab:orange", lw=1.2))

    # --- Titre global ---
    fig.suptitle("Comparison of Cell 1 & Cell 2 Total Power/Energy Consumption",
                 fontsize=17, fontweight="bold", y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("comparison_cells-15h15fontok.png", dpi=300)
    plt.savefig("comparison_cells-15h15fontok.pdf")
    plt.close()

    print("✅ Figures sauvegardées : comparison_cells-15h15fontok.png & comparison_cells-15h15.pdf")


if __name__ == "__main__":
    start = int(datetime.datetime(2025, 9, 29, 15, 15).timestamp())
    end   = int(datetime.datetime(2025, 9, 29, 15, 46).timestamp())

    df1 = build_cell_data(
        cu_regex="oai-cu-75bdd66ddf-625t2",
        du_regex="oai-du1-5d6cb5b76b-vh44m",
        shelly_metric="shelly1_power_watts",
        start=start, end=end
    )
    plot_cell(df1, "Cell 1", "cell1_fig-15h15")

    df2 = build_cell_data(
        cu_regex="oai-cu-75bdd66ddf-625t2",
        du_regex="oai-du2-6d9598fc9d-89ng4",
        shelly_metric="shelly2_power_watts",
        start=start, end=end
    )
    plot_cell(df2, "Cell 2", "cell2_fig-15h15")

    merged = pd.concat([df1.add_prefix("cell1_"), df2.add_prefix("cell2_")], axis=1)
    merged.to_csv("cells_metrics-15h15.csv")

    plot_comparison(df1, df2)
