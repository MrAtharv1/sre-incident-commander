import uvicorn
from fastapi import FastAPI
from models import SREAction, SREObservation
from environment import SREEnvironment

app = FastAPI(title="SRE Incident Commander API")
env = SREEnvironment()

@app.post("/reset")
def reset_endpoint(task_id: str = None):
    obs = env.reset(task_id=task_id)
    return {
        "observation": obs.model_dump(),
        "reward": 0.01,
        "done": False,
        "info": {"score": 0.01}
    }

@app.post("/step")
def step_endpoint(action: SREAction):
    obs, reward_value, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": float(reward_value),
        "done": done,
        "info": info
    }

@app.get("/state")
def state_endpoint():
    obs = env.get_state(output="State polled.")
    return {"observation": obs.model_dump()}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
