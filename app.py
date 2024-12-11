from flask import Flask, render_template
from dotenv import load_dotenv
from services.meme_service import get_all_memes

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    # Obtener los memes desde la base de datos
    memes = get_all_memes()
    return render_template('index.html', memes=memes)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
