import os
import uuid
from typing import List
from openenv.core.env_server import Environment, Action, Observation, State
from openenv.core.env_server.types import Action, Observation
from pydantic import Field

class SREAction(Action):
    command: str
    target: str

class SREObservation(Observation):
    active_alerts: List[str]
    logs_tail: str
    last_command_output: str
    system_status: str
    reward: float = 0.0
    done: bool = False

class SREState(State):
    episode_id: str = ""
    step_count: int = 0
