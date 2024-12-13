from connections.db_connection import create_db_connection
from services.s3_service import get_images_from_s3, upload_image_to_s3
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from services.imagga_service import analyze_image_with_imagga

# Función para obtener la conexión a la base de datos
def get_db_connection():
    connection = create_db_connection()
    if connection is None:
        raise Exception("Error al conectar con la base de datos")
    return connection

# Función para obtener las etiquetas y confianza de la imagen usando Imagga
def get_etiquetas_imagga(image_path):
    etiquetas_imagga = analyze_image_with_imagga(image_path)
    print(f"Etiquetas Imagga: {etiquetas_imagga}")
    return etiquetas_imagga

# Función para combinar etiquetas de usuario y etiquetas de Imagga
def combine_etiquetas(etiquetas_usuario, etiquetas_imagga):
    etiquetas_completas = [(etiqueta, None) for etiqueta in etiquetas_usuario] + \
                          [(etiqueta, confianza) for etiqueta, confianza in etiquetas_imagga]
    return etiquetas_completas

# Función para guardar la imagen en una carpeta temporal
def save_image_temp(image):
    temp_folder = os.path.join(os.getcwd(), 'temp')
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    filename = secure_filename(image.filename)
    image_path = os.path.join(temp_folder, filename)
    image.save(image_path)
    return image_path

# Función para insertar meme en la base de datos
def insert_meme(connection, descripcion, usuario, ruta, cargada):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO memes (descripcion, usuario, ruta, cargada) VALUES (%s, %s, %s, %s) RETURNING id;",
            (descripcion, usuario, ruta, cargada)
        )
        meme_id = cursor.fetchone()[0]  # Obtener el ID del meme insertado
        connection.commit()
    return meme_id

# Función para insertar etiquetas en la base de datos
def insert_etiquetas(connection, meme_id, etiquetas_completas):
    with connection.cursor() as cursor:
        for etiqueta, confianza in etiquetas_completas:
            cursor.execute(
                "INSERT INTO etiquetas (meme_id, etiqueta, confianza) VALUES (%s, %s, %s);",
                (meme_id, etiqueta, confianza)
            )
        connection.commit()

# Función principal para crear un meme
def create_meme(descripcion, usuario, image, cargada, etiquetas_usuario):
    try:
        connection = get_db_connection()

        # Guardar la imagen en un archivo temporal
        image_path = save_image_temp(image)

        # Analizar la imagen con Imagga
        etiquetas_imagga = get_etiquetas_imagga(image_path)

        # Combinar etiquetas de usuario y de Imagga
        etiquetas_completas = combine_etiquetas(etiquetas_usuario, etiquetas_imagga)

        # Subir la imagen a S3
        ruta = upload_image_to_s3(image_path, 'starter-aws-app')
        if ruta is None:
            print("Error: No se pudo subir la imagen a S3.")
            return None

        if not isinstance(cargada, datetime):
            cargada = datetime.now()

        # Insertar el meme en la base de datos
        meme_id = insert_meme(connection, descripcion, usuario, ruta, cargada)

        # Insertar las etiquetas en la base de datos
        insert_etiquetas(connection, meme_id, etiquetas_completas)

        return meme_id
    except Exception as e:
        print(f"Error al crear el meme: {e}")
        return None
    finally:
        connection.close()

# Función para obtener todos los memes
def get_all_memes():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    memes.id AS meme_id,
                    memes.descripcion,
                    memes.usuario,
                    memes.ruta AS meme_ruta,
                    memes.cargada,
                    etiquetas.etiqueta,
                    etiquetas.confianza
                FROM memes
                LEFT JOIN etiquetas ON memes.id = etiquetas.meme_id;
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]

            memes = []
            for row in rows:
                meme_data = dict(zip(columns, row))
                meme_id = meme_data["meme_id"]

                meme = next((m for m in memes if m["meme_id"] == meme_id), None)

                if meme is None:
                    meme = {
                        "meme_id": meme_id,
                        "descripcion": meme_data["descripcion"],
                        "usuario": meme_data["usuario"],
                        "ruta": get_images_from_s3(meme_data["meme_ruta"]),
                        "cargada": meme_data["cargada"],
                        "etiquetas": [],
                        "confianza": {}
                    }
                    memes.append(meme)

                if meme_data["etiqueta"]:
                    meme["etiquetas"].append(meme_data["etiqueta"])

                if meme_data["confianza"] is not None:
                    meme["confianza"][meme_data["etiqueta"]] = meme_data["confianza"]

            return memes
    except Exception as e:
        print(f"Error al obtener los memes: {e}")
        return []
    finally:
        connection.close()

# Función para buscar memes
def search_memes(query):
    """
    Filtra los memes según los criterios de búsqueda proporcionados.
    """
    connection = create_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            base_query = """
                SELECT 
                    memes.id AS meme_id,
                    memes.descripcion,
                    memes.usuario,
                    memes.ruta AS meme_ruta,
                    memes.cargada,
                    etiquetas.etiqueta,
                    etiquetas.confianza
                FROM memes
                LEFT JOIN etiquetas ON memes.id = etiquetas.meme_id
                WHERE
                    (memes.descripcion LIKE %s OR memes.usuario LIKE %s OR etiquetas.etiqueta LIKE %s)
            """

            params = [
                f"%{query['search']}%",
                f"%{query['search']}%",
                f"%{query['search']}%"
            ]
            if query.get('confianza'):
                base_query += " AND etiquetas.confianza = %s"
                params.append(query['confianza'])

            cursor.execute(base_query, params)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            memes = []
            for row in rows:
                meme_data = dict(zip(columns, row))
                meme_id = meme_data["meme_id"]
                print(f"Procesando meme con id: {meme_id}")

                meme = next((m for m in memes if m["meme_id"] == meme_id), None)

                if meme is None:
                    meme = {
                        "meme_id": meme_id,
                        "descripcion": meme_data["descripcion"],
                        "usuario": meme_data["usuario"],
                        "ruta": get_images_from_s3(meme_data["meme_ruta"]),
                        "cargada": meme_data["cargada"],
                        "etiquetas": [],
                        "confianza": {}
                    }
                    memes.append(meme)

                if meme_data["etiqueta"]:
                    meme["etiquetas"].append(meme_data["etiqueta"])

                if meme_data["confianza"] is not None:
                    meme["confianza"][meme_data["etiqueta"]] = meme_data["confianza"]

            # Aquí puedes filtrar los memes según el query y devolver los resultados completos
            return memes
    except Exception as e:
        print(f"Error al buscar los memes: {e}")
        return []
    finally:
        connection.close()

