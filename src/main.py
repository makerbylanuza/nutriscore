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

valores_nutricionales = {

}

puntuaciones = {
    # Aceites de semilla
    "aceite de palma": -7,
    "aceite de girasol": -3,
    "aceite de colza": -2,
    "aceite de soja": -3,
    "aceite de maíz": -3,
    "aceite de sésamo": -2,
    
    # Azúcares y edulcorantes
    "jarabe de glucosa": -8,
    "sucralosa": -4,
    "sacarina": -5,
    "aspartamo": -3,
    "acesulfamo-k": -3,
    "ciclamato": -5,
    
    # Colorantes
    "azorrubina": -6,
    "índigo carmín": -5,
    "verde s": -6,
    "negro brillante": -7,

    # Conservantes y antioxidantes
    "nitratos": -7,
    "nitritos": -7,
    "sulfatos": -2,
    "sulfitos": -4,
    "ácido benzoico": -4,
    "hidroxibenzoato de metilo sódico": -3,
    "benzoato de sodio": -4,
    "butilhidroxianisol": -7,
    "butilhidroxitolueno": -7,

    # Otros
    "grasas trans": -15,

    # Ingredientes positivos
    "stevia": 4,
    "eritritol": 3,
    "miel": 2,
    "canela": 2,
    "frutos secos": 4,
    "avena": 3,
    "aceite de oliva virgen extra": 5,
    "vinagre de manzana": 2,
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

def parse_nutritional_info(text):
    """
    Extrae la información nutricional (sal, grasas insaturadas, proteína, fibra y azúcares)
    de un texto dado.

    Args:
        text (str): El texto que contiene la declaración nutrimental.

    Returns:
        dict: Un diccionario con las cantidades de sal, grasas insaturadas, proteína, fibra y azúcares.
              Las claves serán 'Sal', 'Grasas insaturadas', 'Proteína', 'Fibra' y 'Azúcares'.
              Los valores serán la cantidad encontrada (como float) o None si no se detecta.
    """
    nutritional_data = {
        "Sal": None,
        "Grasas insaturadas": None,
        "Proteína": None,
        "Fibra": None,
        "Azúcares": None
    }

    # Patrones de expresiones regulares (insensibles a mayúsculas/minúsculas)
    # --- SAL ---
    salt_pattern = r"(?:Sal|Sodio)\s*([\d,\.]+)\s*(mg|g)?"

    # --- GRASAS ---
    total_fats_pattern = r"(?:Grasa(?:s)?\s*totales|Grasa(?:s)?)\s*([\d,\.]+)\s*g"
    saturated_fats_pattern = r"(?:Grasa(?:s)?\s*saturada(?:s)?|de las cuales saturada(?:s)?)\s*([\d,\.]+)\s*g"
    mono_fats_pattern = r"(?:Grasa(?:s)?\s*monoinsaturada(?:s)?|de las cuales monoinsaturada(?:s)?)\s*([\d,\.]+)\s*g"
    poly_fats_pattern = r"(?:Grasa(?:s)?\s*poliinsaturada(?:s)?|de las cuales poliinsaturada(?:s)?)\s*([\d,\.]+)\s*g"
    direct_unsaturated_fats_pattern = r"(?:Grasa(?:s)?\s*insaturada(?:s)?|de las cuales insaturada(?:s)?)\s*([\d,\.]+)\s*g"

    # --- PROTEÍNA ---
    protein_pattern = r"Prote[ií]nas?\s*([\d,\.]+)\s*g"

    # --- FIBRA ---
    fiber_pattern = r"(?:Fibra alimentaria|Fibra dietética|Fibra)\s*([\d,\.]+)\s*g"

    # --- AZÚCARES ---
    sugars_pattern = r"Az[uú]car(?:es)?\s*([\d,\.]+)\s*g"


    # --- Extracción de valores ---

    # Sal
    salt_match = re.search(salt_pattern, text, re.IGNORECASE)
    if salt_match:
        quantity_str = salt_match.group(1).replace(',', '.')
        unit = salt_match.group(2).lower() if salt_match.group(2) else 'g'
        try:
            if unit == 'mg':
                sodium_mg = float(quantity_str)
                salt_g = sodium_mg * 2.5 / 1000
                nutritional_data["Sal"] = round(salt_g, 2)
            elif unit == 'g':
                nutritional_data["Sal"] = float(quantity_str)
        except ValueError:
            pass # Keep as None if conversion fails

    # Azúcares
    sugars_match = re.search(sugars_pattern, text, re.IGNORECASE)
    if sugars_match:
        try:
            nutritional_data["Azúcares"] = float(sugars_match.group(1).replace(',', '.'))
        except ValueError:
            pass

    # Proteína
    protein_match = re.search(protein_pattern, text, re.IGNORECASE)
    if protein_match:
        try:
            nutritional_data["Proteína"] = float(protein_match.group(1).replace(',', '.'))
        except ValueError:
            pass

    # Fibra
    fiber_match = re.search(fiber_pattern, text, re.IGNORECASE)
    if fiber_match:
        try:
            nutritional_data["Fibra"] = float(fiber_match.group(1).replace(',', '.'))
        except ValueError:
            pass

    # Grasas insaturadas
    unsaturated_fats = None

    direct_unsaturated_match = re.search(direct_unsaturated_fats_pattern, text, re.IGNORECASE)
    if direct_unsaturated_match:
        try:
            unsaturated_fats = float(direct_unsaturated_match.group(1).replace(',', '.'))
        except ValueError:
            pass

    if unsaturated_fats is None:
        mono_fats_match = re.search(mono_fats_pattern, text, re.IGNORECASE)
        poly_fats_match = re.search(poly_fats_pattern, text, re.IGNORECASE)

        mono_val = 0.0
        poly_val = 0.0

        if mono_fats_match:
            try:
                mono_val = float(mono_fats_match.group(1).replace(',', '.'))
            except ValueError:
                pass
        if poly_fats_match:
            try:
                poly_val = float(poly_fats_match.group(1).replace(',', '.'))
            except ValueError:
                pass

        if mono_fats_match or poly_fats_match:
            unsaturated_fats = mono_val + poly_val
            if unsaturated_fats < 0: # Ensure non-negative
                unsaturated_fats = None

    if unsaturated_fats is None:
        total_fats_match = re.search(total_fats_pattern, text, re.IGNORECASE)
        saturated_fats_match = re.search(saturated_fats_pattern, text, re.IGNORECASE)

        if total_fats_match and saturated_fats_match:
            try:
                total_fats = float(total_fats_match.group(1).replace(',', '.'))
                saturated_fats = float(saturated_fats_match.group(1).replace(',', '.'))
                calculated_unsaturated = total_fats - saturated_fats
                if calculated_unsaturated >= 0:
                    unsaturated_fats = calculated_unsaturated
            except ValueError:
                pass

    if isinstance(unsaturated_fats, float):
        nutritional_data["Grasas insaturadas"] = round(unsaturated_fats, 2)
    else:
        nutritional_data["Grasas insaturadas"] = None

    return nutritional_data

def calculate_score():
    score = 0
    # Suma o resta según si lleva los ingredientes
    for i in ingredientes_negativos_contenidos:
        if ingredientes_negativos_contenidos[i] == True:
            score += puntuaciones[i]

    for i in ingredientes_positivos_contenidos:
        if ingredientes_positivos_contenidos[i] == True:
            score += puntuaciones[i]
    
    # Sumar o restar según valores nutricionales
    if valores_nutricionales["Sal"] < 0.3:
        score += 2
    elif valores_nutricionales["Sal"] > 1.5:
        score -= 2

    if valores_nutricionales["Grasas insaturadas"] >= 3 and valores_nutricionales["Grasas insaturadas"] <= 6:
        score += 2
    elif valores_nutricionales["Grasas insaturadas"] > 6:
        score += 4
    
    # AQUI AUN HAY CODIGO POR ESCRIBIR

    return score

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
    
    # Busca valores nutricionales
    valores_nutricionales = parse_nutritional_info(extracted_text)

    print(calculate_score())

    