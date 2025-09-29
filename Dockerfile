# Usar imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Dar permisos de ejecución al script run.sh
RUN chmod +x run.sh

# Exponer el puerto 8000
EXPOSE 8000

# Ejecutar el script run.sh
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]