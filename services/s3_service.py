import boto3
from botocore.exceptions import NoCredentialsError
import os

def create_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

def generate_presigned_url(s3_client, bucket_name: str, image_path: str):
    try:
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': image_path},
            ExpiresIn=3600
        )
    except NoCredentialsError:
        print("Error: No se encontraron credenciales de AWS.")
        return None
    except Exception as e:
        print(f"Error al generar la URL firmada: {e}")
        return None

def upload_file_to_s3(s3_client, image_path: str, bucket_name: str, object_name: str):
    try:
        s3_client.upload_file(image_path, bucket_name, object_name)
        return object_name
    except FileNotFoundError:
        print(f"Error: El archivo {image_path} no fue encontrado.")
    except NoCredentialsError:
        print("Error: No se encontraron credenciales de AWS.")
    except Exception as e:
        print(f"Error al cargar el archivo a S3: {e}")
    return None

def get_images_from_s3(image_path: str):
    s3_client = create_s3_client()
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    return generate_presigned_url(s3_client, bucket_name, image_path)

def upload_image_to_s3(image_path: str, bucket_name: str, object_name: str = None):
    s3_client = create_s3_client()

    if object_name is None:
        object_name = f"assets/images/{os.path.basename(image_path)}"

    return upload_file_to_s3(s3_client, image_path, bucket_name, object_name)