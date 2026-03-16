# Intelligence in Action: Achieving Trustworthy AI-Driven Networks

## Overview

This platform brings AI-driven analytics and autonomous decision-making to telecommunications networks.

Network telemetry is continuously ingested, processed, and stored. Machine learning models --- registered and versioned via MLflow --- run inference over that data and publish results to a shared event stream. A policy layer governs data access between all components, ensuring that only authorized services can read or act on sensitive network metrics. An LLM-based decision service consumes model inferences and translates them into actionable network recommendations.

The result is a closed-loop system where raw network data flows through collection, analysis, and decision stages, with policy enforcement and observability at every step.


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


> `#` stands for adviser


## Architecture
![architecture](images/architecture.png)

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

```bash
docker compose up -d
```

## Components

| Component | Description | Docs |
|---|---|---|
| **Infra** | Kafka, Prometheus, Grafana, Loki, Alloy | [docs/infra.md](docs/infra.md) |
| **Storage** | InfluxDB, ClickHouse, data-storage API | [docs/storage.md](docs/storage.md) |
| **Policy** | Permit.io PDP, policy-service | [docs/policy.md](docs/policy.md) |
| **Ingestion** | Data ingestion service | [docs/ingestion.md](docs/ingestion.md) |
| **Processor** | Windowed data processor (60s / 300s) | [docs/processor.md](docs/processor.md) |
| **ML** | MLflow, MinIO, PostgreSQL, ML inference service | [docs/ml.md](docs/ml.md) |
| **Decision** | LLM-based decision service | [docs/decision.md](docs/decision.md) |
| **Frontend** | Nginx reverse proxy, Vite/React dashboard | [docs/frontend.md](docs/frontend.md) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[License](LICENSE)
