import uvicorn
import argparse

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with 'uv sync'"
    ) from e

try:
    from ..models import SREAction, SREObservation
    from .my_env_environment import SRETriageEnv
except ModuleNotFoundError:
    from models import SREAction, SREObservation
    from server.my_env_environment import SRETriageEnv

# Create the FastAPI app with your SRE Environment
app = create_app(
    SRETriageEnv,
    SREAction,
    SREObservation,
    env_name="sre-triage-env",
    max_concurrent_envs=1, 
)

def main(host: str = "0.0.0.0", port: int = 7860):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    main(host=args.host, port=args.port)