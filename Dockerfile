
# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

# Оновлення системних пакетів
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Спочатку копіюємо файли залежностей
COPY pyproject.toml uv.lock README.md ./

# Встановлюємо залежності без встановлення самого проєкту
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Копіюємо код проєкту
COPY src ./src

# Встановлюємо проєкт
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable


FROM python:3.12-slim

# Оновлення системних пакетів у фінальному образі
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Створюємо непривілейованого користувача
RUN useradd --system --uid 10001 --no-create-home appuser

WORKDIR /app

# Копіюємо віртуальне середовище з етапу збірки
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Запускаємо застосунок без root-прав
USER appuser

EXPOSE 8000

# Перевірка працездатності застосунку
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "k_cher.api:app", "--host", "0.0.0.0", "--port", "8000"]
