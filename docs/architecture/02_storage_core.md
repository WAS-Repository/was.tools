# 02 Storage Core – Private IPFS Cluster & Cold Backup

## 1. Cluster Topology
* **3 initial VPS nodes** (2 vCPU, 4 GB) → Raft consensus.
* **Swarm Key**: private pnet; no public bootstrappers.
* **Replication Factor**: 3 (min = max) for every pin.

## 2. Configuration Files
* `~/.ipfs/swarm.key` – 32-byte PSK (SOPS-encrypted in repo).
* `service.json` – Raft, `trusted_peers`, `replication_factor`.

## 3. Cold Backup Strategy
| Layer | Tool | Frequency |
|-------|------|-----------|
| CAR export | `ipfs-cluster-ctl pin export` | Nightly |
| Filecoin deals | Estuary.tech umbrella bucket | Weekly |
| R2 snapshot | `rclone sync` | Weekly |

## 4. Disaster Recovery
* Offline copy of `swarm.key`, `cluster_secret`, and CAR snapshots (Shamir 3-of-5 among board members).
* Restore procedure documented in `/docs/dr/restore.md`.

## 5. Metrics & Health Checks
* Grafana dashboards (community JSON) → pin count, peer lag.
* UptimeRobot HTTP + ICMP monitors per node.

## 6. Next Steps (Weeks 1-3)
1. Provision 3 VPS via Terraform/Ansible.
2. Bootstrap Raft cluster; verify `ipfs-cluster-ctl peers ls` shows 3 peers.
3. Pin sample Gutenberg CID; run `pin verify`.
