FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-capstone.txt .

RUN pip install --no-cache-dir -r requirements-capstone.txt

COPY 09_capstone/ui ./09_capstone/ui

EXPOSE 8501

CMD ["streamlit", "run", "09_capstone/ui/app.py", "--server.address=0.0.0.0", "--server.port=8501"]