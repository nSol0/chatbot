import streamlit as st
import requests
from datetime import datetime

# === CONFIGURACIÓN DE API (OpenRouter) ===
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY") or st.sidebar.text_input(
    "🔑 Ingresa tu API Key de OpenRouter", 
    type="password",
    help="Puedes obtener una API Key gratuita en openrouter.ai"
)

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://tuproyecto.com",
    "X-Title": "chatbot-explicador"
}

# === MODELOS DISPONIBLES ===
model_options = {
    "Qwen3": "qwen/qwen3-235b-a22b-07-25:free",
    "DeepSeek R1": "deepseek/deepseek-r1-0528:free",
    "Gemini 2.0": "google/gemini-2.0-flash-exp:free",
}

# === ESTILOS CSS PERSONALIZADOS ===
def load_css():
    st.markdown("""
    <style>
        /* Estilo para el contenedor del input de chat */
        .stChatFloatingInputContainer {
            bottom: 20px;
            background: white;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        /* Textarea con altura fija */
        .stChatFloatingInputContainer textarea {
            min-height: 60px !important;
            max-height: 60px !important;
            height: 60px !important;
            overflow-y: auto !important;
            resize: none !important;
        }
        
        /* Mensajes del usuario */
        [data-testid="stChatMessage"] [data-testid="user"] {
            background-color: #4a8cff;
            color: white;
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            margin-left: auto;
            max-width: 85%;
        }
        
        /* Mensajes del asistente */
        [data-testid="stChatMessage"] [data-testid="assistant"] {
            background-color: #f8f9fa;
            color: #333;
            padding: 12px 16px;
            border-radius: 18px 18px 18px 4px;
            margin-right: auto;
            max-width: 85%;
            border: 1px solid #e1e4e8;
        }
        
        /* Mejoras para móviles */
        @media (max-width: 768px) {
            [data-testid="stChatMessage"] [data-testid="user"],
            [data-testid="stChatMessage"] [data-testid="assistant"] {
                max-width: 100%;
            }
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# === FUNCIÓN PARA CONSULTAR OPENROUTER ===
def ask_openrouter(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"❌ Error: {response.text}"

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="ExpliBot - Asistente Técnico",
    page_icon="🤖",
    layout="wide"
)

# === SIDEBAR ===
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # Guardar el modelo seleccionado anteriormente
    previous_model = st.session_state.get('current_model', None)
    
    MODEL = st.selectbox("🧠 Modelo AI", list(model_options.keys()), index=0)
    MODEL = model_options[MODEL]
    
    # Detectar cambio de modelo
    if 'current_model' not in st.session_state or st.session_state.current_model != MODEL:
        st.session_state.current_model = MODEL
        st.session_state.model_changed = True
    
    # Guardar el modo anterior
    previous_mode = st.session_state.get('current_mode', None)
    
    modo = st.radio("🗣️ Estilo de explicación", 
                   ["Basico", "Ejemplos (Analogías)", "Ejemplos técnicos"])
    
    # Detectar cambio de modo
    if 'current_mode' not in st.session_state or st.session_state.current_mode != modo:
        st.session_state.current_mode = modo
        st.session_state.mode_changed = True
    
    modo_prompt = {
        "Basico": """
        * Explica TODO de una manera facil de entender para alguien sin conocimiento del tema
        * Usa palabras simples y evita términos técnicos
        * Divide conceptos complejos en partes pequeñas
        * Nunca asumas conocimiento previo
        * Usa ejemplos de la vida cotidiana
        * Limita tus respuestas, que no sean muy largas
        """,
        "Ejemplos (Analogías)": """
        * Para cada concepto técnico, ofrece una analogía clara
        * Compara con situaciones comunes (cocina, deportes, viajes)
        * Estructura tus respuestas: Concepto → Analogía → Explicación
        * Usa metáforas visuales cuando sea posible
        * Incluye al menos una analogía por respuesta
        """,
        "Ejemplos técnicos": """
        * Proporciona ejemplos prácticos con código cuando sea relevante
        * Explica primero el concepto en 1-2 frases simples
        * Muestra implementaciones concretas
        * Usa formatos: Explicación → Ejemplo → Aplicación práctica
        * Incluye código caundo sea necesario
        """
    }[modo]
    
    st.markdown("---")
    st.markdown("**Sobre ExpliBot**")
    st.markdown("Asistente para explicar temas técnicos de forma sencilla")

# === INTERFAZ PRINCIPAL ===
st.title("🤖 ExpliBot - Asistente Técnico")
st.caption("Pregúntame sobre IA, programación o ciencia de datos y te lo explicaré de forma clara")

# === LÓGICA DEL CHAT ===
if 'chat_history' not in st.session_state or st.session_state.get('model_changed', False) or st.session_state.get('mode_changed', False):
    # Reiniciar el chat cuando cambia el modelo o el modo
    st.session_state.chat_history = [{
        "role": "system",
        "content": f"""Eres ExpliBot, un asistente especializado en explicar temas técnicos complejos 
        (programación, inteligencia artificial, ciencia de datos, etc.) de manera 
        extremadamente sencilla y accesible para personas sin conocimientos previos.
        Actualmente usando el modelo {MODEL.split('/')[-1]} en modo {modo.lower()}.
        
        Sigue ESTAS reglas esenciales:
        1. Siempre da una breve explicación antes de ejemplos
        2. Divide conceptos en pasos simples
        3. Adapta el nivel según el usuario
        4. Sé paciente y alentador
        
        REGLAS ESPECÍFICAS DEL MODO ACTUAL ({modo}):
        {modo_prompt}"""
    }]
    st.session_state.model_changed = False
    st.session_state.mode_changed = False
    
# Mostrar historial de chat
for msg in st.session_state.chat_history:
    if msg["role"] == "system": continue
    
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input de chat
if OPENROUTER_API_KEY:
    if prompt := st.chat_input("✍️ Escribe tu pregunta..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("🤖 Pensando..."):
            response = ask_openrouter(st.session_state.chat_history)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
else:
    st.warning("⚠️ Ingresa tu API Key para comenzar")
