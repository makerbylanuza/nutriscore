# app.py
from PIL import Image
import pytesseract
import os

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
    test_image_path = "test_image.png"

    # Aquí crearíamos una imagen muy simple para fines de ejemplo si no tienes una.
    # En un escenario real, tendrías tus propias imágenes.
    try:
        test_image = Image.new('RGB', (200, 50), color = (255, 255, 255))
        from PIL import ImageDraw, ImageFont
        d = ImageDraw.Draw(test_image)
        # Puedes necesitar especificar una fuente si tienes problemas.
        # Por ejemplo, font = ImageFont.truetype("arial.ttf", 20) si Arial está disponible.
        d.text((10,10), "Hello World!", fill=(0,0,0))
        d.text((10,30), "Hola Mundo!", fill=(0,0,0))
        test_image.save(test_image_path)
        print(f"Imagen de prueba '{test_image_path}' creada.")
    except ImportError:
        print("Advertencia: Pillow parece no estar completamente instalada para dibujar texto. Necesitarás una imagen de prueba existente.")
        print(f"Por favor, añade una imagen llamada '{test_image_path}' a tu repositorio para probar.")

    # Ejecuta el OCR
    extracted_text = perform_ocr(test_image_path)

    if extracted_text:
        print("\n--- Texto Extraído ---")
        print(extracted_text)
    else:
        print("\nNo se pudo extraer texto.")++
