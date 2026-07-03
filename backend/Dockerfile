FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# The large ML wheels (scikit-learn/pandas/numpy) can exceed pip's default 15s
# read timeout on a slow link; be patient and retry rather than failing the build.
RUN pip install --no-cache-dir --upgrade --timeout 120 --retries 5 -r /code/requirements.txt

COPY ./alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic
COPY ./app /code/app

# Apply migrations before starting the server. The until-loop waits for
# Postgres to become reachable; exec hands signals to uvicorn as PID 1.
CMD ["sh", "-c", "until alembic upgrade head; do echo 'waiting for db...'; sleep 2; done; exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
