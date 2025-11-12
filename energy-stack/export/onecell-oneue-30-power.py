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


def fetch_shelly_metric(metric, start, end, step="5s"):
    """
    Récupère une métrique Shelly (sans pod_name, structure différente).
    Retourne un pandas.Series indexé par datetime.
    """
    query = metric
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

    # Prendre la première série (ou faire la somme si plusieurs)
    all_series = []
    for s in data:
        values = [(datetime.datetime.fromtimestamp(int(ts)), float(val)) for ts, val in s["values"]]
        serie = pd.Series({t: v for t, v in values})
        all_series.append(serie)
    
    if len(all_series) == 1:
        result = all_series[0]
    else:
        # Combiner plusieurs séries si nécessaire
        df_temp = pd.concat(all_series, axis=1)
        result = df_temp.sum(axis=1)
    
    result.name = metric
    return result.sort_index()


def plot_metrics(pod_name, start, end):
    # Récupération des métriques
    kepler_watts = fetch_metric_sum("kepler_pod_cpu_watts", pod_name, start, end)
    kepler_joules = fetch_metric_sum("kepler_pod_cpu_joules_total", pod_name, start, end)
    shelly_watts = fetch_shelly_metric("shelly1_power_watts", start, end)

    # Fusionner pour aligner les index
    df = pd.concat([kepler_watts, kepler_joules, shelly_watts], axis=1)
    
    # Calculer la somme Kepler + Shelly
    df["total_power"] = df["kepler_pod_cpu_watts"] + df["shelly1_power_watts"]

    # Style scientifique
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(16, 12))

    # 1. Courbe Kepler CPU Watts (échelle 0-20W)
    plt.subplot(4, 1, 1)
    plt.plot(df.index, df["kepler_pod_cpu_watts"],
             label="CPU Power (Kepler)", color="tab:blue", linewidth=1.8)
    plt.ylabel("Watts", fontsize=12)
    plt.ylim(0, 20)  # Échelle fixée à 0-20W
    plt.title(f"Pod {pod_name} — Monitoring Énergétique Complet",
              fontsize=14, fontweight="bold")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # 2. Courbe Shelly Power Watts (échelle 0-55W)
    plt.subplot(4, 1, 2)
    plt.plot(df.index, df["shelly1_power_watts"],
             label="Shelly Power", color="tab:orange", linewidth=1.8)
    plt.ylabel("Watts", fontsize=12)
    plt.ylim(0, 55)  # Échelle fixée à 0-55W
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # 3. Courbe Somme Kepler + Shelly
    plt.subplot(4, 1, 3)
    plt.plot(df.index, df["total_power"],
             label="Total Power (Kepler + Shelly)", color="tab:red", linewidth=1.8)
    plt.ylabel("Watts", fontsize=12)
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # 4. Courbe Kepler Joules (cumulative)
    plt.subplot(4, 1, 4)
    plt.plot(df.index, df["kepler_pod_cpu_joules_total"],
             label="CPU Energy (Joules)", color="tab:green", linewidth=1.8)
    plt.ylabel("Joules (cumulative)", fontsize=12)
    plt.xlabel("Time", fontsize=12)
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    plt.tight_layout()

    # Sauvegardes
    plt.savefig("pod_energy_curves_complete.png", dpi=300)   # image haute résolution
    plt.savefig("pod_energy_curves_complete.pdf")           # vectoriel (scientifique)
    print("✅ Figures sauvegardées : pod_energy_curves_complete.png & pod_energy_curves_complete.pdf")

    # Afficher quelques statistiques
    print(f"\n📊 Statistiques sur la période :")
    print(f"Kepler CPU - Moyenne: {df['kepler_pod_cpu_watts'].mean():.2f}W, Max: {df['kepler_pod_cpu_watts'].max():.2f}W")
    print(f"Shelly Power - Moyenne: {df['shelly1_power_watts'].mean():.2f}W, Max: {df['shelly1_power_watts'].max():.2f}W")
    print(f"Puissance totale - Moyenne: {df['total_power'].mean():.2f}W, Max: {df['total_power'].max():.2f}W")


if __name__ == "__main__":
    # Exemple : intervalle fixe (à adapter)
    start = 1758529720
    end   = 1758531980
    pod   = "oai-du-65f96b7b7b-hfv5s"

    plot_metrics(pod, start, end)