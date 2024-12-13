from connections.db_connection import create_db_connection
from services.s3_service import get_images_from_s3, upload_image_to_s3
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from services.imagga_service import analyze_image_with_imagga

def get_all_memes():
    """
    Obtiene todos los memes de la base de datos, sus etiquetas, confianza, y les asigna la URL completa de la imagen desde S3.
    """
    connection = create_db_connection()
    if connection is None:
        return []

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
                
                # Asociar las etiquetas y la confianza
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

            return memes
    except Exception as e:
        return []
    finally:
        connection.close()



def create_meme(descripcion, usuario, image, cargada, etiquetas_usuario):
    """
    Crea un nuevo meme en la tabla 'memes' y la relación correspondiente en 'etiquetas', 
    añadiendo las etiquetas proporcionadas por el usuario junto con las obtenidas mediante la API de Imagga.
    """
    connection = create_db_connection()
    if connection is None:
        return None

    try:
        temp_folder = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        filename = secure_filename(image.filename)
        image_path = os.path.join(temp_folder, filename)
        image.save(image_path)

        # Analizar la imagen con Imagga y obtener las etiquetas
        etiquetas_imagga = analyze_image_with_imagga(image_path)

        # Combinar las etiquetas del usuario con las etiquetas de Imagga
        etiquetas_completas = [(etiqueta, None) for etiqueta in etiquetas_usuario] + \
                              [(etiqueta, confianza) for etiqueta, confianza in etiquetas_imagga]  # Etiquetas del usuario y de Imagga
        
        # Verificar que hay etiquetas para asociar con el meme
        if not etiquetas_completas:
            print("Error: No hay etiquetas disponibles para asociar con el meme.")
            return None

        # Subir la imagen a S3
        ruta = upload_image_to_s3(image_path, 'starter-aws-app')
        if ruta is None:
            print("Error: No se pudo subir la imagen a S3.")
            return None
        
        if not isinstance(cargada, datetime):
            cargada = datetime.now()

        with connection.cursor() as cursor:
            # Insertar el meme en la base de datos
            cursor.execute(
                "INSERT INTO memes (descripcion, usuario, ruta, cargada) VALUES (%s, %s, %s, %s) RETURNING id;",
                (descripcion, usuario, ruta, cargada)
            )
            meme_id = cursor.fetchone()[0]  # Obtener el ID del meme insertado
            connection.commit()

            # Insertar las etiquetas en la tabla 'etiquetas', con la confianza proporcionada por Imagga
            for etiqueta, confianza in etiquetas_completas:
                cursor.execute(
                    "INSERT INTO etiquetas (meme_id, etiqueta, confianza) VALUES (%s, %s, %s);",
                    (meme_id, etiqueta, confianza)
                )
            connection.commit()

            return meme_id
    except Exception as e:
        print(f"Error al crear el meme: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()
