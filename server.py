from fastapi import FastAPI, Query
from models import SREAction, SREObservation
from environment import SREEnvironment

app = FastAPI(title="SRE Incident Commander API")
env = SREEnvironment()

@app.post("/reset", response_model=SREObservation)
def reset_endpoint(task_id: str = Query("task_0")):
    return env.reset(task_id=task_id)

@app.post("/step")
def step_endpoint(action: SREAction):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state", response_model=SREObservation)
def state_endpoint():
    return env.get_state(output="State polled.")