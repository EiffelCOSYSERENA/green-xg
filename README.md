# Green-xG : an Open Federated Tested for Energy-Aware 5G/6G Networks
<div align="center">

<p align="center">
  <img width="200" height="124" alt="green-xg-logo" src="https://github.com/user-attachments/assets/4b5c07e3-4645-45cf-a42d-3bb5d30c87f1" />
</p>

[![License](https://img.shields.io/badge/license-Open%20Source-blue.svg)](https://github.com/EiffelCOSYSERENA/green-xg)
[![DOI](https://img.shields.io/badge/DOI-Zenodo-orange.svg)](https://zenodo.org)

*Real-time observability and joint optimization of power consumption, QoS, and carbon footprint*

</div>

---

## 🎯 Overview

Green xG is an open-source experimental testbed built on **six energy-first principles** and structured around three core missions:

- **🔍 Observe**: Measure energy and QoS without blind spots
- **🧪 Experiment**: Test real-world workloads with dynamic placement
- **✅ Validate**: Ensure reproducible and citable results

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  🔬 Telemetry Pipeline                      │
│            Prometheus • Grafana • DOI/Zenodo                │
├─────────────────────────────────────────────────────────────┤
│                  ☁️ Cloud-Native Plane                      │
│      Kubernetes • Docker • RIC • CRIU • MetalLB             │
├─────────────────────────────────────────────────────────────┤
│                  📡 Physical Substrate                      │
│   Multi-site (3 campuses) • PTP Clock • Power Sensors      │
│        OAI RAN • Open5GS • USRP • Mobile Robots            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Components

### 📡 Radio Access Network (RAN)

| Component | Technology | Purpose |
|-----------|------------|---------|
| **OpenAirInterface** | Open-source RAN | Modifiable radio stack with power probes |
| **USRP** | Software-defined radio | Synthetic UEs for deterministic traffic |
| **FlexRIC Near-RT RIC** | O-RAN controller | Sub-second scheduling adjustments |

### 🌐 5G Core Network

| Component | Technology | Purpose |
|-----------|------------|---------|
| **OpenAirInterface Core Network** | OAI 5GC | Containerized core functions (AMF, SMF, UPF, UDM, AUSF) |
| **Open5GS** | Open-source 5GC | Containerized core functions (AMF, SMF, UPF, UDM, AUSF) |
| **Non-RT RIC** | O-RAN controller | Long-horizon policy management |

### ⚡ Multi-Level Power Sensing

| Level | Tool | Precision | Description |
|-------|------|-----------|-------------|
| **Rack** | Shelly Plug | kHz-class | Aggregate radio & server consumption |
| **Workload** | Kepler | ~100ms | Per-container power attribution |
| **Device** | FuelGauge/INA219 | ~1s | End-user equipment monitoring |

### 🤖 Mobility Platforms

| Platform | Speed | Use Case | Positioning |
|----------|-------|----------|-------------|
| **Indoor Robots** | ~0.26 m/s | Human mobility | UWB (m to dm accuracy) |
| **Vehicular Robots** | Up to 70 km/h | High-speed scenarios | RTK-GNSS (sub-dm accuracy) |

### ⏱️ Synchronization & Timing

| Component | Precision | Purpose |
|-----------|-----------|---------|
| **IEEE-1588 PTP** | Microsecond | Unified timebase across all sites |
| **Hardware Grandmaster** | Sub-μs | Reference clock distribution |

### ☁️ Cloud-Native Stack

| Component | Role | Key Feature |
|-----------|------|-------------|
| **Docker** | Containerization | Reproducible packaging |
| **Kubernetes** | Orchestration | Automated placement & recovery |
| **CRIU** | Live migration | Function relocation in seconds |
| **MetalLB** | Load balancing | Seamless IP re-announcement |

### 📊 Observability Pipeline

| Component | Function | Cadence |
|-----------|----------|---------|
| **Prometheus** | Time-series collection | 1-second scraping |
| **Grafana** | Visualization | Unified timeline dashboard |
| **CI/CD** | Artifact generation | Automated bundle creation |
| **Zenodo** | Archival | DOI-based citation |

### 🌍 Geographic Infrastructure

| Component | Coverage | Purpose |
|-----------|----------|---------|
| **RENATER** | 3 French sites | National research network backbone |
| **Sites** | Bordeaux, Marne-la-Vallée, Villeneuve-d'Ascq | Multi-site latency diversity (sub-ms to tens of ms RTT) |
| **ENTSO-E** | European grid data | Real-time carbon intensity & energy mix |

---

## 📏 Standardized Metadata Schema

Every measurement includes:

```yaml
experiment_id: "unique-run-identifier"
code_digest: "git-commit-hash"
site_id: "bordeaux|marne|villeneuve"
calibration_tag: "metering-profile-v1"
timestamp: "PTP-synchronized-microseconds"
```

---

## 🎯 Experimental Capabilities

### ✓ Validated Use Cases

- ✅ **E1**: Side-by-side cell energy comparison under identical load
- ✅ **E2**: Per-pod power analysis with carbon-aware placement
- ✅ **E3**: 5G core baseline under steady control-plane traffic

### 🔬 Research Domains

- Energy-aware scheduling & sleep modes
- Carbon-optimized function placement
- QoS vs. power trade-off analysis
- Cross-layer protocol optimization
- Mobility-driven energy profiling

---

## 📋 Prerequisites

### Hardware Requirements

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Compute Nodes** | 2+ nodes (master + worker) | Kubernetes cluster |
| **SDR Hardware** | USRP N310 or compatible | Radio front-end |
| **Power Meters** | Shelly Plug or smart PDU | Energy monitoring |
| **Timing Source** | PTP-capable NIC or GPS | Microsecond synchronization |

### Software Stack

```yaml
Required Components:
  - Kubernetes: v1.28+
  - Docker/Containerd: Latest stable
  - PTP4L: LinuxPTP package
  - UHD: 4.7+ (USRP Hardware Driver)
  - Helm: v3.12+
  - MetalLB: v0.13+
  
Monitoring Stack:
  - Prometheus: v2.45+
  - Grafana: v10.0+
  - Kepler: Latest release
  
Network Functions:
  - OpenAirInterface: develop branch
  - Open5GS: v2.6+
```

### Cluster Configuration

#### Master Node (platform-master)
- **Role**: Control plane + Telemetry
- **CPU**: 12+ cores
- **RAM**: 32GB+
- **Storage**: 100GB+ SSD
- **Network**: 10Gbps + PTP-capable NIC

#### Worker Node (platform-worker)
- **Role**: RAN/Core workloads
- **CPU**: 16+ cores (for real-time processing)
- **RAM**: 32GB+
- **Storage**: 200GB+ SSD
- **Network**: 10Gbps + PTP-capable NIC
- **GPU/FPGA**: Optional (for acceleration)

### PTP4L Setup

```bash
# Install LinuxPTP
sudo apt-get install linuxptp

# Configure PTP on master node
sudo ptp4l -i eth0 -m -s -H

# Configure PTP on worker node
sudo ptp4l -i eth0 -m -s
```

### UHD Installation

```bash
# Install UHD for SDR support
sudo apt-get install libuhd-dev uhd-host
sudo uhd_images_downloader

# Verify USRP connection
uhd_find_devices
uhd_usrp_probe
```

### Additional Dependencies

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

# Install Prometheus & Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Install Kepler
kubectl apply -f https://raw.githubusercontent.com/sustainable-computing-io/kepler/main/manifests/kubernetes/deployment.yaml
```

---

<!-- ## 🚀 Getting Started

### Quick Start

```bash
# Clone the repository
git clone https://github.com/EiffelCOSYSERENA/green-xg.git
cd green-xg

# Verify prerequisites
./scripts/check-prerequisites.sh

# Configure your site
cp config/site.example.yaml config/site.yaml
# Edit config/site.yaml with your parameters

# Deploy the platform
./deploy.sh --site marne --experiment baseline

# Verify deployment
kubectl get pods -n green-xg

# Access Grafana dashboard
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Default credentials: admin/admin
```

### Running Your First Experiment

```bash
# Deploy a baseline 5G core
./experiments/run.sh --name e3-core-baseline --duration 30m

# Monitor in real-time
kubectl logs -f deployment/prometheus -n monitoring

# Export results
./scripts/export-results.sh --experiment e3-core-baseline --format DOI
```

---
 -->
## 🤝 Contributing

Green xG is an open platform welcoming contributions:

- 🐛 Report issues or bugs
- 💡 Propose new experimental scenarios
- 🔧 Contribute code improvements
- 📝 Enhance documentation
- 🌍 Add new testbed sites

---

## 📄 License

Open Source - See LICENSE file for details

---

## 👥 Team

**Université Gustave Eiffel** • **Université de Pau** • **Université des Sciences, des Techniques et des Technologies de Bamako**  **University of West London** 

---

<div align="center">

**Advancing sustainable and transparent wireless research toward 6G**

⭐ Star us on GitHub • 🔔 Watch for updates • 🍴 Fork to contribute

</div>
