FROM python:3.10.7-slim-buster

RUN apt-get update && \
  apt-get install --no-install-recommends -y postgresql postgresql-contrib python-psycopg2 libpq-dev gcc musl-dev libc-dev libffi-dev libssl-dev cargo wget make wait-for-it openssh-server\
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

COPY start.sh ./
COPY poetry.lock pyproject.toml ./
COPY alembic.ini ./
COPY alembic.ini /etc/src/alembic.ini

RUN rm /etc/timezone

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY src /srv/app/src

EXPOSE 8080

CMD ["/bin/bash", "start.sh"]
