import os
import requests
import json
from openai import OpenAI
from typing import List, Optional

# --- Configuration & Environment Variables ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3-70b-chat-hf")
ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")
BENCHMARK = "sre_incident_commander"
SUCCESS_SCORE_THRESHOLD = 0.8 # Score needed to be considered a 'success'

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy_key_for_local")

SYSTEM_PROMPT = """You are a Tier-3 SRE. Your goal is to identify and resolve the root cause of system alerts.
Available Actions: get_service_tree, inspect_logs, check_metrics, read_config, rollback_config, restart_pod.
Targets: frontend, api-gateway, auth, database.
Provide actions in pure JSON format: {"command": "...", "target": "..."}
Think carefully about dependencies and logs before taking destructive actions."""

# --- Strict STDOUT Logging Helpers ---
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Flatten the action JSON string to ensure it prints on a single line
    action_flat = action.replace('\n', '').replace(' ', '')
    print(
        f"[STEP] step={step} action={action_flat} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

# --- Main Inference Loop ---
def run_baseline():
    tasks = ["task_0", "task_1", "task_2"]
    
    for task in tasks:
        log_start(task=task, env=BENCHMARK, model=MODEL_NAME)
        
        try:
            obs = requests.post(f"{ENV_URL}/reset?task_id={task}").json()
        except Exception as e:
            # Environment connection failure
            log_step(step=1, action="reset", reward=0.0, done=True, error=str(e))
            log_end(success=False, steps=1, rewards=[0.0])
            continue
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Alert triggered. Current state: {json.dumps(obs)}"}
        ]
        
        done = False
        step_count = 0
        rewards = []
        success = False
        
        while not done and step_count < 15:
            step_count += 1
            error = None
            reward = 0.0
            action_str = "{}"
            
            try:
                # 1. Get Model Action
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                action_str = response.choices[0].message.content
                action_dict = json.loads(action_str)
                messages.append({"role": "assistant", "content": action_str})
                
                # 2. Step Environment
                step_res = requests.post(f"{ENV_URL}/step", json=action_dict).json()
                
                output = step_res['observation']['output']
                reward = float(step_res['reward'])
                done = bool(step_res['done'])
                
                messages.append({"role": "user", "content": f"Result: {output}. Current telemetry: {step_res['observation']['telemetry']}"})
                
                # Check grader score if episode finished
                if done:
                    grader_score = step_res.get("info", {}).get("grader_score", 0.0)
                    success = grader_score >= SUCCESS_SCORE_THRESHOLD
                    
            except Exception as e:
                # Catch JSON parse errors or LLM timeouts gracefully
                error = str(e).replace('\n', ' ')
                done = True
                success = False

            # Append current step reward
            rewards.append(reward)
            
            # 3. Log strictly formatted step
            log_step(step=step_count, action=action_str, reward=reward, done=done, error=error)

        # 4. Log strictly formatted end
        log_end(success=success, steps=step_count, rewards=rewards)

if __name__ == "__main__":
    # Remove all standard prints to protect STDOUT parser
    run_baseline()