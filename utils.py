import os
import json
import re
from typing import List, Dict, Any

def cargar_todos_los_json(directorio_base="data"):
    """Carga todos los archivos JSON y los estructura mejor"""
    documentos = []

    for empresa in os.listdir(directorio_base):
        ruta_empresa = os.path.join(directorio_base, empresa)
        if os.path.isdir(ruta_empresa):
            for archivo in os.listdir(ruta_empresa):
                if archivo.endswith(".json"):
                    ruta_archivo = os.path.join(ruta_empresa, archivo)
                    try:
                        with open(ruta_archivo, "r", encoding="utf-8") as f:
                            contenido = json.load(f)
                            documentos.append({
                                "company": empresa,
                                "file": archivo,
                                "data": contenido,
                                "search_text": crear_texto_busqueda(contenido, empresa, archivo)
                            })
                    except Exception as e:
                        print(f"Error cargando {ruta_archivo}: {e}")
    return documentos

def crear_texto_busqueda(datos, empresa, archivo):
    """Crea un texto plano para facilitar la búsqueda"""
    texto = f"Empresa: {empresa} Archivo: {archivo} "
    
    def extraer_texto(obj, prefijo=""):
        texto_extraido = ""
        if isinstance(obj, dict):
            for clave, valor in obj.items():
                texto_extraido += f"{prefijo}{clave}: {extraer_texto(valor, prefijo)} "
        elif isinstance(obj, list):
            for item in obj:
                texto_extraido += f"{extraer_texto(item, prefijo)} "
        else:
            texto_extraido += str(obj) + " "
        return texto_extraido
    
    return texto + extraer_texto(datos)

def buscar_documentos_relevantes(documentos, pregunta, max_docs=5):
    """Busca documentos relevantes basándose en palabras clave"""
    # Palabras clave comunes en seguros
    palabras_clave_seguros = {
        'cobertura': ['cobertura', 'cubre', 'incluye', 'protege'],
        'exclusion': ['exclusión', 'excluye', 'no cubre', 'limitación'],
        'vigencia': ['vigencia', 'válido', 'duración', 'período'],
        'preexistencia': ['preexistente', 'preexistencia', 'condición previa'],
        'deducible': ['deducible', 'franquicia', 'copago'],
        'limite': ['límite', 'máximo', 'tope'],
        'emergencia': ['emergencia', 'urgencia', 'accidente'],
        'medico': ['médico', 'hospital', 'clínica', 'doctor', 'salud'],
        'equipaje': ['equipaje', 'maleta', 'pertenencias'],
        'cancelacion': ['cancelación', 'anulación', 'suspensión'],
        'edad': ['edad', 'años', 'menor', 'mayor'],
        'destino': ['destino', 'país', 'región', 'territorio']
    }
    
    pregunta_lower = pregunta.lower()
    
    # Calcular relevancia para cada documento
    docs_con_score = []
    for doc in documentos:
        score = 0
        texto_busqueda = doc['search_text'].lower()
        
        # Puntuación por palabras exactas en la pregunta
        palabras_pregunta = re.findall(r'\b\w+\b', pregunta_lower)
        for palabra in palabras_pregunta:
            if len(palabra) > 3:  # Ignorar palabras muy cortas
                score += texto_busqueda.count(palabra) * 2
        
        # Puntuación por categorías de seguros
        for categoria, sinonimos in palabras_clave_seguros.items():
            if any(palabra in pregunta_lower for palabra in sinonimos):
                for sinonimo in sinonimos:
                    score += texto_busqueda.count(sinonimo) * 3
        
        docs_con_score.append((doc, score))
    
    # Ordenar por relevancia y devolver los más relevantes
    docs_con_score.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in docs_con_score[:max_docs] if score > 0]

def construir_contexto_inteligente(documentos, pregunta, limite_caracteres=8000):
    """Construye contexto más inteligente basado en la pregunta"""
    docs_relevantes = buscar_documentos_relevantes(documentos, pregunta)
    
    if not docs_relevantes:
        # Si no hay documentos relevantes, usar algunos aleatorios
        docs_relevantes = documentos[:3]
    
    contexto = "=== INFORMACIÓN DE PÓLIZAS DE SEGURO ===\n\n"
    
    for doc in docs_relevantes:
        datos = doc["data"]
        nombre_archivo = doc["file"]
        empresa = doc["company"]
        
        contexto += f"📋 EMPRESA: {empresa}\n"
        contexto += f"📄 PÓLIZA: {nombre_archivo.replace('.json', '')}\n"
        contexto += "─" * 50 + "\n"
        
        # Formatear mejor los datos
        contexto += formatear_datos_poliza(datos)
        contexto += "\n" + "=" * 50 + "\n\n"
        
        # Verificar límite de caracteres
        if len(contexto) > limite_caracteres:
            contexto = contexto[:limite_caracteres] + "...\n[INFORMACIÓN TRUNCADA]"
            break
    
    return contexto

def formatear_datos_poliza(datos, nivel=0):
    """Formatea los datos de la póliza de manera más legible"""
    texto = ""
    indent = "  " * nivel
    
    if isinstance(datos, dict):
        for clave, valor in datos.items():
            clave_formateada = clave.replace('_', ' ').title()
            if isinstance(valor, (dict, list)):
                texto += f"{indent}• {clave_formateada}:\n"
                texto += formatear_datos_poliza(valor, nivel + 1)
            else:
                texto += f"{indent}• {clave_formateada}: {valor}\n"
    elif isinstance(datos, list):
        for i, item in enumerate(datos):
            if isinstance(item, (dict, list)):
                texto += f"{indent}  {i+1}. "
                texto += formatear_datos_poliza(item, nivel + 1)
            else:
                texto += f"{indent}  - {item}\n"
    else:
        texto += f"{indent}{datos}\n"
    
    return texto

def extraer_empresas_disponibles(documentos):
    """Extrae lista de empresas disponibles"""
    empresas = set()
    for doc in documentos:
        empresas.add(doc['company'])
    return sorted(list(empresas))

def extraer_tipos_poliza(documentos):
    """Extrae tipos de pólizas disponibles"""
    tipos = set()
    for doc in documentos:
        tipos.add(doc['file'].replace('.json', ''))
    return sorted(list(tipos))

def obtener_estadisticas_base_datos(documentos):
    """Obtiene estadísticas básicas de la base de datos"""
    empresas = extraer_empresas_disponibles(documentos)
    tipos = extraer_tipos_poliza(documentos)
    
    return {
        'total_documentos': len(documentos),
        'total_empresas': len(empresas),
        'empresas': empresas,
        'tipos_poliza': tipos
    }