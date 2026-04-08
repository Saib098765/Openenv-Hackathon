import sys
from models import SREAction
from server.my_env_environment import SRETriageEnv

def main():
    env = SRETriageEnv()
    obs = env.reset()
    task_name = env.task_name
    
    print(f"[START] task={task_name}", flush=True)
    
    action1 = SREAction(command="grep", target="error")
    obs = env.step(action1)
    
    print(f"[STEP] step=1 reward={obs.reward}", flush=True)
    
    action2 = SREAction(command="resolve_ticket", target="none")
    obs = env.step(action2)
    
    print(f"[STEP] step=2 reward={obs.reward}", flush=True)
    
    print(f"[END] task={task_name} score={env.score} steps={env.state.step_count}", flush=True)

if __name__ == "__main__":
    main()