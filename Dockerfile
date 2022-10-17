FROM duffn/python-poetry:3.10-slim-1.2.2

WORKDIR /root

COPY nick_bot nick_bot
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN poetry install

CMD poetry run python nick_bot/main.py
