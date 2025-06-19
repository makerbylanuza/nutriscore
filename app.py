from flask import Flask, request, render_template
from PIL import Image
import pytesseract
import os
import re

# Importa tu función desde src/main.py
from src.analyser import perform_ocr
from src.analyser import parse_nutritional_info
from src.analyser import calculate_score
from src.analyser import analizar

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    texto_entrada = request.form.get('texto', '').strip()
    imagen = request.files.get('imagen')

    texto_analizar = ""

    if imagen and imagen.filename != '':
        try:
            texto_analizar = perform_ocr(imagen)
        except Exception as e:
            return f"Error al procesar imagen: {str(e)}", 400
    elif texto_entrada:
        texto_analizar = texto_entrada
    else:
        return "No se subió imagen ni se ingresó texto.", 400

    try:
        resultado = analizar(texto_analizar)
    except Exception as e:
        return f"Error al analizar el texto: {str(e)}", 500

    return render_template('resultado.html', resultado=resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
