FROM python:3.12-slim

WORKDIR /app

COPY nick_bot nick_bot
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

# Install and configure Poetry
RUN pip install poetry
ENV PATH="${PATH}:/home/python/.local/bin"

RUN poetry install

CMD poetry run python nick_bot/main.py