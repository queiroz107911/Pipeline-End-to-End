FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv && uv sync

COPY . .

CMD ["python", "src/pipeline.py"]

