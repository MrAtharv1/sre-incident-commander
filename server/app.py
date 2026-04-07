from fastapi import FastAPI, Query
from models import SREAction, SREObservation, SREReward
from environment import SREEnvironment

app = FastAPI(title="SRE Incident Commander API")
env = SREEnvironment()

@app.post("/reset", response_model=SREObservation)
def reset_endpoint(task_id: str = Query("task_0")):
    return env.reset(task_id=task_id)

@app.post("/step")
def step_endpoint(action: SREAction):
    obs, reward_value, done, info = env.step(action)
    
    
    reward_model = SREReward(value=reward_value)
    
    return {
        "observation": obs.model_dump(),
        "reward": reward_model.model_dump(), 
        "done": done,
        "info": info
    }

@app.get("/state", response_model=SREObservation)
def state_endpoint():
    return env.get_state(output="State polled.")
