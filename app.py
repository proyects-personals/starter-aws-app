from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from modules.memes.routes import memes_routes

load_dotenv()

app = Flask(__name__)

app.register_blueprint(memes_routes, url_prefix='/app')

# Redirigir la raíz a /app/
@app.route('/')
def index():
    return redirect(url_for('memes_routes.home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
