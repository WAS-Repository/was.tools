# 05 Ops & Observability

## 1. Infrastructure-as-Code
* Terraform modules forked from HashiCorp reference.
* Secrets encrypted with SOPS (age).
* Ansible bootstrap for VPS.

## 2. Monitoring Stack
| Layer | Tool | Endpoint |
|-------|------|----------|
| Metrics | Prometheus | `/metrics` |
| Dashboards | Grafana | `grafana.was.network` |
| Logs | Loki | `loki.was.network` |
| Traces | Tempo | integrated |
| Alerts | UptimeRobot + PagerDuty | 2 min intervals |

> **Mesh upgrade:** inject Envoy or OpenTelemetry sidecars for every non-Worker pod, shipping traces to Tempo; enable Istio mTLS telemetry.

## 3. CI/CD Gates
* Trivy scan; fail if CVE >7.0.
* Cosign verify container provenance.
* OTLP traces for every deploy step.
* **Golden Path Template:** each new micro-service repo inherits Dockerfile, Helm chart, protobuf contract tests, Trivy scan, Cosign sign-off, Hugo docs.
* Nightly **contract test** GitHub Action asserts protobuf backward compatibility across `main` → `HEAD`.

## 4. Cost & Carbon Tracking
* Tag R2 bandwidth / storage.
* Estimate kgCO₂ via cloud PUE factors.

## 5. Disaster Recovery
* Monthly restore drill using CAR snapshots.
* Shamir 3-of-5 for `cluster_secret`.
