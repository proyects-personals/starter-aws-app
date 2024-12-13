from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.meme_service import get_all_memes, create_meme, search_memes

memes_routes = Blueprint('memes_routes', __name__)

@memes_routes.route('/', methods=['GET'])
def home():
    search_query = request.args.get('search', '')
    confianza = request.args.get('confianza', None)

    if search_query:
        # Si hay un parámetro de búsqueda, se filtran los memes
        query = {
            'search': search_query,
            'confianza': int(confianza) if confianza else None
        }
        memes = search_memes(query)
    else:
        # Si no hay búsqueda, mostrar todos los memes
        memes = get_all_memes()

    return render_template('index.html', memes=memes)

@memes_routes.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        usuario = request.form['usuario']
        imagen_file = request.files['imagen']
        etiquetas = request.form['etiquetas'].split(',')
        meme_id = create_meme(descripcion, usuario, imagen_file, True, etiquetas)

        if meme_id:
            flash('Meme creado con éxito', 'success')
            return redirect(url_for('memes_routes.home'))
        else:
            flash('Error al crear el meme', 'error')

    return render_template('pages/modules/memes/crear.html')
