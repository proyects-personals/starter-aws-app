from flask import Blueprint, render_template
from services.meme_service import get_all_memes

memes_routes = Blueprint('memes_routes', __name__)

@memes_routes.route('/')
def home():
    memes = get_all_memes()
    return render_template('index.html', memes=memes)

@memes_routes.route('/crear')
def crear():
    return render_template('pages/modules/memes/crear.html')
