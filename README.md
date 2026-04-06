---
title: SRE Incident Commander
emoji: 🚨
colorFrom: blue
colorTo: red
sdk: docker
tags:
  - openenv
---

# SRE Incident Commander (OpenEnv)

## Description & Motivation
The **SRE Incident Commander** environment simulates real-world Site Reliability Engineering (SRE) triage. Instead of testing models on simplistic puzzle games, this environment evaluates a frontier AI's ability to logically debug a cascading microservices architecture (`Frontend -> API-Gateway -> Auth -> Database`). 

It explicitly penalizes "blind guessing" (restarting healthy services without checking metrics) and rewards methodical log/metric correlation. It features an integrated programmatic grader returning deterministic 0.0 - 1.0 scores based on efficiency and accuracy.

## Action & Observation Space
* **Action Space (`SREAction`):** Strictly typed JSON schema requiring a `command` (`get_service_tree`, `inspect_logs`, `check_metrics`, `read_config`, `rollback_config`, `restart_pod`) and a `target` service.
* **Observation Space (`SREObservation`):** Returns real-time system `telemetry`, console `output` from the last command, and a decaying `health_score`.

## Tasks & Difficulty Structure
1. **Task 0 (Easy) - Service Stopped:** The database service crashes and reports a DOWN state. The agent must detect the failure, read the OOMKilled logs, and execute a `restart_pod`.
2. **Task 1 (Medium) - Port Mismatch:** The API Gateway suffers a bad deployment, changing its listening port. The agent must `read_config` to identify the expected vs. actual port, and execute a `rollback_config`.
3. **Task 2 (Hard) - Cascading Leak + Chaos Monkey:** A configuration typo in the Auth service drastically limits its connection pool. This bubbles up the dependency tree, presenting as a 504 Timeout at the Frontend. Furthermore, a transient "Chaos Monkey" injects random latency noise across the mesh. The agent must map the service tree, ignore the transient latency spikes, trace the 504s down to the Auth service logs, and execute a `rollback_config`. (Note: Simply restarting the Auth pod will temporarily clear the pool but will *not* resolve the root cause config drift).

## Setup & Execution

**Containerized Execution (Docker):**
```bash
docker build -t sre-openenv .
docker run -p 8000:8000 sre-openenv