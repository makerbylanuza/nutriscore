# app.py
from PIL import Image
import pytesseract
import os
import re

ingredientes_negativos_nombres = {
    # Aceites de semilla
    "aceite de palma": r"aceite de palma|aceite de palmiste|grasa de palma|grasa vegetal (palma)|grasa vegetal fraccionada e hidrogenada de palmiste|estearina de palma|palmoleina|oleina de palma|manteca de palma|elaeis guineensis",
    "aceite de girasol": r"aceite de girasol|aceite de maravilla|aceite de semilla de girasol|helianthus annus",
    "aceite de colza": r"aceite de colza|aceite de nabina|aceite de canola|brassica napus",
    "aceite de soja": r"aceite de soja|aceite de soya|glycine soya oil|óleo de soja|óleo de soya",
    "aceite de maíz": r"aceite de maíz|aceite de grano de maíz|aceite de zea mays",
    "aceite de sésamo": r"aceite de sésamo|aceite de ajonjolí|aceite de benina|nallennai",
    
    # Azúcares y edulcorantes
    "jarabe de glucosa": r"jarabe de glucosa|jarabe de fructosa|jarabe de maíz|jarabe de glucosa y fructosa|jarabe de glucosa-fructosa|glucosa|fructosa|dextrosa|jarabe de maíz de alta fructosa",
    "sucralosa": r"sucralosa|E955|E-955|E 955",
    "sacarina": r"sacarina|E954|E-954|E 954",
    "aspartamo": r"aspartamo|E951|E-951|E 951",
    "acesulfamo-k": r"acesulfamo k|acesulfamo-k|ace k|ace-k|acesulfamo de potasio|acesulfamo potásico|acesulfame k|acesulfame-k|E950|E-950|E 950",
    "ciclamato": r"ciclamato|ciclohexilsulfamato|sodium cyclamate|E952|E-952|E 952",
    
    # Colorantes
    "azorrubina": r"azorrubina|carmoisina|E-122|E 122|E122|rojo 3|rojo ácido 14|brillantcarmoisin o",
    "sacarina": r"sacarina|E954|E-954|E 954",
    "índigo carmín": r"índigo carmín|indigo carmin|índigo carmin|indigo carmín|carmín de índigo|carmin de indigo|carmín de indigo|carmin de índigo|azul índigo|azul indigo|azul ácido 74|indigotina|indigotindisulfonato sódico|ácido 5,5'-indigosulfónico sal disódic",
    "verde s": r"verde s|verde ácido|verde lisamina|E142|E-142|E 142",
    "negro brillante": r"negro brillante|E151|E-151|E 151|negro bn|brilliant black|food black 1",

    # Conservantes y antioxidantes
    "nitratos": r"nitrato|nitratos|E-251|E 251|E251|E-252|E 252|E252",
    "nitritos": r"nitrito|nitritos|E-249|E 249|E249|E-250|E 250|E250",
    "sulfatos": r"sulfato|sulfatos|E-514|E 514|E514",
    "sulfitos": r"sulfito|sulfitos|E-220|E 220|E220|E-221|E 221|E221|E-222|E 222|E222|E-223|E 223|E223|E-224|E 224|E224|E-225|E 225|E225|E-226|E 226|E226|E-227|E 227|E227|E-228|E 228|E228",
    "ácido benzoico": r"acido benzoico|ácido benzoico|E-210|E 210|E210",
    "hidroxibenzoato de metilo sódico": r"hidroxibenzoato de metilo sódico|metilparabeno de sodio|E-219|E 219|E219",
    "benzoato de sodio": r"benzoato de sodio|E-211|E 211|E211",
    "butilhidroxianisol": r"butilhidroxianisol|bha|E-320|E 320|E320",
    "butilhidroxitolueno": r"butilhidroxitolueno|bht|E-321|E 321|E321",

    # Otros
    "grasas trans": r"trans|hidrogenadas|hydrogenated",
}

ingredientes_negativos_contenidos = {

}

ingredientes_positivos_nombres = {
    "stevia": r"stevia|esteviósido|esteviosido|rebaudiósido a|rebaudiosido a|rebaudiósido m|rebaudiosido m|dulcósido|dulcosido|esteviolbiósido|esteviolbiosido|E960|E-960|E 960",
    "eritritol": r"eritritol|eritrita|tetrahidroxibutano|alcohol de azúcar|alcohol de azucar|E968|E-968|E 968",
    "miel": r"miel|honey",
    "canela": r"canela|cinnamon|cinnamomum",
    "frutos secos": r"frutos secos|nuts",
    "avena": r"avena|oats|oatmeal",
    "aceite de oliva virgen extra": r"aceite de oliva virgen extra|aove|evoo|zumo de aceituna",
    "vinagre de manzana": r"vinagre de manzana",
}

ingredientes_positivos_contenidos = {

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
    test_image_path = "tests/data/" + input("imagen: ")

    # Ejecuta el OCR
    extracted_text = perform_ocr(test_image_path)
    print(extracted_text)

    # Busca ingredientes negativos
    ingredientes_negativos_contenidos.clear()
    for ingrediente, patron in ingredientes_negativos_nombres.items():
        if re.search(patron, extracted_text.lower()):
            ingredientes_negativos_contenidos[ingrediente] = True
        else:
            ingredientes_negativos_contenidos[ingrediente] = False

    # Busca ingredientes positivos
    ingredientes_positivos_contenidos.clear()
    for ingrediente, patron in ingredientes_positivos_nombres.items():
        if re.search(patron, extracted_text.lower()):
            ingredientes_positivos_contenidos[ingrediente] = True
        else:
            ingredientes_positivos_contenidos[ingrediente] = False