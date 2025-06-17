# app.py
from PIL import Image
import pytesseract
import os
import re

ingredientes_buscados = {
    # Aceites de semilla
    "aceite de palma": r"aceite de palma|aceite de palmiste|grasa de palma|grasa vegetal (palma)|grasa vegetal fraccionada e hidrogenada de palmiste|estearina de palma|palmoleina|oleina de palma|manteca de palma|elaeis guineensis",
    "aceite de girasol": r"aceite de girasol|aceite de maravilla|aceite de semilla de girasol|helianthus annus",
    "aceite de colza": r"aceite de colza|aceite de nabina|aceite de canola|brassica napus",
    "aceite de soja": r"aceite de soja|aceite de soya|glycine soya oil|óleo de soja|óleo de soya",
    "aceite de maíz": r"aceite de maíz|aceite de rgano de maíz|aceite de zea mays",
    "aceite de sésamo": r"aceite de sésamo|aceite de ajonjolí|aceite de benina|nallennai",
    
    # Azúcares y edulcorantes
    "jarabe de glucosa": r"jarabe de glucosa|jarabe de fructosa|jarabe de maíz|jarabe de glucosa y fructosa|jarabe de glucosa-fructosa|glucosa|fructosa|dextrosa|jarabe de maíz de alta fructosa",
    "sucralosa": r"sucralosa|E955|E-955|E 955",
    "sacarina": r"sacarina|E954|E-954|E 954",
    "aspartamo": r"aspartamo|E951|E-951|E 951",
    "acesulfamo-k": r"acesulfamo k|acesulfamo-k|ace k|ace-k|acesulfamo de potasio|acesulfamo potásico|acesulfame k|acesulfame-k|E950|E-950|E 950",
    "ciclamato": r"ciclamato|ciclohexilsulfamato|sodium cyclamate|E952|E-952|E 952",
    
}

contiene_ingredientes = {

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
    test_image_path = input("imagen: ")

    # Ejecuta el OCR
    extracted_text = perform_ocr(test_image_path)
    print(extracted_text)

    for ingrediente, patron in ingredientes_buscados.items():
        if re.search(patron, extracted_text.lower()):
            print(f"¡Se encontró '{ingrediente}' en los ingredientes!")
        else:
            print(f"'{ingrediente}' no encontrado.")
