import uvicorn
from openenv.server import create_app
import sys
import os

# Ensure the parent directory is in the path so it can find env.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env import SRETriageEnv

# Wrap the environment in the OpenEnv standard FastAPI app
app = create_app(SRETriageEnv)

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()