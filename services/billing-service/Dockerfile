# Multi-stage Dockerfile for billing-service
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY packages/common-py /app/packages/common-py
COPY services/billing-service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /app/packages/common-py /app/packages/common-py
COPY --chown=appuser:appuser services/billing-service/src /app/src

USER appuser

ENV PATH=/home/appuser/.local/bin:/home/runner/work/_temp/ghcca-node/node/bin:/snap/bin:/home/runner/.local/bin:/opt/pipx_bin:/home/runner/.cargo/bin:/home/runner/.config/composer/vendor/bin:/usr/local/.ghcup/bin:/home/runner/.dotnet/tools:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
ENV PYTHONPATH=/app

EXPOSE 8003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
