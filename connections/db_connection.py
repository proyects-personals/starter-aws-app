import psycopg2
import os

def create_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        print("Conexión exitosa a la base de datos")
        return connection
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
