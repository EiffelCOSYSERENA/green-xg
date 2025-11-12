import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt

PROM_URL = "http://localhost:9090/api/v1/query_range"

def fetch_metric_sum(metric, pod_name, start, end, step="5s"):
    """
    Récupère un métrique Prometheus et fait la somme des zones (dram + package).
    Retourne un pandas.Series indexé par datetime.
    """
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

    if not data:
        return pd.Series(dtype=float)

    # Construire DataFrame avec toutes les séries (dram, package, autres éventuelles)
    df = pd.DataFrame()
    for s in data:
        values = [(datetime.datetime.fromtimestamp(int(ts)), float(val)) for ts, val in s["values"]]
        serie = pd.Series({t: v for t, v in values})
        df[s["metric"].get("zone", "total")] = serie

    # Somme sur toutes les colonnes
    summed = df.sum(axis=1).sort_index()
    summed.name = metric
    return summed


def plot_metrics(pod_name, start, end):
    watts = fetch_metric_sum("kepler_pod_cpu_watts", pod_name, start, end)
    joules = fetch_metric_sum("kepler_pod_cpu_joules_total", pod_name, start, end)

    # Fusionner pour aligner les index
    df = pd.concat([watts, joules], axis=1)

    # Style scientifique
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(14, 8))

    # Courbe Watts
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df["kepler_pod_cpu_watts"],
             label="CPU Power (Watts)", color="tab:blue", linewidth=1.8)
    plt.ylabel("Watts", fontsize=12)
    plt.title(f"Pod {pod_name} – CPU Power & Energy",
              fontsize=14, fontweight="bold")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Courbe Joules
    plt.subplot(2, 1, 2)
    plt.plot(df.index, df["kepler_pod_cpu_joules_total"],
             label="CPU Energy (Joules)", color="tab:green", linewidth=1.8)
    plt.ylabel("Joules (cumulative)", fontsize=12)
    plt.xlabel("Time", fontsize=12)
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    plt.tight_layout()

    # Sauvegardes
    plt.savefig("pod_energy_curves.png", dpi=300)   # image haute résolution
    plt.savefig("pod_energy_curves.pdf")            # vectoriel (scientifique)
    print("✅ Figures sauvegardées : pod_energy_curves.png & pod_energy_curves.pdf")


if __name__ == "__main__":
    # Exemple : intervalle fixe (à adapter)
    start = 1758529800
    end   = 1758531900
    pod   = "oai-du-65f96b7b7b-hfv5s"

    plot_metrics(pod, start, end)
