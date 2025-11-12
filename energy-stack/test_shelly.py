from prometheus_client import start_http_server, Gauge
import requests
import time
import threading

# Adresse IP fixe de ton Shelly PlugS3
SHELLY1_IP = "192.168.18.126"

# Définition des métriques Prometheus
power_gauge = Gauge('shelly_power_watts', 'Puissance instantanée en Watts')
energy_gauge = Gauge('shelly_energy_wh', 'Énergie cumulée en Wh')
voltage_gauge = Gauge('shelly_voltage_v', 'Tension en Volts')
current_gauge = Gauge('shelly_current_a', 'Courant en Ampères')

def fetch_metrics():
    while True:
        try:
            # Exemple d'appel API Shelly PlugS3 (adapter si besoin)
            r = requests.get(f"http://{SHELLY1_IP}/rpc/Switch.GetStatus?id=0", timeout=1)
            data = r.json()

            # Extraction des métriques
            power = data.get("apower", 0)
            energy = data.get("aenergy", {}).get("total", 0) / 60.0  # Wh (si fourni en Ws)
            voltage = data.get("voltage", 0)
            current = data.get("current", 0)

            # Mise à jour des métriques
            power_gauge.set(power)
            energy_gauge.set(energy)
            voltage_gauge.set(voltage)
            current_gauge.set(current)

            print(f"[OK] Power={power}W | Energy={energy}Wh | Voltage={voltage}V | Current={current}A")

        except Exception as e:
            print("Erreur de récupération:", e)

        # Attente 1 seconde
        time.sleep(.1)

if __name__ == "__main__":
    # Lancer serveur HTTP pour Prometheus sur port 9100
    start_http_server(9110)

    # Thread de récupération des métriques
    t = threading.Thread(target=fetch_metrics)
    t.daemon = True
    t.start()

    # Boucle principale
    while True:
        time.sleep(1)
