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
| [Infra](https://github.com/ATNoG/pei-nwdaf-infra)| Infrastructure components: Kafka, InfluxDB, ClickHouse, and monitoring stack |
| [Decision](https://github.com/ATNoG/pei-nwdaf-decision)| LLM-based decision engine that translates ML inferences into actionable network recommendations |
| [Frontend](https://github.com/ATNoG/pei-nwdaf-frontend)| Web dashboard for visualization, model training, inference, and system monitoring |
| [ML](https://github.com/ATNoG/pei-nwdaf-ml)| Machine learning service with MLflow for model versioning, training, and inference |
| [Policy](https://github.com/ATNoG/pei-nwdaf-policy)| Policy enforcement layer controlling data access between components via Permit.io |


## Quick Start

### Prerequisites

- Docker compose
- git
- CPU: 4+ cores
- RAM: 16 GB recommended
- Disk: 20+ GB free
- Ollama instance ( Just needed for decisions )

### Cloning project 
```sh
git clone --recurse-submodules https://github.com/ATNoG/pei-nwdaf
```

### Configuration

**Note:** The `.env.example` can be used as `.env` for single-machine deployments. All services communicate via the internal `nwdaf-network` Docker bridge network.

```bash
cp .env.example .env
# edit .env as needed
```
```

# Todo: add section about how to run with ledger
# 

### Running the Stack

#### Quick Start (Development Mode)
```bash
docker compose up --build
```
All services expose ports for debugging. Access services directly on their configured ports.

#### Production Mode
```bash
docker compose --profile prod up --build
```
Only nginx exposes ports (80/443). All services communicate privately via Docker network.

#### Manual Service Control (Development)
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

### Accessing Dashboard

**Development Mode (localhost with direct access):**
- Dashboard: `http://localhost:5173` (or via nginx: `http://localhost/`)
- MLflow: `http://localhost:5000/` (or via nginx: `http://localhost/mlflow`)
- Services exposed on configured ports

**Production Mode (via nginx only):**
- All services: `http://localhost/` (nginx reverse proxy)
- Internal services not directly accessible

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[License](LICENSE)
