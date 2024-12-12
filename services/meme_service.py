from connections.db_connection import create_db_connection

def get_all_memes():
    """
    Obtiene todos los registros de la tabla 'memes' como una lista de diccionarios.
    """
    connection = create_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM memes;")
            rows = cursor.fetchall()
            # Nombres de las columnas de la tabla
            columns = [desc[0] for desc in cursor.description]
            # Convertir cada fila (tupla) en un diccionario
            memes = [dict(zip(columns, row)) for row in rows]
            return memes
    except Exception as e:
        print(f"Error al obtener los memes: {e}")
        return []
    finally:
        connection.close()


def get_meme_by_id(meme_id):
    """
    Obtiene un meme específico por su ID.
    """
    connection = create_db_connection()
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM memes WHERE id = %s;", (meme_id,))
            meme = cursor.fetchone()  # Obtiene un solo resultado
            return meme
    except Exception as e:
        print(f"Error al obtener el meme con ID {meme_id}: {e}")
        return None
    finally:
        connection.close()


def create_meme(descripcion, usuario, ruta, cargada):
    """
    Crea un nuevo meme en la tabla 'memes'.
    """
    connection = create_db_connection()
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO memes (descripcion, usuario, ruta, cargada) VALUES (%s, %s, %s, %s) RETURNING id;",
                (descripcion, usuario, ruta, cargada)
            )
            meme_id = cursor.fetchone()[0]  # Obtiene el ID del nuevo meme insertado
            connection.commit()
            return meme_id
    except Exception as e:
        print(f"Error al crear el meme: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def update_meme(meme_id, descripcion, usuario, ruta, cargada):
    """
    Actualiza un meme en la tabla 'memes' por su ID.
    """
    connection = create_db_connection()
    if connection is None:
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE memes SET descripcion = %s, usuario = %s, ruta = %s, cargada = %s WHERE id = %s;",
                (descripcion, usuario, ruta, cargada, meme_id)
            )
            connection.commit()
            return cursor.rowcount > 0  # Retorna True si al menos una fila fue actualizada
    except Exception as e:
        print(f"Error al actualizar el meme con ID {meme_id}: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def delete_meme(meme_id):
    """
    Elimina un meme de la tabla 'memes' por su ID.
    """
    connection = create_db_connection()
    if connection is None:
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM memes WHERE id = %s;", (meme_id,))
            connection.commit()
            return cursor.rowcount > 0  # Retorna True si el meme fue eliminado
    except Exception as e:
        print(f"Error al eliminar el meme con ID {meme_id}: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()
