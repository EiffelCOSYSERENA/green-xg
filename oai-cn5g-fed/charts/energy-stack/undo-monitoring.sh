helm uninstall -n kepler kepler

helm uninstall -n monitoring prometheus-stack

kubectl delete -f prometheus-stack-persistent-volume.yaml 
