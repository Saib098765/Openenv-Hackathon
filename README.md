---
title: SRE Log Triage OpenEnv
emoji: 🛠️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

## Action Space
- `command` (String): The action to execute (`grep`, `block_ip`, `restart_service`, `resolve_ticket`).
- `target` (String): The payload for the command. 

## Observation Space
- `active_alerts` (List[String]): PagerDuty-style alerts active in the current state.
- `logs_tail` (String): The most recent standard output from the server environment.
- `last_command_output` (String): The direct output of the agent's last chosen command.
- `system_status` (String): Summarized status of firewalls and active services.

## Tasks
1. **task-1-ip-block (Easy):** Find the IP address causing continuous 404s in the log string and block it.
2. **task-2-restart (Medium):** Identify the microservice exhibiting a memory leak and restart it.
3. **task-3-sql-inject (Hard):** Observe an SQL injection attack in the logs, block the originating IP, AND restart the compromised database service.

## Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Validate environment: `openenv validate`
3. Run inference: 
   ```bash
   export OPENAI_API_KEY="your-key"
   export OPENENV_TASK="task-1-ip-block"
   python inference.py