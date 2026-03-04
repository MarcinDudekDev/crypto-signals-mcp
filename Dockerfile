FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
EXPOSE 8788
CMD ["python", "server.py", "--transport", "sse", "--port", "8788"]
