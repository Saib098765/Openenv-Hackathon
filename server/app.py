import uvicorn
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env import SRETriageEnv, SREAction, SREObservation
from openenv.core.env_server import create_app

# FastAPI app
app = create_app(
    SRETriageEnv,
    SREAction,
    SREObservation,
    env_name="sre-triage-env"
)

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()