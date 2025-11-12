#This line must be run once. Please change the data folder in the storage.yaml file.
# kubectl apply -f storage.yaml

# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# helm repo update

# kubectl apply -f grafana-dashboards.yaml
# cd ~/oai-cn5g-fed/charts/oai-5g-ric
# helm -n green-xg install oai-ric .
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f values.yaml

cd ~/green-xg/oai-cn5g-fed/charts/e2e_scenarios/case2
helm dependency build
helm -n green-xg install f1-split .

# sleep 30s

# cd ~/oai-cn5g-fed/charts/xapp-kpm-moni
#helm -n green-xg install xapp-kpm-moni .

#cd ~/green-xg/oai-cn5g-fed/charts/energy-stack

cd ~/kepler

helm install kepler manifests/helm/kepler/ -n kepler  --values  manifests/helm/kepler/values.yaml

cd 

cd ~/green-xg/oai-cn5g-fed/charts/energy-stack/shelly-exporter
helm -n monitoring install shelly-exporter . 

kubectl port-forward svc/prometheus-stack-kube-prom-prometheus 9090 -n monitoring &
kubectl port-forward svc/kepler 28282 -n kepler &

# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update

