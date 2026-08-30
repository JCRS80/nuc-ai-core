# syntax=docker/dockerfile:1.7
###############################################################################
# nuc-ai-core — Dockerfile multi-stage con uv
# Stage 1 (builder): resuelve e instala dependencias en un .venv aislado
# Stage 2 (runtime): imagen slim, solo runtime + venv + código de la app
###############################################################################

########################  STAGE 1 — BUILDER  ##################################
FROM python:3.12-slim AS builder

# Instala uv desde la imagen oficial (copia binario, sin curl)
COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

# Optimizaciones de build de uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 1) Instala SOLO las dependencias (capa cacheable) usando el lockfile
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 2) Copia el código fuente e instala el propio proyecto
COPY src ./src
RUN echo "# nuc-ai-core\nBackend de telemetría y orquestación de agentes — NUC Lab." > README.md
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

########################  STAGE 2 — RUNTIME  ##################################
FROM python:3.12-slim AS runtime

# Usuario no-root por seguridad
RUN groupadd --system app && useradd --system --gid app --home /app appuser

WORKDIR /app

# Copia el entorno virtual y el código ya construidos desde el builder
COPY --from=builder --chown=appuser:app /app/.venv /app/.venv
COPY --from=builder --chown=appuser:app /app/src /app/src

# El .venv en el PATH => uvicorn/python disponibles directamente
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=nuc-lab

EXPOSE 8000

USER appuser

# Healthcheck nativo de Docker apuntando al endpoint /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

CMD ["uvicorn", "nuc_ai_core.main:app", "--host", "0.0.0.0", "--port", "8000"]
