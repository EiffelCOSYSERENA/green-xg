from prometheus_client import start_http_server, Gauge
import requests
import time
import threading
import os
import logging

# Lire les Shelly depuis la variable d'env
devices_env = os.getenv("SHELLY_DEVICES", "")
logger = logging.getLogger(__name__)
SHELLY_DEVICES = {}

for entry in devices_env.split(","):
    if ":" in entry:
        name, ip = entry.split(":")
        SHELLY_DEVICES[name.strip()] = ip.strip()

# Création dynamique des métriques
metrics = {}
for name in SHELLY_DEVICES:
    metrics[name] = {
        "power": Gauge(f"{name}_power_watts", f"Puissance instantanée en Watts ({name})"),
        "energy": Gauge(f"{name}_energy_wh", f"Énergie cumulée en Wh ({name})"),
        "voltage": Gauge(f"{name}_voltage_v", f"Tension en Volts ({name})"),
        "current": Gauge(f"{name}_current_a", f"Courant en Ampères ({name})"),
    }

def fetch_metrics(name, ip):
    while True:
        try:
            r = requests.get(f"http://{ip}/rpc/Switch.GetStatus?id=0", timeout=2)
            data = r.json()

            power = data.get("apower", 0)
            energy = data.get("aenergy", {}).get("total", 0) / 60.0
            voltage = data.get("voltage", 0)
            current = data.get("current", 0)

            metrics[name]["power"].set(power)
            metrics[name]["energy"].set(energy)
            metrics[name]["voltage"].set(voltage)
            metrics[name]["current"].set(current)

            print(f"[{name}] OK Power={power}W | Energy={energy}Wh | V={voltage}V | I={current}A")
            logger.info(f"[{name}] OK Power={power}W | Energy={energy}Wh | V={voltage}V | I={current}A")
        except Exception as e:
            print(f"[{name}] Erreur récupération:", e)
            logger.error(f"[{name}] Erreur récupération:", e)
        time.sleep(1)

if __name__ == "__main__":
    start_http_server(9100, addr="0.0.0.0")
    logging.basicConfig(filename='shelly-exporter.log', level=logging.INFO)
    logger.info('Shelly devices exporter Started')        
    for name, ip in SHELLY_DEVICES.items():
        t = threading.Thread(target=fetch_metrics, args=(name, ip), daemon=True)
        t.start()
    while True:
        time.sleep(1)
