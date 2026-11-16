FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .

ENV MCP_TRANSPORT=streamable-http HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["team-time-mcp"]
