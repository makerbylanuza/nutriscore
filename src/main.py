# app.py
from PIL import Image
import pytesseract
import os
import re

nombres_aceites = {
    "aceite de palma": r"aceite de palma",
    "aceite de girasol": r"aceite de girasol",
    "aceite de colza": r"aceite de colza",
    "aceite de soja": r"aceite de soja",
    "aceite de maíz": r"aceite de maíz",
    "aceite de sésamo": r"aceite de sésamo",
}

contiene_aceites = {

}

# --- Configuración (opcional pero recomendado) ---
# Si Tesseract no está en tu PATH, puedes especificar su ubicación
# En un Codespace con la configuración anterior, probablemente no sea necesario
# pero es bueno saberlo.
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def perform_ocr(image_path):
    """
    Realiza OCR en una imagen dada y devuelve el texto extraído.
    """
    if not os.path.exists(image_path):
        print(f"Error: La imagen '{image_path}' no se encontró.")
        return None

    try:
        # Abrir la imagen
        img = Image.open(image_path)
        print(f"Imagen '{image_path}' cargada con éxito.")

        # Realizar OCR
        # lang='eng+spa' le dice a Tesseract que use datos de idioma inglés y español
        text = pytesseract.image_to_string(img, lang='eng+spa')
        return text
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract no está instalado o no se encuentra en el PATH.")
        print("Asegúrate de que 'tesseract-ocr' esté instalado en tu Codespace.")
        return None
    except Exception as e:
        print(f"Ocurrió un error durante el OCR: {e}")
        return None

if __name__ == "__main__":
    # Crea una imagen de prueba simple (o usa una existente)
    # Para probar, podrías tener una imagen .png o .jpg en tu repositorio
    # Por ejemplo, una imagen llamada 'test_image.png'
    test_image_path = "tests/data/patatas.png"

    # Ejecuta el OCR
    extracted_text = perform_ocr(test_image_path)

    for aceite, patron in nombres_aceites.items():
        if re.search(patron, extracted_text.lower()):
            print(f"¡Se encontró '{aceite}' en los ingredientes!")
        else:
            print(f"'{aceite}' no encontrado.")
