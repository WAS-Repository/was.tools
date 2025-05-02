# World Archive System – Architecture Overview

This document summarises the micro-services, cloud-native architecture that underpins the World Archive System (WAS).

## High-Level Domains
| Domain | Purpose | Principle Tech |
|--------|---------|----------------|
| **Ingestion Mesh** | Harvest, enrich, validate public-domain artefacts | Python/Go agents, OCI images, NATS JetStream |
| **Storage Core** | Private IPFS Cluster + Filecoin cold backups | Kubo, ipfs-cluster-service |
| **Index & Search** | Typesense keyword index, FAISS vector shards, Graph DB | Typesense, FAISS, Neo4j/Neptune |
| **API Gateway** | Read-only GraphQL + REST search | Cloudflare Workers, Durable Objects |
| **Frontend Studio** | Browser IDE & data explorer | Vite + React + Monaco + Yjs |
| **Observability & Ops** | Metrics, logs, traces, IaC | Prometheus, Grafana, Loki, Terraform |
| **Platform & Mesh** | Service mesh, internal gRPC contracts | Istio/Linkerd, Envoy, protobuf |
| **Governance & Compliance** | Takedown workflow, Source Trust Registry | Durable Objects, GitHub Actions |

## Micro-service Groups
1. **Harvester / Extractor / Validator / Deduplicator / Pinner / Connector** – stateless OCI containers; event-driven.
2. **Search-Gateway** – lightweight Go/Rust service; hybrid ranker; deployed as CF Worker.
3. **Graph-Service** – Neo4j/Neptune container with Cypher/SPARQL endpoint.
4. **Authz-Edge** – Cloudflare Worker handling JWT issuance & rate-limiting.
5. **Studio-Graph** – containerised GraphQL resolver (BFF) speaking gRPC to backend services.
6. **Service Mesh** – Istio/Linkerd sidecars enabling mTLS & telemetry across pods.

## Data Flow
```
URL list → Harvester → Raw CID (CAR) ↘
                                 Validator → Pinner → IPFS Cluster
          Extractor → Metadata JSON ───────┘             ↓
                                                      Edge KV (index)
```
Vector + token indices are built from metadata and stored in FAISS / Typesense.

## Deployment Footprint
* **Edge**: Cloudflare Workers + KV + Durable Objects.
* **Core**: 3-node IPFS Cluster (Raft), Prometheus+Grafana stack.
* **GPU**: Prime Intellect H100 Kubernetes namespace hosting Extractor & FAISS shards.

Refer to the individual service documents in this folder for implementation specifics.

---

## Domain Map & Service Endpoints

| Domain | Purpose / Audience | Key Endpoints |
|--------|--------------------|---------------|
| **was.foundation** | Governance site, documentation, OAuth | `www.was.foundation` (Next.js), `docs.was.foundation` (MkDocs), `auth.was.foundation` (Auth callbacks) |
| **was.network** | Internal ops & platform mesh | `grafana.was.network`, `loki.was.network`, `tempo.was.network`, `registry.was.network` (Harbor), `*.svc.was.network` (Istio service DNS) |
| **was.tools** | Public APIs & frontend | `api.was.tools/graphql`, `search.was.tools` (REST), `studio.was.tools` (SPA), `cdn.was.tools` (assets/R2) |
| **was.ngo / was.ong** | Long-term public archive & trust domain | `browse.was.ngo` (static gateway UI), `ipns.was.ngo` → `dnslink=/ipns/w.a.s`, `embed.was.ngo/{cid}` (oEmbed) |

Each micro-service is deployed under the domain that best matches its audience and trust boundary (e.g., internal mesh services under `*.was.network`; public read APIs under `was.tools`).
