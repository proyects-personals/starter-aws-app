# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y libpq-dev

# Copia el archivo de dependencias (requirements.txt) al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos al contenedor
COPY . .

# Expone el puerto en el que correrá Flask (5000)
EXPOSE 5000

# Define el comando para correr la aplicación
CMD ["python", "app.py"]
