FROM mwalbeck/python-poetry:1-3.10

WORKDIR /root

COPY nick_bot nick_bot
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN poetry install

CMD poetry run python nick_bot/main.py
