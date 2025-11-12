#!/bin/bash

# deploy-with-network.sh - Déploiement Prometheus Stack avec accès réseau direct

set -e

# Variables de configuration
NAMESPACE="monitoring"
RELEASE_NAME="prometheus"
NODE_IP=""

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Fonction pour obtenir l'IP du nœud
get_node_ip() {
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
    if [ -z "$NODE_IP" ]; then
        NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
    fi
    echo "$NODE_IP"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl n'est pas installé"
        exit 1
    fi
    
    # Vérifier helm
    if ! command -v helm &> /dev/null; then
        log_error "helm n'est pas installé"
        exit 1
    fi
    
    # Vérifier la connexion au cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Impossible de se connecter au cluster Kubernetes"
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# Fonction principale de déploiement
deploy_prometheus_stack() {
    log_info "🚀 Démarrage du déploiement Prometheus Stack..."
    
    # 1. Créer le namespace
    log_info "📁 Création du namespace $NAMESPACE..."
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # 2. Ajouter et mettre à jour les repositories Helm
    log_info "📦 Configuration des repositories Helm..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # 3. Déployer l'Ingress Controller si nécessaire
    log_info "🌐 Vérification de l'Ingress Controller..."
    if ! kubectl get ingressclass nginx &> /dev/null; then
        log_info "Installation d'Ingress NGINX..."
        helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
            --namespace ingress-nginx \
            --create-namespace \
            --set controller.service.type=NodePort \
            --set controller.service.nodePorts.http=30080 \
            --set controller.service.nodePorts.https=30443
        
        log_info "Attente de l'Ingress Controller..."
        kubectl wait --namespace ingress-nginx \
            --for=condition=ready pod \
            --selector=app.kubernetes.io/component=controller \
            --timeout=300s
    else
        log_success "Ingress Controller déjà installé"
    fi
    

    # 4. Appliquer les ressources supplémentaires
    log_info "📄 Création des ressources supplémentaires..."
    kubectl apply -f additional-resources.yaml
    
    # 5. Attendre que le PVC soit disponible
    log_info "⏳ Attente du PVC..."
    kubectl wait --for=condition=Bound pvc/sqlite-pvc -n $NAMESPACE --timeout=120s
    
    # 6. Déployer Prometheus Stack
    log_info "⚡ Déploiement de Prometheus Stack..."
    helm upgrade --install $RELEASE_NAME prometheus-community/kube-prometheus-stack \
        --namespace $NAMESPACE \
        --values custom-values.yaml \
        --wait \
        --timeout 15m
    cd ~/kepler
    helm install kepler manifests/helm/kepler/ -n kepler  --values  manifests/helm/kepler/values.yaml
    # 7. Attendre que tous les pods soient prêts
    log_info "⏳ Attente des pods..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n $NAMESPACE --timeout=300s
    
    log_success "Déploiement terminé avec succès !"
}




# Fonction pour afficher les informations d'accès
show_access_info() {
    local node_ip=$(get_node_ip)
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 DÉPLOIEMENT RÉUSSI - INFORMATIONS D'ACCÈS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    log_success "📊 GRAFANA :"
    echo "   • NodePort: http://$node_ip:30000"
    if kubectl get ingress -n $NAMESPACE &> /dev/null; then
        echo "   • Ingress: http://grafana.local (ajoutez dans /etc/hosts: $node_ip grafana.local)"
        echo "   • Ingress via NodePort: http://$node_ip:30080"
    fi
    echo "   • Identifiants: admin / SecurePassword123!"
    echo ""
    
    log_success "🔍 PROMETHEUS :"
    echo "   • NodePort: http://$node_ip:30001"
    echo ""
    
    log_success "🚨 ALERTMANAGER :"
    echo "   • NodePort: http://$node_ip:30002"
    echo ""
    
    log_info "📋 COMMANDES UTILES :"
    echo "   • Pods: kubectl get pods -n $NAMESPACE"
    echo "   • Services: kubectl get svc -n $NAMESPACE"
    echo "   • Logs Grafana: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=grafana"
    echo "   • Redémarrer Grafana: kubectl rollout restart deployment -n $NAMESPACE prometheus-grafana"
    echo ""
    
    if [ -n "$(kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)" ]; then
        log_warning "💡 Pour utiliser l'Ingress, ajoutez dans votre /etc/hosts :"
        echo "   echo '$node_ip grafana.local' | sudo tee -a /etc/hosts"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Fonction pour vérifier l'état du déploiement
check_deployment_health() {
    log_info "🔍 Vérification de l'état du déploiement..."
    
    # Vérifier les pods
    local failed_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
    if [ "$failed_pods" -gt 0 ]; then
        log_warning "$failed_pods pod(s) ne sont pas en état Running"
        kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running
    else
        log_success "Tous les pods sont en état Running"
    fi
    
    # Vérifier les services
    local services_count=$(kubectl get svc -n $NAMESPACE --no-headers | wc -l)
    log_success "$services_count service(s) créé(s)"
    
    # Test de connectivité Grafana
    local node_ip=$(get_node_ip)
    log_info "Test de connectivité Grafana..."
    if timeout 10 bash -c "</dev/tcp/$node_ip/30000" &> /dev/null; then
        log_success "Grafana est accessible sur $node_ip:30000"
    else
        log_warning "Grafana pourrait ne pas être encore accessible (démarrage en cours...)"
    fi
}

# Fonction de nettoyage (optionnelle)
cleanup() {
    if [ "$1" = "--cleanup" ]; then
        log_warning "🗑️  Nettoyage du déploiement..."
        helm uninstall $RELEASE_NAME -n $NAMESPACE
        kubectl delete namespace $NAMESPACE
        log_success "Nettoyage terminé"
        exit 0
    fi
}

# Script principal
main() {
    # Gestion des arguments
    cleanup "$1"
    
    # Déploiement
    check_prerequisites
    deploy_prometheus_stack
    check_deployment_health
    show_access_info
    
    log_success "🎯 Votre stack de monitoring est prête à l'emploi !"
}

# Exécution du script
main "$@"