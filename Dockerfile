# Usar imagen base de Python
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x run.sh

# Variables de entorno por defecto
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

EXPOSE ${APP_PORT}

# Usamos las variables en CMD
CMD ["sh", "-c", "uvicorn main:app --host $APP_HOST --port $APP_PORT"]
