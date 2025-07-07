import os
import json

def cargar_todos_los_json(directorio_base="data"):
    documentos = []

    for empresa in os.listdir(directorio_base):
        ruta_empresa = os.path.join(directorio_base, empresa)
        if os.path.isdir(ruta_empresa):
            for archivo in os.listdir(ruta_empresa):
                if archivo.endswith(".json"):
                    ruta_archivo = os.path.join(ruta_empresa, archivo)
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        contenido = json.load(f)
                        documentos.append({
                            "company": empresa,
                            "file": archivo,
                            "data": contenido
                        })
    return documentos

def construir_contexto(documentos, limite_caracteres=6000):
    contexto = ""
    for doc in documentos:
        datos = doc["data"]
        nombre_archivo = doc["file"]
        empresa = doc["company"]
        contexto += f"---\nEmpresa: {empresa}\nArchivo: {nombre_archivo}\n"
        for k, v in datos.items():
            contexto += f"{k}: {v}\n"
    return contexto[:limite_caracteres]