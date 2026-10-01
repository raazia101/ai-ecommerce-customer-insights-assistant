FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-api.txt .

RUN pip install --no-cache-dir -r requirements-api.txt

COPY 06_ml ./06_ml

EXPOSE 8000

CMD ["uvicorn", "06_ml.api.main:app", "--host", "0.0.0.0", "--port", "8000"]