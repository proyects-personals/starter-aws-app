from flask import Blueprint, render_template
from services.meme_service import get_all_memes

# Crear un blueprint para las rutas de memes
memes_routes = Blueprint('memes_routes', __name__)

# Ruta de inicio
@memes_routes.route('/')
def home():
    memes = get_all_memes()
    return render_template('index.html', memes=memes)

# Ruta para la lista de memes
@memes_routes.route('/listas')
def listas():
    memes = get_all_memes()
    print("Datos enviados al template:", memes)
    return render_template('pages/modules/memes/list.html', memes=memes)

# Ruta para la página de memes
@memes_routes.route('/memes')
def memes():
    memes = get_all_memes()
    return render_template('pages/modules/memes/index.html', memes=memes)

# Ruta para crear memes
@memes_routes.route('/crear')
def crear():
    return render_template('pages/modules/memes/crear.html')
