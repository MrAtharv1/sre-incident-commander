import random
from typing import Tuple, Dict
from models import SREAction, SREObservation
from pydantic import BaseModel

SERVICES = ["frontend", "api-gateway", "auth", "database"]

class TaskConfig(BaseModel):
    task_id: str
    difficulty: str
    incident: str
    chaos_monkey: bool

TASKS = {
    "task_0": TaskConfig(task_id="task_0", difficulty="easy", incident="Service Stopped", chaos_monkey=False),
    "task_1": TaskConfig(task_id="task_1", difficulty="medium", incident="Port Mismatch", chaos_monkey=False),
    "task_2": TaskConfig(task_id="task_2", difficulty="hard", incident="Cascading Leak", chaos_monkey=True)
}

class SREEnvironment:
    def __init__(self):
        self.reset()

    def reset(self, task_id: str = "task_0") -> SREObservation:
        self.current_task = TASKS.get(task_id, TASKS["task_0"])
        self.step_count = 0
        self.service_tree_called = False
        self.resolved = False
        self.health_score = 1.0
        
        self.telemetry = {svc: {"status": "healthy", "latency_ms": 50, "errors": 0} for svc in SERVICES}
        self.chaos_monkey_active = self.current_task.chaos_monkey
        
        self._apply_incident_symptoms()
        return self.get_state(output=f"Initialized {self.current_task.difficulty} task. Monitoring alerts triggered.")

    def _apply_incident_symptoms(self):
        inc = self.current_task.incident
        if inc == "Service Stopped":
            self.telemetry["database"]["status"] = "DOWN"
        elif inc == "Port Mismatch":
            self.telemetry["api-gateway"]["status"] = "Connection Refused"
            self.telemetry["frontend"]["errors"] += 45
        elif inc == "Cascading Leak":
            self.telemetry["auth"]["errors"] += 500
            self.telemetry["api-gateway"]["status"] = "504 Timeout"
            self.telemetry["frontend"]["status"] = "504 Timeout"

    def _calculate_grader_score(self) -> float:
        """Programmatic grader returning 0.0 to 1.0 based on deterministic criteria."""
        score = 0.0
        if self.service_tree_called: score += 0.2
        if self.resolved: score += 0.8
        
        # Severe penalty for failing to resolve before SLA breach (step count limit)
        if not self.resolved and self.step_count > 10: 
            score = max(0.0, score - 0.5)
            
        return max(0.01, min(0.99, score)) 

    def step(self, action: SREAction) -> Tuple[SREObservation, float, bool, Dict]:
        self.step_count += 1
        reward = -0.01  # Step penalty for efficiency
        done = False
        output = ""

        # Chaos Monkey transient network jitter simulation
        if self.chaos_monkey_active and self.step_count > 4:
            self.chaos_monkey_active = False
            output += "[NETWORK ALERT] Transient BGP flap subsided. Noise cleared.\n"

        inc = self.current_task.incident

        if action.command == "get_service_tree":
            if not self.service_tree_called: 
                reward += 0.1
                self.service_tree_called = True
            output += "Dependency Tree: Frontend -> API-Gateway -> Auth -> Database"

        elif action.command == "inspect_logs":
            if action.target == "database" and inc == "Service Stopped": 
                output += "[FATAL] postgres: Process exited with code 137 (OOMKilled)."
            elif action.target == "api-gateway" and inc == "Port Mismatch": 
                output += "[ERROR] nginx: Upstream connection refused on port 8081."
            elif action.target == "auth" and inc == "Cascading Leak": 
                output += "[FATAL] auth-service: Connection Pool Exhausted due to config param max_conn=1."
            else: 
                output += f"[{action.target}] Logs indicate standard operation."

        elif action.command == "check_metrics":
            output += f"Metrics for {action.target}: {self.telemetry.get(action.target, 'Service not found.')}"

        elif action.command == "read_config":
            if action.target == "api-gateway" and inc == "Port Mismatch": 
                output += "listen_port: 8081 (Expected: 8080)"
            elif action.target == "auth" and inc == "Cascading Leak": 
                output += "max_conn: 1 (Expected: 100)"
            else: 
                output += f"[{action.target}] Configuration matches GitOps baseline."

        elif action.command == "rollback_config":
            if action.target == "api-gateway" and inc == "Port Mismatch":
                reward += 0.8
                self.resolved = True
                output += "Gateway config successfully rolled back to port 8080. Connections restored."
            elif action.target == "auth" and inc == "Cascading Leak":
                reward += 0.8
                self.resolved = True
                output += "Auth config successfully rolled back (max_conn=100). Cascading timeouts resolved."
            else:
                output += "Rollback applied, but had no effect on the ongoing incident."

        elif action.command == "restart_pod":
            if action.target == "database" and inc == "Service Stopped":
                reward += 0.8
                self.resolved = True
                output += "Database pod restarted. Process running on PID 1. Service healthy."
            elif action.target == "auth" and inc == "Cascading Leak":
                output += "Auth pod restarted. Connection pool temporarily cleared, but max_conn config is still restricted. Root cause remains."
            elif action.target in self.telemetry and self.telemetry[action.target]["status"] == "healthy":
                reward -= 0.3 
                output += f"Warning: Restarted {action.target} blindly. SLA penalty incurred."
            else:
                output += f"Pod {action.target} restarted. No change in overall system health."

        # Terminal conditions
        if self.resolved or self.step_count >= 15:
            done = True
        
        # Decay health score if unresolved
        if not self.resolved:
            self.health_score = max(0.0, 1.0 - (self.step_count * 0.05))

        obs = self.get_state(output=output)
        info = {}
        if done:
            info["task_id"] = self.current_task.task_id
            info["grader_score"] = self._calculate_grader_score()

        return obs, reward, done, info

    def get_state(self, output: str = "") -> SREObservation:
        current_telem = dict(self.telemetry)
        if self.chaos_monkey_active:
            # Inject transient noise
            for svc in current_telem:
                current_telem[svc]["latency_ms"] += random.randint(100, 400)
                
        return SREObservation(telemetry=current_telem, output=output, health_score=self.health_score)
