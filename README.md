# Intelligence in Action: Achieving Trustworthy AI-Driven Networks

## Overview

This platform brings AI-driven analytics and autonomous decision-making to telecommunications networks.

Network telemetry is continuously ingested, processed, and stored. Machine learning models --- registered and versioned via MLflow --- run inference over that data and publish results to a shared event stream. A policy layer governs data access between all components, ensuring that only authorized services can read or act on sensitive network metrics. An LLM-based decision service consumes model inferences and translates them into actionable network recommendations.

The result is a closed-loop system where raw network data flows through collection, analysis, and decision stages, with policy enforcement and observability at every step.

For a more detailed explanation of the project access our [website](https://atnog.github.io/pei-nwdaf-microsite/).

### Team

| Name | GitHub |
|---|---|
| Thiago Vicente | [@ThiagoAVicente](https://github.com/ThiagoAVicente) |
| Miguel Neto | [@alxmra](https://github.com/alxmra) |
| Alexandre Andrade | [@Alexandre-A](https://github.com/Alexandre-A) |
| João Pereira | [@JPSP9547](https://github.com/JPSP9547) |
| André Martins | [@Pencsss](https://github.com/Pencsss) |

#### Advisors

| Name | 
|---|
| Rui Aguiar |
| Rafael Direito | 
| Rafael Teixeira | 

## Architecture
![architecture](images/architecture.png)

### Relevant repositories

| Repository | Description|
|-----------|------------|
| [Data Storage](https://github.com/ATNoG/pei-nwdaf-data-storage)| Stores processed network analytics data in InfluxDB and ClickHouse for querying and analysis |
| [Data Ingestion](https://github.com/ATNoG/pei-nwdaf-data-ingestion)| Receives raw network telemetry from producers via HTTP/WebSocket and publishes to Kafka |
| [Data Processor](https://github.com/ATNoG/pei-nwdaf-data-processor)| Consumes raw data from Kafka, aggregates into time windows, and writes to storage |
| [Network Producer](https://github.com/ATNoG/pei-nwdaf-network-producer)| Captures network traffic (pcap/csv) and sends batches to ingestion service |
| [Infra](https://github.com/ATNoG/pei-nwdaf-infra)| Infrastructure components: Kafka, InfluxDB, ClickHouse, and monitoring stack |
| [Decision](https://github.com/ATNoG/pei-nwdaf-decision)| LLM-based decision engine that translates ML inferences into actionable network recommendations |
| [Frontend](https://github.com/ATNoG/pei-nwdaf-frontend)| Web dashboard for visualization, model training, inference, and system monitoring |
| [ML](https://github.com/ATNoG/pei-nwdaf-ml)| Machine learning service with MLflow for model versioning, training, and inference |
| [Policy](https://github.com/ATNoG/pei-nwdaf-policy)| Policy enforcement layer controlling data access between components via Permit.io |
| [Network Producer](https://github.com/ATNoG/pei-network-producer)| Standalone network traffic producer for testing and development |

## Quick Start

### Prerequisites

- Docker compose
- git
- CPU: 4+ cores
- RAM: 16 GB recommended
- Disk: 20+ GB free

### Cloning project 
```sh
git clone --recurse-submodules https://github.com/ATNoG/pei-nwdaf
```

### Configuration

**Note:** The `.env.example` can be used as `.env` if the project components are on the same machine.

```bash
cp .env.example .env
# edit .env as needed
```

### Running the Stack

**Start kafka**
```bash
docker compose up --build kafka kafka-init-topics -d
```

**Start services**

> **Note:** This will give you some errors on policy-service if you don't set a permit api key but it won't stop the application from running if POLICY_ENABLED is set to false

```bash
docker compose up --build data-storage data-ingestion processor1 processor2 mlservice decision policy-api
```

**Start frontend**
```bash
docker compose up --build frontend nginx
```

**Start network producer**
```bash
cd Network-Producer
PORT=8001 docker compose up --build producer-csv 

# if u want to test the system with data from one of your internet interfaces

CAPTURE_INTERFACE="<your_interface>" docker compose up --build producer-tshark
```

### Acessing dashboard

**Running on local machine**

Access `http://localhost/`.

**Connect your producer**

1. Click on **Add Producer** 

2. Set url `http://producer-csv:8001/subscriptions`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[License](LICENSE)
