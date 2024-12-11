from dotenv import load_dotenv
import os
import boto3

# Cargar variables de entorno
load_dotenv()

# Configuración de S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

# Función para verificar la conexión
def test_s3_connection():
    try:
        # Listar los objetos del bucket como prueba
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            print("Conexión exitosa. Archivos en el bucket:")
            for obj in response['Contents']:
                print(f" - {obj['Key']}")
        else:
            print("Conexión exitosa, pero el bucket está vacío.")
    except Exception as e:
        print(f"Error al conectarse a S3: {e}")

# Ejecutar la prueba
if __name__ == "__main__":
    test_s3_connection()
