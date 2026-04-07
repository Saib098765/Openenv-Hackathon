import os
import uuid
from openenv.core.env_server import Environment

try:
    from models import SREAction, SREObservation, SREState
except ImportError:
    from my_env.models import SREAction, SREObservation, SREState

class SRETriageEnv(Environment[SREAction, SREObservation, SREState]):
    def __init__(self):
        super().__init__()
        self._state = SREState(episode_id="init", step_count=0)
        self.task_name = os.getenv("OPENENV_TASK", "task-1-ip-block")
        self.max_steps = 10
        self.score = 0.01 
        self.blocked_ips = set()
        self.restarted_services = set()
        self._setup_task()

    @property
    def state(self) -> SREState:
        return self._state

    def _setup_task(self):
        self.logs = []
        if self.task_name == "task-1-ip-block":
            self.alerts = ["High rate of 404 errors detected."]
            self.logs = [
                "[INFO] auth-service started",
                "[WARN] 404 Not Found from IP 203.0.113.45",
                "[WARN] 404 Not Found from IP 203.0.113.45"
            ]
            self.target_ip = "203.0.113.45"
        
        elif self.task_name == "task-2-restart":
            self.alerts = ["Memory utilization critical on worker nodes."]
            self.logs = [
                "[INFO] cache-service healthy",
                "[ERROR] payment-service: OutOfMemoryError - Heap space",
                "[ERROR] payment-service: OutOfMemoryError - Heap space"
            ]
            self.target_service = "payment-service"

        elif self.task_name == "task-3-sql-inject":
            self.alerts = ["Suspicious database queries detected.", "High DB load."]
            self.logs = [
                "[INFO] web-service received request",
                "[WARN] SQL syntax error near 'OR 1=1' from IP 198.51.100.99",
                "[ERROR] db-service crashed due to malformed payload"
            ]
            self.target_ip = "198.51.100.99"
            self.target_service = "db-service"
        else:
            self.alerts = ["Unknown"]

    def reset(self, seed=None, episode_id=None, **kwargs) -> SREObservation:
        self._state.episode_id = episode_id or str(uuid.uuid4())
        self._state.step_count = 0
        self.blocked_ips.clear()
        self.restarted_services.clear()
        self.score = 0.01 
        self._setup_task()
        return self._get_observation("Environment initialized. Ready for commands.", False)

    def _get_observation(self, command_output: str, is_done: bool) -> SREObservation:
        return SREObservation(
            active_alerts=self.alerts,
            logs_tail="\n".join(self.logs[-5:]),
            last_command_output=command_output,
            system_status=f"Blocked IPs: {len(self.blocked_ips)} | Restarted Services: {len(self.restarted_services)}",
            reward=self.score,
            done=is_done
        )

    def step(self, action: SREAction, timeout_s=None, **kwargs) -> SREObservation:
        self._state.step_count += 1
        output = ""
        step_reward = 0.0
        is_done = False

        if action.command == "grep":
            matches = [line for line in self.logs if action.target in line]
            output = "\n".join(matches) if matches else "No matches found."
            step_reward += 0.1 
            
        elif action.command == "block_ip":
            self.blocked_ips.add(action.target)
            output = f"IP {action.target} added to firewall blocklist."
            if hasattr(self, 'target_ip') and action.target == self.target_ip:
                step_reward += 0.4 
            else:
                step_reward -= 0.2 
                
        elif action.command == "restart_service":
            self.restarted_services.add(action.target)
            output = f"Service {action.target} restarted successfully."
            if hasattr(self, 'target_service') and action.target == self.target_service:
                step_reward += 0.4 
            else:
                step_reward -= 0.2 
                
        elif action.command == "resolve_ticket":
            is_done = True
            output = "Ticket resolution submitted. Evaluating:"
            self._evaluate_task()
            step_reward = self.score 
        else:
            output = f"Unknown command: {action.command}. Valid: grep, block_ip, restart_service, resolve_ticket."
            step_reward -= 0.1

        if self._state.step_count >= self.max_steps:
            is_done = True
            self._evaluate_task()

        self.score = min(max(self.score + step_reward, 0.01), 0.99)
        return self._get_observation(output, is_done)

    def _evaluate_task(self):
        success_score = 0.95
        fail_score = 0.05
        if self.task_name == "task-1-ip-block":
            self.score = success_score if getattr(self, 'target_ip', None) in self.blocked_ips else fail_score
        elif self.task_name == "task-2-restart":
            self.score = success_score if getattr(self, 'target_service', None) in self.restarted_services else fail_score
        elif self.task_name == "task-3-sql-inject":
            has_ip = getattr(self, 'target_ip', None) in self.blocked_ips
            has_svc = getattr(self, 'target_service', None) in self.restarted_services
            if has_ip and has_svc:
                self.score = success_score
            elif has_ip or has_svc:
                self.score = 0.50
            else:
                self.score = fail_score