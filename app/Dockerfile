FROM python:3.10-slim

ENV PROJECT_DIR=/app
WORKDIR $PROJECT_DIR

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src src
COPY alembic.ini .

CMD alembic upgrade head; python src/main.py
