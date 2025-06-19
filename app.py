from flask import Flask, request, render_template
from PIL import Image
import pytesseract
import os
import re

ingredientes_negativos_nombres = {
    # Aceites de semilla
    "aceite de palma": r"aceite de palma|aceite de palmiste|grasa de palma|grasa vegetal (palma)|grasa vegetal fraccionada e hidrogenada de palmiste|estearina de palma|palmoleina|oleina de palma|manteca de palma|elaeis guineensis",
    "aceite de girasol": r"aceite de girasol|aceite de maravilla|aceite de semilla de girasol|helianthus annus",
    "aceite de colza": r"aceite de colza|aceite de nabina|aceite de canola|brassica napus",
    "aceite de soja": r"aceite de soja|aceite de soya|glycine soya oil|óleo de soja|óleo de soya|aceite vegetal (soja)",
    "aceite de maíz": r"aceite de maíz|aceite de grano de maíz|aceite de zea mays",
    "aceite de sésamo": r"aceite de sésamo|aceite de ajonjolí|aceite de benina|nallennai",
    
    # Azúcares y edulcorantes
    "jarabe de glucosa": r"jarabe de glucosa|jarabe de fructosa|jarabe de maíz|jarabe de glucosa y fructosa|jarabe de glucosa-fructosa|glucosa|fructosa|dextrosa|jarabe de maíz de alta fructosa",
    "sucralosa": r"sucralosa|e955|e-955|e 955",
    "sacarina": r"sacarina|e954|e-954|e 954",
    "aspartamo": r"aspartamo|e951|e-951|e 951",
    "acesulfamo-k": r"acesulfamo k|acesulfamo-k|ace k|ace-k|acesulfamo de potasio|acesulfamo potásico|acesulfame k|acesulfame-k|e950|e-950|e 950",
    "ciclamato": r"ciclamato|ciclohexilsulfamato|sodium cyclamate|e952|e-952|e 952",
    
    # Colorantes
    "azorrubina": r"azorrubina|carmoisina|e-122|e 122|e122|rojo 3|rojo ácido 14|brillantcarmoisin o",
    "índigo carmín": r"índigo carmín|indigo carmin|índigo carmin|indigo carmín|carmín de índigo|carmin de indigo|carmín de indigo|carmin de índigo|azul índigo|azul indigo|azul ácido 74|indigotina|indigotindisulfonato sódico|ácido 5,5'-indigosulfónico sal disódic",
    "verde s": r"verde s|verde ácido|verde lisamina|e142|e-142|e 142",
    "negro brillante": r"negro brillante|e151|e-151|e 151|negro bn|brilliant black|food black 1",

    # Conservantes y antioxidantes
    "nitratos": r"nitrato|nitratos|e-251|e 251|e251|e-252|e 252|e252",
    "nitritos": r"nitrito|nitritos|e-249|e 249|e249|e-250|e 250|e250",
    "sulfatos": r"sulfato|sulfatos|e-514|e 514|e514",
    "sulfitos": r"sulfito|sulfitos|e-220|e 220|e220|e-221|e 221|e221|e-222|e 222|e222|e-223|e 223|e223|e-224|e 224|e224|e-225|e 225|e225|e-226|e 226|e226|e-227|e 227|e227|e-228|e 228|e228",
    "ácido benzoico": r"acido benzoico|ácido benzoico|e-210|e 210|e210",
    "hidroxibenzoato de metilo sódico": r"hidroxibenzoato de metilo sódico|metilparabeno de sodio|e-219|e 219|e219",
    "benzoato de sodio": r"benzoato de sodio|e-211|e 211|e211",
    "butilhidroxianisol": r"butilhidroxianisol|bha|e-320|e 320|e320",
    "butilhidroxitolueno": r"butilhidroxitolueno|bht|e-321|e 321|e321",

    # Otros
    "grasas trans": r"trans|hidrogenadas|hydrogenated",
}

ingredientes_negativos_contenidos = {

}

