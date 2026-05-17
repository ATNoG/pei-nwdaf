# Performance Test Results

Load tests run with [Locust](https://locust.io) against the platform's three primary services.
All tests target a shared deployment at `https://10.255.28.248` unless noted otherwise.

---

## 1. Ingestion Service

**Endpoint:** `POST /data-ingestion/nef/notify`

| Users | Avg (ms) | p95 (ms) | RPS | Failures |
|-------|----------|----------|-----|----------|
| 25    | 49       | 93       | ~180 | 0        |
| 100   | 365      | 510      | ~180 | 0        |

**Conclusion:** Ingestion is stable under both loads with zero failures. Throughput plateaus around 180 RPS, which means the bottleneck is downstream (Kafka/processor), not the ingestion endpoint itself. Latency degrades 7× from 25→100 users but remains well within acceptable range.

---

## 2. Data Storage Service

**Endpoint:** `GET /data-storage/processed` (ClickHouse query)

### Remote (via reverse proxy)

| Users | Avg (ms) | p95 (ms) | p99 (ms) | RPS | Notes          |
|-------|----------|----------|----------|-----|----------------|
| 25    | 90       | 130      | 180      | 85  | baseline       |
| 75    | 261      | 470      | 1100     | 159 | baseline       |
| 75    | 187      | 340      | 490      | 168 | with replication |

### Localhost (before vs after optimization)

| Version  | Users | Avg (ms) | RPS  |
|----------|-------|----------|------|
| Previous | 250   | 1648     | ~130  |
| Current  | 250   | 134      | ~700  |
| Current  | 1000  | 765      | ~700   |


**Conclusion:** The current version is a **12× improvement** at 250 users (134ms vs 1648ms, 685 vs 132 RPS). Replication at 75 users actually improves latency (187ms vs 261ms) and slightly increases throughput. Reads benefit from replica distribution but still limited to the one instance of clickhouse. At 1000 users latency climbs to 765ms but still zero failures, suggesting the service degrades gracefully.

---

## 3. ML Inference Service

**Endpoint:** `POST /pei-ml/inference`

### Previous version

| Hardware | Users | Avg (ms) | p50 (ms) | p95 (ms) | RPS  | Failures |
|----------|-------|----------|----------|----------|------|----------|
| Standard | 5     | 322      | 300      | 440      | 9.5  | 1 (model load) |
| Standard | 25    | 1646     | 1700     | 2300     | 13.2 | 1        |
| Standard | 100   | 6732     | 7200     | 9700     | 12.1 | 4        |
| Better   | 10    | 218      | 220      | 330      | 23.0 | 0        |

### Current version

| Hardware | Users | Avg (ms) | p50 (ms) | p95 (ms) | RPS   | Failures |
|----------|-------|----------|----------|----------|-------|----------|
| Standard | 25    | 187      | 170      | 280      | 61.3  | 0        |
| Standard | 100   | 1424     | 1300     | 3000     | 49.6  | 0        |
| Standard | 600   | 23844    | 26000    | 54000    | 22.1  | 0        |
| Better   | 25    | 56       | 52       | 78       | 93.5  | 0        |
| Better   | 100   | 303      | 280      | 640      | 161.8 | 2        |

**Conclusion:** ML inference is the primary bottleneck of the system, as expected for CPU-bound inference.

- **Current vs previous (standard hardware, 100u):** 4× throughput gain (49.6 vs 12.1 RPS), 5.6× latency improvement (1424ms vs 6732ms avg).
- **Hardware matters most:** On better hardware, 100u achieves 162 RPS at 303ms avg — a **13× throughput gain** over the old version on standard hardware.
- **600u stress test:** System saturates at ~22 RPS with 23s average latency. No failures — the service queues requests rather than dropping them. Not suitable for high concurrency without horizontal scaling.

---

## Conclusion

The ingestion and storage layers are not the bottleneck. All production load pressure lands on ML inference. 
The system scales and most of the services can be replicated to handle high concurrency.
The problem on inference isn't the lack of GPU since models are tiny and can be served by a single CPU core. All the latency comes from data fetching ( including model and architecture ) and the overhead of passing the inference to a isolated container.
