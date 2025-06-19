from PIL import Image
import pytesseract
import os
import re

# Funciones
def perform_ocr(image_path):
    """
    Realiza OCR en una imagen dada y devuelve el texto extraído.
    """
    if not os.path.exists(image_path):
        print(f"Error: La imagen '{image_path}' no se encontró.")
        return None

    try:
        # Abrir la imagen
        img = Image.open(image_path.stream)
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
    nutritional_data = {
        "Sal": "",
        "Grasas insaturadas": "",
        "Proteína": "",
        "Fibra": "",
        "Azúcares": ""
    }

    # Patrones de expresiones regulares (insensibles a mayúsculas/minúsculas)
    # --- SAL ---
    salt_pattern = r"(?:Sal|Sodio)\s*[:\-]?\s*(\d+(?:[.,]\d+)?)\s*(mg|g)?"

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
        quantity_str = salt_match.group(1).replace(',', '.').strip()
        unit = salt_match.group(2).lower() if salt_match.group(2) else 'g'
        try:
            if unit == 'mg':
                sodium_mg = float(quantity_str)
                salt_g = sodium_mg * 2.5 / 1000
                nutritional_data["Sal"] = round(salt_g, 2)
            elif unit == 'g':
                nutritional_data["Sal"] = float(quantity_str)
        except ValueError:
            pass  # Keep as empty string if conversion fails

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
            if unsaturated_fats < 0:  # Ensure non-negative
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
        nutritional_data["Grasas insaturadas"] = ""

    return nutritional_data

def calculate_score(avisos):
    score = 0
    # Suma o resta según si lleva los ingredientes
    for i in ingredientes_negativos_contenidos:
        if ingredientes_negativos_contenidos[i] == True:
            score += puntuaciones[i]
            avisos.append(avisos_textos[i])

    for i in ingredientes_positivos_contenidos:
        if ingredientes_positivos_contenidos[i] == True:
            score += puntuaciones[i]
    
    # Sumar o restar según valores nutricionales
    if type(valores_nutricionales["Sal"]) == float:
        if valores_nutricionales["Sal"] < 0.3:
            score += 2
        elif valores_nutricionales["Sal"] > 1.5:
            score -= 2

    if type(valores_nutricionales["Grasas insaturadas"]) == float:
        if valores_nutricionales["Grasas insaturadas"] >= 3 and valores_nutricionales["Grasas insaturadas"] <= 6:
            score += 2
        elif valores_nutricionales["Grasas insaturadas"] > 6:
            score += 4
    
    if type(valores_nutricionales["Proteína"]) == float:
        if valores_nutricionales["Proteína"] > 20:
            score += 5
        elif valores_nutricionales["Proteína"] > 15 and valores_nutricionales["Proteína"] <= 20:
            score += 4
        elif valores_nutricionales["Proteína"] > 10 and valores_nutricionales["Proteína"] <= 15:
            score += 3
        elif valores_nutricionales["Proteína"] > 5 and valores_nutricionales["Proteína"] <= 10:
            score += 2
        elif valores_nutricionales["Proteína"] > 3 and valores_nutricionales["Proteína"] <= 5:
            score += 1
    
    if type(valores_nutricionales["Fibra"]) == float:
        if valores_nutricionales["Fibra"] > 6:
            score += 5
        elif valores_nutricionales["Fibra"] > 3 and valores_nutricionales["Fibra"] <= 6:
            score += 4
        elif valores_nutricionales["Fibra"] > 1.5 and valores_nutricionales["Fibra"] <= 3:
            score += 1
    
    if type(valores_nutricionales["Azúcares"]) == float:
        if valores_nutricionales["Azúcares"] > 22.5:
            score -= 5
        elif valores_nutricionales["Azúcares"] > 15 and valores_nutricionales["Azúcares"] <= 22.5:
            score -= 4
        elif valores_nutricionales["Azúcares"] > 10 and valores_nutricionales["Azúcares"] <= 15:
            score -= 3
        elif valores_nutricionales["Azúcares"] > 5 and valores_nutricionales["Azúcares"] <= 10:
            score -= 1
        
    return score

def analizar(extracted_text):    
    
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
    
    # Busca valores nutricionales y calcula puntuación
    valores_nutricionales = parse_nutritional_info(extracted_text)
    puntos = calculate_score(avisos)
    
    resultado = {
        "valores": valores_nutricionales,
        "puntuacion": puntos,
        "avisos": avisos
    }
    
    return resultado
