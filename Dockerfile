FROM python:3.12-slim
LABEL io.modelcontextprotocol.server.name="io.github.marcindudekdev/crypto-signals-mcp"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
ENV MCP_TRANSPORT=sse
EXPOSE 8080
CMD ["python", "server.py"]
