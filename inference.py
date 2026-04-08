import os
import sys
import json
from openai import OpenAI
from models import SREAction
from server.my_env_environment import SRETriageEnv

def main():
    # 1. Initialize environment
    env = SRETriageEnv()
    obs = env.reset()
    task_name = env.task_name
    
    print(f"[START] task={task_name}", flush=True)
    
    # 2. Connect to the Hackathon's LiteLLM Proxy
    # Fallbacks provided just in case, but os.environ will catch their injected keys
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", "dummy_key")
    
    client = OpenAI(base_url=api_base_url, api_key=api_key)
    
    # 3. Agent Loop (Max 3 steps to prevent infinite loops)
    for step in range(1, 4):
        if obs.done:
            break
            
        # Build the prompt asking the LLM what to do based on the current logs
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
            # Call the hackathon's proxy
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            llm_output = response.choices[0].message.content.strip()
            action_dict = json.loads(llm_output)
            action = SREAction(command=action_dict["command"], target=action_dict["target"])
            
        except Exception as e:
            action = SREAction(command="resolve_ticket", target="none")
            
        obs = env.step(action)
        
        print(f"[STEP] step={step} reward={obs.reward}", flush=True)
        
    print(f"[END] task={task_name} score={env.score} steps={env.state.step_count}", flush=True)

if __name__ == "__main__":
    main()