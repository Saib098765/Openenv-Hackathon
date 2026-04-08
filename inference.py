import os
import json
from openai import OpenAI
from models import SREAction
from server.my_env_environment import SRETriageEnv

def main():
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", "dummy_key")
    client = OpenAI(base_url=api_base_url, api_key=api_key)
    
    tasks_to_run = ["task-1-ip-block", "task-2-restart", "task-3-sql-inject"]
    
    for task_name in tasks_to_run:
        os.environ["OPENENV_TASK"] = task_name
        
        env = SRETriageEnv()
        obs = env.reset()

        print(f"[START] task={task_name}", flush=True)
        
        # Agent Loop (Max 3 steps per task)
        for step in range(1, 4):
            if obs.done:
                break
                
            prompt = f"""
            You are an SRE AI agent. Your goal is to solve the server issue.
            Available commands: grep, block_ip, restart_service, resolve_ticket.
            Target must be a string (e.g., an IP address, a service name, or "none").

            Current Observation:
            Alerts: {obs.active_alerts}
            Logs: {obs.logs_tail}
            System Status: {obs.system_status}

            Look at the logs to find the offending IP or failing service.
            Respond ONLY with a valid JSON object in this exact format:
            {{"command": "your_command", "target": "your_target"}}
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                
                llm_output = response.choices[0].message.content.strip()
                action_dict = json.loads(llm_output)
                action = SREAction(command=action_dict["command"], target=action_dict["target"])
                
            except Exception:
                # Fallback to prevent crash if LLM hallucinates formatting
                action = SREAction(command="resolve_ticket", target="none")
                
            obs = env.step(action)
            
            print(f"[STEP] step={step} reward={obs.reward}", flush=True)
            
        print(f"[END] task={task_name} score={env.score} steps={env.state.step_count}", flush=True)

if __name__ == "__main__":
    main()