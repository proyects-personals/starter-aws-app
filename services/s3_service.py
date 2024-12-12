
import boto3
from botocore.exceptions import NoCredentialsError
import os

def get_images_from_s3(image_path: str):
    """
    Obtiene la URL completa de una imagen almacenada en S3.

    Args:
        image_path (str): La ruta de la imagen dentro del bucket S3.

    Returns:
        str: URL completa de la imagen en S3.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    bucket_name = 'starter-aws-app'
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': image_path},
            ExpiresIn=3600  # La URL expirará después de una hora
        )
        return url
    except NoCredentialsError:
        print("Error: No se encontraron credenciales de AWS.")
        return None
    except Exception as e:
        print(f"Error al obtener la URL de la imagen: {e}")
        return None
