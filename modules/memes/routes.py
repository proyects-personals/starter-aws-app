from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.meme_service import get_all_memes, create_meme

memes_routes = Blueprint('memes_routes', __name__)

@memes_routes.route('/')
def home():
    memes = get_all_memes()
    return render_template('index.html', memes=memes)

@memes_routes.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        # Recoger los datos del formulario
        descripcion = request.form['descripcion']
        usuario = request.form['usuario']
        imagen_file = request.files['imagen']
        etiquetas = request.form['etiquetas'].split(',')
        confianza = list(map(int, request.form['confianza'].split(',')))

        meme_id = create_meme(descripcion, usuario, imagen_file, True, list(zip(etiquetas, confianza)))

        if meme_id:
            flash('Meme creado con éxito', 'success')
            return redirect(url_for('memes_routes.home'))
        else:
            flash('Error al crear el meme', 'error')

    return render_template('pages/modules/memes/crear.html')
