from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from modules.memes.routes import memes_routes
import os

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la SECRET_KEY para las sesiones
app.config['SECRET_KEY'] = os.urandom(24)  # Genera una clave aleatoria de 24 bytes

# Registrar el blueprint de memes
app.register_blueprint(memes_routes, url_prefix='/app')

# Redirigir la raíz a /app/
@app.route('/')
def index():
    return redirect(url_for('memes_routes.home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
