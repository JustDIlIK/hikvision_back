FROM python:3.12


WORKDIR /hik_backend

COPY req.txt .

RUN pip install -r req.txt

COPY . .

WORKDIR /app/

CMD gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8001