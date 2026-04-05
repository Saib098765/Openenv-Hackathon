import uvicorn
import sys
import os

# Ensure the parent directory is in the path so it can find env.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our environment and models
from env import SRETriageEnv, SREAction, SREObservation

# The correct import path for openenv-core v0.1+
from openenv.core.env_server import create_app

# Create the FastAPI app. 
# We pass the class references so the server can automatically generate the correct API schemas.
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