FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates poppler-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY *.py ./
COPY config ./config
COPY dist ./dist
COPY scripts ./scripts
RUN mkdir -p /app/data
ENV PYTHONUNBUFFERED=1 EKLIST_HOSTED=1 PORT=10000
EXPOSE 10000
CMD ["sh", "scripts/start-hosted.sh"]
