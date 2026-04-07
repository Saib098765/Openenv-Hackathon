
import os
import re
import json
import textwrap 
from typing import List, Optional
try:
    from server.my_env_environment import SRETriageEnv
    from models import SREAction
except ModuleNotFoundError:
    from my_env.server.my_env_environment import SRETriageEnv
    from my_env.models import SREAction
from openai import OpenAI
from env import SRETriageEnv, SREAction

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("OPENENV_TASK", "task-1-ip-block")
BENCHMARK = os.getenv("OPENENV_BENCHMARK", "sre-triage-env")

MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 0.9

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an autonomous Site Reliability Engineer (SRE).
    You will receive system observations including active alerts and log tails.
    You must output a JSON object representing your next action.
    Valid commands: 'grep', 'block_ip', 'restart_service', 'resolve_ticket'.
    Format your response STRICTLY as valid JSON:
    {"command": "command_name", "target": "target_value"}
    """
).strip()

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_model_action(client: OpenAI, obs_text: str) -> SREAction:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": obs_text},
            ],
            temperature=0.2,
            max_tokens=150,
            
        )
        text = (completion.choices[0].message.content or "").strip()
        
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE).strip()
        
        data = json.loads(text)
        return SREAction(command=data.get("command", "grep"), target=data.get("target", "error"))
        
    except Exception as exc:
        print(f"\n[DEBUG] LLM API/Parsing Error: {exc}\n", flush=True)
        return SREAction(command="resolve_ticket", target="error_parsing_llm")

def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = SRETriageEnv() 
    
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = env.reset() 
        
        for step in range(1, MAX_STEPS + 1):
            if getattr(obs, "done", False):
                break

            # Back to Pydantic's model_dump()
            obs_dump = json.dumps(obs.model_dump(), indent=2)
            action = get_model_action(client, obs_dump)
            action_str = f"{action.command}('{action.target}')"

            try:
                obs = env.step(action)
                reward = getattr(obs, "reward", 0.0)
                done = getattr(obs, "done", False)
                error = None
            except Exception as e:
                reward = 0.0
                done = True
                error = str(e)

            rewards.append(reward)
            steps_taken = step
            score = reward 

            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

            if done:
                break

        score = min(max(score, 0.01), 0.99)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    main()