ingredientes_positivos_nombres = {
    "stevia": r"stevia|esteviósido|esteviosido|rebaudiósido a|rebaudiosido a|rebaudiósido m|rebaudiosido m|dulcósido|dulcosido|esteviolbiósido|esteviolbiosido|e960|e-960|e 960",
    "eritritol": r"eritritol|eritrita|tetrahidroxibutano|alcohol de azúcar|alcohol de azucar|e968|e-968|e 968",
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

avisos_textos = {
    # Aceites de semilla
    "aceite de palma": "Los aceites de semilla refinados como el de girasol, maíz, soja o canola pueden ser perjudiciales porque contienen grandes cantidades de omega-6, lo que favorece la inflamación si se consumen en exceso. Además, son inestables al calor y, al cocinarse, generan compuestos tóxicos que pueden dañar las células. Su extracción industrial con químicos también afecta su calidad. Un estudio publicado en BMJ (Ramsden et al., 2013) mostró que un alto consumo de estos aceites puede aumentar el riesgo de enfermedades cardíacas. Se recomienda limitar su consumo y preferir grasas extraídas sin procedimientos químicos, como el aceite de oliva.",
    "aceite de girasol": "Los aceites de semilla refinados como el de girasol, maíz, soja o canola pueden ser perjudiciales porque contienen grandes cantidades de omega-6, lo que favorece la inflamación si se consumen en exceso. Además, son inestables al calor y, al cocinarse, generan compuestos tóxicos que pueden dañar las células. Su extracción industrial con químicos también afecta su calidad. Un estudio publicado en BMJ (Ramsden et al., 2013) mostró que un alto consumo de estos aceites puede aumentar el riesgo de enfermedades cardíacas. Se recomienda limitar su consumo y preferir grasas extraídas sin procedimientos químicos, como el aceite de oliva.",
    "aceite de colza": "Los aceites de semilla refinados como el de girasol, maíz, soja o canola pueden ser perjudiciales porque contienen grandes cantidades de omega-6, lo que favorece la inflamación si se consumen en exceso. Además, son inestables al calor y, al cocinarse, generan compuestos tóxicos que pueden dañar las células. Su extracción industrial con químicos también afecta su calidad. Un estudio publicado en BMJ (Ramsden et al., 2013) mostró que un alto consumo de estos aceites puede aumentar el riesgo de enfermedades cardíacas. Se recomienda limitar su consumo y preferir grasas extraídas sin procedimientos químicos, como el aceite de oliva.",
    "aceite de soja": "Los aceites de semilla refinados como el de girasol, maíz, soja o canola pueden ser perjudiciales porque contienen grandes cantidades de omega-6, lo que favorece la inflamación si se consumen en exceso. Además, son inestables al calor y, al cocinarse, generan compuestos tóxicos que pueden dañar las células. Su extracción industrial con químicos también afecta su calidad. Un estudio publicado en BMJ (Ramsden et al., 2013) mostró que un alto consumo de estos aceites puede aumentar el riesgo de enfermedades cardíacas. Se recomienda limitar su consumo y preferir grasas extraídas sin procedimientos químicos, como el aceite de oliva.",
    "aceite de maíz": "Los aceites de semilla refinados como el de girasol, maíz, soja o canola pueden ser perjudiciales porque contienen grandes cantidades de omega-6, lo que favorece la inflamación si se consumen en exceso. Además, son inestables al calor y, al cocinarse, generan compuestos tóxicos que pueden dañar las células. Su extracción industrial con químicos también afecta su calidad. Un estudio publicado en BMJ (Ramsden et al., 2013) mostró que un alto consumo de estos aceites puede aumentar el riesgo de enfermedades cardíacas. Se recomienda limitar su consumo y preferir grasas extraídas sin procedimientos químicos, como el aceite de oliva.",
    "aceite de sésamo": "Los aceites de semilla refinados como el de girasol, maíz, soja o canola pueden ser perjudiciales porque contienen grandes cantidades de omega-6, lo que favorece la inflamación si se consumen en exceso. Además, son inestables al calor y, al cocinarse, generan compuestos tóxicos que pueden dañar las células. Su extracción industrial con químicos también afecta su calidad. Un estudio publicado en BMJ (Ramsden et al., 2013) mostró que un alto consumo de estos aceites puede aumentar el riesgo de enfermedades cardíacas. Se recomienda limitar su consumo y preferir grasas extraídas sin procedimientos químicos, como el aceite de oliva.",
    
    # Azúcares y edulcorantes
    "jarabe de glucosa": "Los jarabes de glucosa y fructosa se utilizan para dar sabor dulce a los alimentos procesados, pero muchos de ellos, como la sacarosa, los jarabes de glucosa o fructosa y el jarabe de maíz de alta fructosa, son tipos de azúcares simples que el cuerpo absorbe muy rápido. Esto provoca picos de azúcar en sangre y, con el tiempo, puede aumentar el riesgo de obesidad, caries, resistencia a la insulina, diabetes tipo 2, hígado graso y enfermedades cardiovasculares. Todos estos ingredientes se usan mucho porque son baratos y realzan el sabor, pero su uso frecuente está relacionado con efectos negativos en la salud. Por eso, organizaciones como la OMS, la EFSA y la American Heart Association recomiendan limitar su consumo, especialmente en niños.",
    "sucralosa": "La sucralosa es un edulcorante artificial sin calorías, mucho más dulce que el azúcar. Aunque no sube el azúcar en sangre, algunos estudios sugieren que podría afectar la microbiota intestinal o generar compuestos tóxicos si se calienta.",
    "sacarina": "La sacarina es uno de los edulcorantes más antiguos. Es hasta 300 veces más dulce que el azúcar y no aporta calorías. Se puede usar hasta 9 mg por kilo de peso al día, según la EFSA. Hace años se pensaba que podía causar cáncer de vejiga en animales, pero hoy se considera segura en humanos. Aun así, en algunas personas puede causar sabor metálico o reacciones alérgicas leves.",
    "aspartamo": "El aspartamo es un edulcorante muy usado en refrescos, chicles y productos “sin azúcar”. Es entre 150 y 200 veces más dulce que el azúcar. La EFSA (Agencia Europea de Seguridad Alimentaria) dice que se puede consumir hasta 40 mg por kilo de peso al día sin problemas. Sin embargo, hay estudios que lo relacionan con cáncer en animales, y por eso la OMS lo clasifica como posiblemente cancerígeno. Las personas con una enfermedad genética llamada fenilcetonuria no deben consumirlo, porque su cuerpo no puede procesarlo bien.",
    "acesulfamo-k": "Este edulcorante se usa en muchos productos bajos en calorías, como postres, yogures o bebidas. No aporta calorías y es unas 200 veces más dulce que el azúcar. La cantidad máxima recomendada es de 15 mg por kilo de peso al día. Está aprobado por organizaciones como la EFSA y la FDA (Estados Unidos). No hay pruebas sólidas de que cause cáncer, pero algunos estudios recientes están investigando si puede afectar a las bacterias del intestino.",
    "ciclamato": "El ciclamato es otro edulcorante que se usa en productos sin azúcar. Su dulzor es más suave y a veces se combina con otros edulcorantes. La cantidad máxima recomendada es de 7 mg por kilo de peso al día. Está prohibido en Estados Unidos desde hace décadas, ya que algunos estudios antiguos en animales lo relacionaron con cáncer, aunque hoy no hay pruebas claras en humanos. En Europa sigue permitido pero se usa con precaución.",
    
    # Colorantes
    "azorrubina": "La azorrubina o carmoisina es un colorante rojo artificial usado en chucherías, postres y bebidas. Aunque se permite su uso, algunas personas sensibles pueden tener reacciones alérgicas, sobre todo niños con asma o intolerancia a ciertos aditivos. La cantidad máxima recomendada es de 4 mg por kilo de peso al día. Está aprobado en Europa, pero se desaconseja su uso frecuente en niños.",
    "índigo carmín": "El índigo carmín es un colorante azul artificial que se usa en dulces, bebidas y algunos postres. En algunas personas sensibles puede causar reacciones alérgicas o problemas respiratorios. Su consumo excesivo no se recomienda, especialmente en niños.",
    "verde s": "El Verde S es un colorante verde sintético usado en golosinas, bebidas y productos de panadería. Puede provocar reacciones alérgicas y en algunos países está prohibido por posibles efectos negativos sobre la salud, especialmente en niños.",
    "negro brillante": "El negro brillante es un colorante negro artificial presente en caramelos, salsas o postres. Se ha relacionado con alergias y efectos negativos en personas asmáticas. Está prohibido en algunos países por preocupaciones sobre su seguridad a largo plazo.",

    # Conservantes y antioxidantes
    "nitratos": "Los nitratos y nitritos se usan como conservantes en embutidos, salchichas y carnes curadas. Ayudan a que la carne mantenga su color y evitan el crecimiento de bacterias peligrosas. El problema es que en el cuerpo pueden transformarse en nitrosaminas, sustancias que podrían aumentar el riesgo de cáncer. La cantidad máxima recomendada es de 3.7 mg/kg/día para nitratos y 0.07 mg/kg/día para nitritos. Se recomienda limitar su consumo, especialmente en niños.",
    "nitritos": "Los nitratos y nitritos se usan como conservantes en embutidos, salchichas y carnes curadas. Ayudan a que la carne mantenga su color y evitan el crecimiento de bacterias peligrosas. El problema es que en el cuerpo pueden transformarse en nitrosaminas, sustancias que podrían aumentar el riesgo de cáncer. La cantidad máxima recomendada es de 3.7 mg/kg/día para nitratos y 0.07 mg/kg/día para nitritos. Se recomienda limitar su consumo, especialmente en niños.",
    "sulfatos": "Los sulfitos y sulfatos son conservantes usados en alimentos como frutas secas, vinos, embutidos y productos procesados para evitar que se oxiden o fermenten. Aunque están aprobados en pequeñas cantidades, pueden causar reacciones adversas, especialmente en personas sensibles o asmáticas, como dolores de cabeza, dificultad para respirar o urticaria. Su consumo excesivo también puede alterar la microbiota intestinal. La EFSA establece una ingesta diaria aceptable (IDA) de 0.7 mg por kilo de peso corporal. Por precaución, se recomienda evitar productos con sulfitos frecuentes, sobre todo en niños y personas con alergias respiratorias.",
    "sulfitos": "Los sulfitos y sulfatos son conservantes usados en alimentos como frutas secas, vinos, embutidos y productos procesados para evitar que se oxiden o fermenten. Aunque están aprobados en pequeñas cantidades, pueden causar reacciones adversas, especialmente en personas sensibles o asmáticas, como dolores de cabeza, dificultad para respirar o urticaria. Su consumo excesivo también puede alterar la microbiota intestinal. La EFSA establece una ingesta diaria aceptable (IDA) de 0.7 mg por kilo de peso corporal. Por precaución, se recomienda evitar productos con sulfitos frecuentes, sobre todo en niños y personas con alergias respiratorias.",
    "ácido benzoico": "El ácido benzoico o E210 es un conservante que se usa para evitar que crezcan bacterias en refrescos, jugos y salsas. Puede causar alergias, irritación en la piel o problemas respiratorios en personas sensibles.",
    "hidroxibenzoato de metilo sódico": "El E219 es una sal del ácido p-hidroxibenzoico, usada como conservante antimicrobiano. Puede generar reacciones alérgicas y, aunque no está del todo prohibido, su uso está muy regulado por posibles efectos hormonales.",
    "benzoato de sodio": "El benzoato de sodio es un conservante muy común en refrescos y productos ácidos. Puede causar hiperactividad en niños y, si se mezcla con vitamina C, puede formar benceno, una sustancia potencialmente cancerígena.",
    "butilhidroxianisol": "El butilhidroxianisol o E320 se usa para evitar que las grasas se enrancien en cereales, snacks y chicles. Está relacionado con posibles efectos cancerígenos en estudios con animales y puede afectar el sistema hormonal.",
    "butilhidroxitolueno": "El butilhidroxitolueno o BHT es un compuesto similar al BHA, este antioxidante se encuentra en muchos productos procesados. Hay estudios que lo relacionan con alteraciones hormonales y posibles efectos negativos sobre el hígado y los riñones.",

    # Otros
    "grasas trans": -15,
}

# Funciones
def perform_ocr(file_storage):
    """
    Realiza OCR en una imagen dada (FileStorage) y devuelve el texto extraído.
    """
    try:
        img = Image.open(file_storage.stream)  # 👈 esto ya es correcto
        print(f"Imagen '{file_storage.filename}' cargada con éxito.")

        text = pytesseract.image_to_string(img, lang='eng+spa')
        return text

    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract no está instalado o no se encuentra en el PATH.")
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
            pass

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

avisos = []

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
        # Busca ingredientes negativos
        ingredientes_negativos_contenidos.clear()
        for ingrediente, patron in ingredientes_negativos_nombres.items():
            if re.search(patron, texto_analizar.lower()):
                ingredientes_negativos_contenidos[ingrediente] = True
            else:
                ingredientes_negativos_contenidos[ingrediente] = False
        
        # Busca ingredientes positivos
        ingredientes_positivos_contenidos.clear()
        for ingrediente, patron in ingredientes_positivos_nombres.items():
            if re.search(patron, texto_analizar.lower()):
                ingredientes_positivos_contenidos[ingrediente] = True
            else:
                ingredientes_positivos_contenidos[ingrediente] = False
        
        # Busca valores nutricionales y calcula puntuación
        global valores_nutricionales
        valores_nutricionales = parse_nutritional_info(texto_analizar)
        puntos = calculate_score(avisos)
        
        resultado = {
            "valores": valores_nutricionales,
            "puntuacion": puntos,
            "avisos": avisos
        }
        
    except Exception as e:
        return f"Error al analizar el texto: {str(e)}", 500

    return render_template('resultado.html', resultado=resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
