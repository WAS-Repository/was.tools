# 03 Search Stack – Keyword, Vector & Graph

This expands on §15 of `advisement.txt`.

## 1. Goals
* p95 latency <300 ms WW
* Hybrid BM25 + dense vectors + graph traversal

## 2. Components
| # | Service | Tech | Deployment |
|---|---------|------|------------|
| 1 | Token Index | Typesense Cloud | SaaS → self-host later |
| 2 | Vector Index | FAISS shards | H100 GPUs |
| 3 | Graph DB | Neo4j/Neptune | Container next to IPFS |
| 4 | Search-Gateway | Go/Rust | CF Worker + internal API |
| 5 | Reranker-Svc | Cross-encoder gRPC | H100 GPUs |

## 3. Data Flow
```
Metadata JSON → Index Builder →
  • Typesense collection push
  • FAISS shard (.index) → IPFS CAR
  • Graph edge list → Neo4j bulk import
```

## 4. Query Flow
1. Parse & classify query via **Search-Gateway**.
2. Keyword search (BM25) + semantic search (FAISS).
3. RRF fusion → top-100.
4. Call **Reranker-Svc** gRPC (mutual-TLS via Envoy sidecar) for cross-encoder.
5. Graph expansion (optional) → related docs.
6. Return results.

## 5. APIs
* `/search` REST (**search.was.tools**) (Worker)
* `search(query:)` GraphQL resolver
* `/graph/cypher` proxy endpoint

## 6. KPIs
| Metric | Target | Phase |
|--------|--------|-------|
| nDCG@10 | >0.85 | Week-16 |
| semantic recall@10 | >0.75 | Week-16 |

## 7. Timeline
| Week | Deliverable |
|------|-------------|
| 4 | Typesense schema + 10 k docs |
| 6 | FAISS PoC + Search-Gateway skeleton w/ Envoy sidecar |
| 8 | Reranker-Svc deployed on H100 (gRPC) |
| 12 | Studio search bar switch (mesh mTLS) |
| 17 | Neo4j ingest + graph queries |
