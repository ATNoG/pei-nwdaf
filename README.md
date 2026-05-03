# Intelligence in Action: Achieving Trustworthy AI-Driven Networks

## Overview

This platform brings AI-driven analytics and automatic decision creation to telecommunications networks.

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

## Quick Start

### Prerequisites

- Docker compose
- git
- make
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
make env 
# edit .env as needed
```

### Running the Stack

#### Quick Start (Development Mode)
```bash
make dev
```
> All services expose ports for debugging. Access services directly on their configured ports.

### Quick Start (Production)
```bash
make prod 
```
> Note that in this mode we only expose ports for nginx, ingestion service , decision service and observability stack.

### Quick Start (Producer)
As for now we only support `Nef_event_exposure` on ingestion service. (without auth). If you don't have one then you can run the simulator we provide. Note that this simulator follows TS 29.591 but only sends random values.
```bash
make producers
```

### Accessing Dashboard

Go to `http://localhost/`

## Advanced configuration

- [Train models on kubernetes](docs/train_models_on_kube.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[License](LICENSE)
