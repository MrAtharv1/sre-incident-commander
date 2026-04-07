from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

class SREAction(BaseModel):
    command: Literal[
        "get_service_tree", 
        "inspect_logs", 
        "check_metrics", 
        "read_config", 
        "rollback_config", 
        "restart_pod"
    ] = Field(..., description="The SRE command to execute.")
    target: str = Field(..., description="The target service ('frontend', 'api-gateway', 'auth', 'database', or 'all').")

class SREObservation(BaseModel):
    telemetry: Dict[str, Any] = Field(..., description="Current system metrics and states.")
    output: str = Field(..., description="Console output from the last executed command.")
    health_score: float = Field(..., description="Current system health score (0.0 to 1.0).")


class SREReward(BaseModel):
    value: float = Field(..., description="The numerical reward value.")
