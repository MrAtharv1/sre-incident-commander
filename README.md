---
title: SRE Incident Commander
emoji: 🚨
colorFrom: blue
colorTo: red
sdk: docker
tags:
  - openenv
---

# 🚨 SRE Incident Commander (OpenEnv)

### Autonomous Site Reliability Engineering & Root Cause Analysis Benchmark

## 🚀 Description & Motivation
The **SRE Incident Commander** environment simulates real-world Site Reliability Engineering (SRE) triage. Unlike simplistic puzzle games, this environment evaluates a frontier AI's ability to logically debug a cascading microservices architecture.

It explicitly penalizes "blind guessing" (e.g., restarting healthy services without prior log inspection) and rewards methodical correlation of logs and metrics to minimize MTTR (Mean Time To Recovery).

## 🧠 System Topology & Action Space
The environment models a strict 4-tier dependency mesh: `frontend ➔ api-gateway ➔ auth ➔ database`

| Command | Purpose | Impact on MTTR |
| :--- | :--- | :--- |
| `get_service_tree` | Map the dependency mesh | High (Identifies blast radius) |
| `inspect_logs` | Retrieve stdout/stderr telemetry | Critical (Root Cause Analysis) |
| `check_metrics` | Analyze CPU/RAM/Latency spikes | High (Performance Triage) |
| `read_config` | Check current service configuration | Medium (Spots drift) |
| `rollback_config` | Revert to last known stable state | Critical (Remediation) |
| `restart_pod` | Force a service restart (OOM recovery) | Medium (Service Restoration) |

## 🔥 Benchmark Tasks & Difficulty

* **Task 0 (Easy) - Service Restoration:** The `database` crashes (OOMKilled). Agent must detect the DOWN state, verify logs, and execute `restart_pod`.
* **Task 1 (Medium) - Configuration Drift:** Port mismatch in `api-gateway` post-deployment. Requires `read_config` vs actual state comparison and `rollback_config`.
* **Task 2 (Hard) - Cascading Leak + Chaos Monkey:** * *The Bug:* The `auth` service suffers a connection pool limit typo causing a 504 Timeout at the `frontend`.
  * *The Noise:* An integrated "Chaos Monkey" injects transient latency spikes across the entire mesh.
  * *The Challenge:* The agent must maintain SLA by ignoring transient noise, tracing the timeout down the tree to `auth`, and fixing the root cause via `rollback_config`. *(Note: Simple restarts will fail as the config drift persists).*

## 📊 Evaluation & Scoring
The environment features an integrated programmatic grader returning a deterministic score (0.0 - 1.0):
* **Accuracy:** Did the agent resolve the root cause on the correct target?
* **Efficiency:** Step-penalty deductions for unnecessary "destructive" actions or hallucinated commands.
* **SLA Adherence:** Was the resolution within the strict 15-step limit?

## 🛠️ Setup & Execution (Docker)
Ensure you have Docker installed, then run:

```bash
# 1. Build the environment
docker build -t sre-openenv .

# 2. Run the SRE Commander (Port 7860 for Hugging Face compatibility)
docker run -p 7860:7860 sre-openenv

## 🏆 Baseline Scores (Qwen 2.5 72B)
* **Task 0:** Success (Score: 0.98) - Solved in 3 steps
* **Task 1:** Success (Score: 0.96) - Solved in 5 steps
* **Task 2:** Success (Score: 0.84) - Solved in 6 steps (Successfully filtered Chaos Monkey noise)
```
---
*Built by **Team Virasat** (JSS Academy of Technical Education, Noida)*