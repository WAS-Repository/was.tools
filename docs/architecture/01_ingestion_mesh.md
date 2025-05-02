# 01 Ingestion Mesh – Agents & Control-Plane

This document drills into the fleet of micro-agents that continuously collect, enrich, and validate public-domain data for WAS.

## 1. Agent Catalogue
| Agent | Function | Example Tech |
|-------|----------|--------------|
| **Harvester** | Fetch raw HTML, PDF, EPUB, CSV, images | `httpx`, `trio`, Wget |
| **Extractor** | NLP / ML enrichment → metadata & embeddings | spaCy, Tika, Whisper, CLIP |
| **Deduplicator** | Detect near-duplicate CIDs | MinHash / SimHash (datasketch) |
| **Validator** | Licence & malware checks | SPDX DB, VirusTotal API |
| **Pinner** | Pin approved CIDs to IPFS-Cluster | `ipfs-cluster-ctl`, CAR generation |
| **Connector** | Discover inter-document relationships | Custom regex, citation parser |
| **Telemetry Collector** | Ship OpenTelemetry traces / metrics | OTLP gRPC → Tempo + Prometheus |

All agents are stateless OCI containers (<150 MB) orchestrated by Kubernetes (edge VPS or GPU farm).

> **Platform update:** every agent has its own repo + CI pipeline; images are published to an **internal Harbor registry** (`registry.was.network`) signed with Cosign. Subject names are versioned (`v1.harvester.raw`, etc.) to allow parallel migrations.

## 2. Control Plane
* **Message Broker:** NATS JetStream (`nats.was.network`) (topics: `v1.source.discovered`, `v1.file.harvested`, `v1.file.extracted`, `v1.file.validated`).
* **Backpressure:** JetStream consumer quotas + lag metrics.
* **Auth:** agents receive short-lived JWTs signed by WAS.foundation.
* **Agent-Catalog:** Durable Object micro-service that exposes live agent health (`/agents/online`) and desired replica counts (consumed by KEDA autoscaler).

## 3. Data Formats
* **WARC/1.1** for raw crawls (gzip).
* **DAG-JSON** for metadata blocks linked to parent WARC CAR.
* **Parquet** snapshots for offline analytics.

## 4. Deployment Models
| Environment | Orchestration | Notes |
|-------------|--------------|-------|
| Prime Intellect H100 | K8s namespace | GPU-bound Extractor jobs |
| Edge VPS | Docker Compose / systemd-nspawn | Always-on Harvesters |
| Community Nodes | Crontab script | Volunteer crawl tasks |

## 5. Observability
* OTLP traces from every agent.
* Prometheus scrape → Grafana; alert if harvest success < 95 %.
* Loki logs; Tempo traces.

## 6. Security & Compliance
* Robots.txt respect.
* Extractors run under gVisor/Firecracker.
* IPLD event log for full provenance.

## 7. Immediate Tasks (Weeks 0-6)
1. Draft `was-agents` mono-repo template with protobuf contracts and GitHub Actions (Trivy + Cosign).
2. Package Harvester PoC (Project Gutenberg) → CAR and push image to internal registry.
3. Set up JetStream test cluster; publish/consume **versioned** events.
