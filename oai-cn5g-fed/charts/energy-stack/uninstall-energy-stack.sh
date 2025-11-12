
helm uninstall prometheus-stack -n monitoring

helm uninstall kepler -n kepler

helm uninstall f1-split -n green-xg
helm uninstall f1-split2 -n green-xg
# helm uninstall -n green-xg xapp-kpm-moni 

helm uninstall shelly-exporter -n monitoring
# kubectl delete -f grafana-dashboards.yaml

# kubectl delete -f storage.yaml
