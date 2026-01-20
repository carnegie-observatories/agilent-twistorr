FROM ghcr.io/astral-sh/uv:debian

COPY . /app
WORKDIR /app
RUN uv sync
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "grafana_load.py"]
