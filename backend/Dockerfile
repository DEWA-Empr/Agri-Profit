FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# The large ML wheels (scikit-learn/pandas/numpy) can exceed pip's default 15s
# read timeout on a slow link; be patient and retry rather than failing the build.
RUN pip install --no-cache-dir --upgrade --timeout 120 --retries 5 -r /code/requirements.txt

COPY ./alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic
COPY ./app /code/app

# Run as a normal account. There is no reason for an API server to be root
# inside its own container, and it is the cheapest reduction available in the
# blast radius of a dependency compromise.
#
# The application owns nothing it does not need to write. /code stays
# root-owned and read-only to this user; only the two directories the DSS
# actually writes at runtime are handed over:
#
#   app/ml/models  latest_model.joblib, written by train-on-boot when the image
#                  carries no artefact (main.py lifespan -> train.ensure_model)
#   app/ml/data    crop_yield.csv, the generated training set
#
# They are created here rather than left to os.makedirs so their ownership is
# set at build time; a non-root process cannot create them under a root-owned
# parent, and the failure would surface as a startup crash on a cold volume.
RUN useradd --create-home --shell /usr/sbin/nologin agriprofit     && mkdir -p /code/app/ml/models /code/app/ml/data     && chown -R agriprofit:agriprofit /code/app/ml/models /code/app/ml/data

USER agriprofit

# Apply migrations before starting the server. The until-loop waits for
# Postgres to become reachable; exec hands signals to uvicorn as PID 1.
CMD ["sh", "-c", "until alembic upgrade head; do echo 'waiting for db...'; sleep 2; done; exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
