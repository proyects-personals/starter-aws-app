import os
import requests

def analyze_image_with_imagga(image_path):
    """
    Analiza una imagen usando la API de Imagga y devuelve las etiquetas más confiables.
    :param image_path: Ruta de la imagen a analizar.
    :return: Lista de etiquetas con sus niveles de confianza (máximo 2 etiquetas).
    """
    IMAGGA_API_KEY = os.getenv("IMAGGA_API_KEY")  # Se espera que las credenciales se configuren en las variables de entorno
    IMAGGA_API_SECRET = os.getenv("IMAGGA_API_SECRET")
    
    if not IMAGGA_API_KEY or not IMAGGA_API_SECRET:
        raise ValueError("Faltan las credenciales de Imagga.")
    
    url = "https://api.imagga.com/v2/tags"

    try:
        with open(image_path, "rb") as image_file:
            # Realizar la solicitud POST a la API de Imagga
            response = requests.post(url, auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET), files={"image": image_file})

        if response.status_code != 200:
            raise Exception(f"Error en la API de Imagga: {response.status_code}, {response.text}")
        
        # Extraer las etiquetas más confiables (las dos primeras)
        tags = response.json().get("result", {}).get("tags", [])
        top_tags = [(tag["tag"]["en"], tag["confidence"]) for tag in tags[:2]]  # Tomar solo las dos primeras etiquetas más confiables

        return top_tags
    
    except FileNotFoundError:
        print(f"Error: La imagen en la ruta {image_path} no se encontró.")
        return []
    except Exception as e:
        print(f"Error al analizar la imagen con Imagga: {e}")
        return []
