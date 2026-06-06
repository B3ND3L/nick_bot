FROM ghcr.io/astral-sh/uv:0.11-trixie-slim as builder

COPY nick_bot .
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync

FROM python:3.14-slim as final

WORKDIR /app

COPY --from=builder .venv/lib/python3.14/site-packages /usr/local/lib/python3.14
COPY nick_bot .

CMD python nick_bot.py