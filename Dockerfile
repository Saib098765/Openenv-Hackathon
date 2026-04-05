FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose standard HF Space port
EXPOSE 7860

# Command to run openenv API server via its CLI
CMD ["openenv", "serve", "--host", "0.0.0.0", "--port", "7860"]