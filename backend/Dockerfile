FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py database.py gunicorn.conf.py ./

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
