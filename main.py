import streamlit as st
from utils import (
    cargar_todos_los_json, 
    construir_contexto_inteligente,
    obtener_estadisticas_base_datos,
    extraer_empresas_disponibles,
    extraer_tipos_poliza
)
import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar la API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Chatbot de Pólizas", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Asistente Inteligente de Seguros de Viaje")
st.markdown("Consulta información detallada sobre coberturas, exclusiones, vigencias y más.")

# Cargar documentos (con cache para mejorar performance)
@st.cache_data
def cargar_datos():
    return cargar_todos_los_json()

# Sidebar con información
with st.sidebar:
    st.header("📊 Base de Datos")
    
    with st.spinner("Cargando información..."):
        documentos = cargar_datos()
        stats = obtener_estadisticas_base_datos(documentos)
    
    st.metric("Total de Pólizas", stats['total_documentos'])
    st.metric("Empresas", stats['total_empresas'])
    
    with st.expander("📋 Empresas Disponibles"):
        for empresa in stats['empresas']:
            st.write(f"• {empresa}")
    
    with st.expander("📄 Tipos de Póliza"):
        for tipo in stats['tipos_poliza']:
            st.write(f"• {tipo}")
    
    st.markdown("---")
    st.markdown("### 💡 Ejemplos de Preguntas")
    ejemplos = [
        "¿Qué cubre la póliza básica de Noma Pax?",
        "¿Cuál es la edad máxima para contratar seguro?",
        "¿Qué exclusiones tiene el seguro médico?",
        "¿Cuánto es el deducible para equipaje?",
        "¿Cubre condiciones preexistentes?",
        "¿Qué destinos están incluidos?",
        "¿Cuál es la vigencia máxima?",
        "Compara las coberturas de todas las empresas"
    ]
    
    for i, ejemplo in enumerate(ejemplos):
        if st.button(ejemplo, key=f"ejemplo_btn_{i}"):
            st.session_state['pregunta_seleccionada'] = ejemplo

# Área principal
col1, col2 = st.columns([3, 1])

with col1:
    # Input para la pregunta
    pregunta_inicial = st.session_state.get('pregunta_seleccionada', '')
    pregunta = st.text_area(
        "📝 Escribe tu pregunta sobre seguros:", 
        value=pregunta_inicial,
        height=100,
        placeholder="Ejemplo: ¿Qué cubre la póliza de Pax para emergencias médicas?"
    )
    
    # Limpiar la pregunta ejemplo después de usarla
    if 'pregunta_seleccionada' in st.session_state:
        del st.session_state['pregunta_seleccionada']

with col2:
    st.markdown("### 🎯 Filtros")
    empresas_disponibles = extraer_empresas_disponibles(documentos)
    empresa_filtro = st.selectbox(
        "Filtrar por empresa:",
        ["Todas"] + empresas_disponibles
    )
    
    incluir_comparacion = st.checkbox("Incluir comparación entre empresas", value=True)

if st.button("🔍 Consultar", type="primary") and pregunta:
    with st.spinner("Analizando información..."):
        # Filtrar documentos si se seleccionó una empresa específica
        docs_filtrados = documentos
        if empresa_filtro != "Todas":
            docs_filtrados = [doc for doc in documentos if doc['company'] == empresa_filtro]
        
        # Construir contexto inteligente
        contexto = construir_contexto_inteligente(docs_filtrados, pregunta)
        
        # Crear prompt mejorado
        prompt = f"""
Eres un asistente experto en seguros de viaje con amplia experiencia en pólizas, coberturas y regulaciones.

INSTRUCCIONES IMPORTANTES:
1. Responde SOLO basándote en la información proporcionada
2. Si no tienes información específica, dilo claramente
3. Sé preciso con números, montos y porcentajes
4. Identifica claramente qué empresa y póliza aplica para cada información
5. Si hay diferencias entre empresas, compáralas claramente
6. Usa un formato estructurado y fácil de leer

CONTEXTO DE PÓLIZAS:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

FORMATO DE RESPUESTA:
- Usa emojis para hacer más clara la información
- Estructura la respuesta con títulos y subtítulos
- Incluye tablas comparativas cuando sea relevante
- Menciona siempre la fuente (empresa y póliza)
- Si hay información contradictoria, señálala

Responde de forma profesional pero accesible:
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Más determinista
                max_tokens=1500
            )
            respuesta = response.choices[0].message.content
            
            # Mostrar respuesta
            st.markdown("### 📌 Respuesta:")
            st.markdown(respuesta)
            
            # Mostrar información adicional
            with st.expander("🔍 Información Técnica"):
                st.markdown("**Documentos consultados:**")
                docs_relevantes = [doc for doc in docs_filtrados if any(palabra in doc['search_text'].lower() for palabra in pregunta.lower().split())]
                for doc in docs_relevantes[:5]:  # Mostrar máximo 5
                    st.write(f"• {doc['company']} - {doc['file']}")
                
                st.markdown("**Tokens utilizados:**")
                st.write(f"Contexto: ~{len(contexto)//4} tokens")
                st.write(f"Respuesta: ~{len(respuesta)//4} tokens")
            
        except Exception as e:
            st.error(f"Error al procesar la consulta: {e}")
            st.info("Verifica que tu API key de OpenAI esté correctamente configurada.")

# Área de ayuda
st.markdown("---")
with st.expander("❓ Ayuda y Consejos"):
    st.markdown("""
    ### 🎯 Cómo hacer mejores preguntas:
    
    **✅ Preguntas específicas:**
    - "¿Cuál es el límite de cobertura médica en la póliza Premium de Noma?"
    - "¿Qué exclusiones tiene el seguro de equipaje?"
    
    **✅ Preguntas comparativas:**
    - "Compara las coberturas médicas entre todas las empresas"
    - "¿Qué empresa tiene mejor cobertura para cancelación?"
    
    **✅ Preguntas contextuales:**
    - "Soy mayor de 70 años, ¿qué opciones tengo?"
    - "Voy a Europa por 6 meses, ¿qué póliza me conviene?"
    
    **❌ Evita preguntas muy vagas:**
    - "¿Qué cubre?" (muy general)
    - "¿Es bueno?" (subjetivo)
    """)

# Footer
st.markdown("---")
st.markdown("*Asistente desarrollado para consultas de seguros de viaje. Siempre verifica la información directamente con la aseguradora.*")