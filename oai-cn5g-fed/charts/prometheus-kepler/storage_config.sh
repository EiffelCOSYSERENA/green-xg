# On each worker node where Prometheus/Grafana might run:
sudo mkdir -p /data/prometheus
sudo mkdir -p /mnt/grafana
sudo chown -R 1000:1000 /mnt/prometheus /mnt/grafana  # Set proper ownership