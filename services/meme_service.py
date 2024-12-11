from connections.db_connection import create_db_connection

def get_all_memes():
    """
    Obtiene todos los registros de la tabla 'memes'.
    """
    connection = create_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM memes;")
            memes = cursor.fetchall()  # Obtiene todos los resultados
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
