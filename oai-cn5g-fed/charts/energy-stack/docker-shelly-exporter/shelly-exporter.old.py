from prometheus_client import start_http_server, Gauge
import requests
import time
import threading

# Adresse IP fixe de ton Shelly PlugS3
SHELLY1_IP = "192.168.18.126"
SHELLY2_IP = "192.168.18.127"
# Définition des métriques Prometheus
power_gauge1 = Gauge('shelly1_power_watts', 'Puissance instantanée en Watts')
energy_gauge1 = Gauge('shelly1_energy_wh', 'Énergie cumulée en Wh')
voltage_gauge1 = Gauge('shelly1_voltage_v', 'Tension en Volts')
current_gauge1 = Gauge('shelly1_current_a', 'Courant en Ampères')

power_gauge2 = Gauge('shelly2_power_watts', 'Puissance instantanée en Watts')
energy_gauge2 = Gauge('shelly2_energy_wh', 'Énergie cumulée en Wh')
voltage_gauge2 = Gauge('shelly2_voltage_v', 'Tension en Volts')
current_gauge2 = Gauge('shelly2_current_a', 'Courant en Ampères')
def fetch_metrics1():
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
            power_gauge1.set(power)
            energy_gauge1.set(energy)
            voltage_gauge1.set(voltage)
            current_gauge1.set(current)

            print(f"SHELLY 1: [OK] Power={power}W | Energy={energy}Wh | Voltage={voltage}V | Current={current}A")

        except Exception as e:
            print("Erreur de récupération:", e)

        # Attente 1 seconde
        time.sleep(.5)
def fetch_metrics2():
    while True:
        try:
            # Exemple d'appel API Shelly PlugS3 (adapter si besoin)
            r = requests.get(f"http://{SHELLY2_IP}/rpc/Switch.GetStatus?id=0", timeout=1)
            data = r.json()

            # Extraction des métriques
            power = data.get("apower", 0)
            energy = data.get("aenergy", {}).get("total", 0) / 60.0  # Wh (si fourni en Ws)
            voltage = data.get("voltage", 0)
            current = data.get("current", 0)

            # Mise à jour des métriques
            power_gauge2.set(power)
            energy_gauge2.set(energy)
            voltage_gauge2.set(voltage)
            current_gauge2.set(current)

            print(f"SHELLY 2: [OK] Power={power}W | Energy={energy}Wh | Voltage={voltage}V | Current={current}A")

        except Exception as e:
            print("Erreur de récupération:", e)

        # Attente 1 seconde
        time.sleep(.5)


if __name__ == "__main__":
    # Lancer serveur HTTP pour Prometheus sur port 9100
    start_http_server(9110)

    # Thread de récupération des métriques
    t1 = threading.Thread(target=fetch_metrics1)
    t2 = threading.Thread(target=fetch_metrics2)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    # Boucle principale
    while True:
        time.sleep(0.5)
