FROM python:3.11-slim

# Crear directorio de la app
WORKDIR /app

# Copiar requerimientos
COPY requirements.txt .

# Instalar dependencias sin cache (más liviano)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto donde corre Flask
ENV PORT=5000

# Comando para ejecutarse en Coolify
CMD ["python", "app.py"]
