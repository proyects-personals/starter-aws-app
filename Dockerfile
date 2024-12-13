FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias, como libpq-dev
RUN apt-get update && apt-get install -y libpq-dev

# Copia el archivo de requerimientos y luego instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el archivo .env (asegúrate de que el archivo .env esté en la misma carpeta que tu Dockerfile)
COPY .env .env

# Copia el resto de los archivos del proyecto
COPY . .

# Exponer el puerto 5000 para que sea accesible
EXPOSE 5000

# Asegúrate de que tu aplicación cargue el archivo .env antes de ejecutar el código
CMD ["python", "app.py"]
