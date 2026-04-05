FROM python:3.10-slim

WORKDIR /app

# Copy all your project files into the container
COPY . .

# Install the project and its dependencies directly from pyproject.toml
RUN pip install --no-cache-dir .

# Expose the standard Hugging Face Space port
EXPOSE 7860

# Boot the FastAPI server exactly how openenv validate expects it
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]