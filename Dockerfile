FROM python:3.11-slim

# Crear el directorio de trabajo
WORKDIR /app

# Copiar los archivos
COPY requirements.txt .
COPY stress.py .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto
CMD ["python", "stress.py"]
