# Dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y ssh telnet && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server script and testbed
COPY mcp_server_pyats.py mcp_server_pyats.py
COPY testbed.yaml .

# Expose any necessary ports (optional, for debugging)
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "mcp_server_pyats"]
