from connections.s3_connection import create_s3_client
from connections.db_connection import create_db_connection
import os

def test_s3_connection():
    try:
        s3_client = create_s3_client()
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            print("Conexión exitosa a S3. Archivos en el bucket:")
            for obj in response['Contents']:
                print(f" - {obj['Key']}")
        else:
            print("Conexión exitosa a S3, pero el bucket está vacío.")
    except Exception as e:
        print(f"Error al conectarse a S3: {e}")

def test_db_connection():
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Conexión exitosa a la base de datos PostgreSQL. Versión: {db_version[0]}")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error al conectarse a la base de datos PostgreSQL: {e}")
