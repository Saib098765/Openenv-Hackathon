from models import SREAction
from server.my_env_environment import SRETriageEnv

def main():
    print("Starting SRE Triage Environment Evaluation...")
    # Instantiate the environment
    env = SRETriageEnv()
    
    # Reset to start a new episode
    obs = env.reset()
    print(f"Initial State: {obs.last_command_output}")
    print(f"Alerts: {obs.active_alerts}")
    
    # Take a test step
    action = SREAction(command="grep", target="404")
    obs = env.step(action)
    
    print(f"Action taken: grep '404'")
    print(f"Reward: {obs.reward}")
    print(f"Done: {obs.done}")

if __name__ == "__main__":
    main()