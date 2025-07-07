import streamlit as st
from utils import cargar_todos_los_json, construir_contexto
import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar la API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Chatbot de Pólizas", layout="centered")

st.title("🤖 Chatbot de Pólizas de Seguro")
st.markdown("Haz preguntas sobre coberturas, preexistencias, vigencias, etc.")

# Cargar documentos
with st.spinner("Cargando pólizas..."):
    documentos = cargar_todos_los_json()

pregunta = st.text_input("📝 Escribe tu pregunta:", "")

if st.button("Responder") and pregunta:
    with st.spinner("Consultando modelo..."):
        contexto = construir_contexto(documentos)

        prompt = f"""
Eres un asistente experto en seguros de viaje. A continuación tienes información en formato JSON sobre distintas pólizas y condiciones generales. Usa esta información para responder con precisión.

Contexto:
{contexto}

Pregunta del usuario:
{pregunta}

Responde de forma clara, basada solo en el contexto proporcionado.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        respuesta = response.choices[0].message.content
        st.markdown("### 📌 Respuesta:")
        st.write(respuesta)