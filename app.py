# app.py
from flask import Flask
from dotenv import load_dotenv
from modules.memes.routes import memes_routes

load_dotenv()

app = Flask(__name__)

app.register_blueprint(memes_routes, url_prefix='/app')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
