FROM python:3.10-bookworm as base

# Setup env
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.6.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN mkdir -p $POETRY_HOME
# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python -
RUN ls -la $POETRY_HOME
COPY poetry.lock pyproject.toml ./

RUN poetry export --format=requirements.txt --without-hashes -o /tmp/requirements.txt


FROM python:3.10-bookworm AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY --from=base /tmp/requirements.txt ./requirements.txt
RUN python -m pip install -r ./requirements.txt

COPY main.py .
COPY reddit_sentiment_analysis ./reddit_sentiment_analysis

CMD ["python", "main.py"]

