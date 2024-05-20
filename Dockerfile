FROM python:3.12


WORKDIR /hik_backend

COPY req.txt .

RUN pip install -r req.txt

COPY . .


CMD alembic upgrade head && gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --forwarded-allow-ips='*'
