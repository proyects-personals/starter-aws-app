from flask import Flask, render_template
from dotenv import load_dotenv
from test.test_connections import test_s3_connection, test_db_connection  # Importación absoluta

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    test_s3_connection()
    test_db_connection()
    return render_template('index.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
