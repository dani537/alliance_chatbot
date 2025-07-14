# app.py
import os
import streamlit as st
from src.gemini_api import GeminiChat
from src.preguntas import evaluar_pregunta
from src.consultas import polizas, siniestros

# Configuración inicial
st.set_page_config(
    page_title="Financial Chatbot",
    page_icon="💬",
    layout="centered"
)

def get_buttons_config(resultado):
    if resultado == "1_poliza_hogar":
        return {"buttons": ["Productos de hogar", "Siniestralidad en hogar", "Prima Media según hogar"], "type": "polizas"}
    elif resultado == "2_siniestralidad":
        return {"buttons": ["Coste Siniestralidad según LoB", "Costes por provincias", "Reservas según LoB"], "type": "siniestros"}
    else:
        return {"buttons": [], "type": None}

def handle_button_click(button_text, button_type):
    """Maneja el click en los botones dinámicos"""
    try:
        if button_type == "polizas":
            prompt_generado = polizas()
            image_path = "./src/data/polizas_image.png"
        elif button_type == "siniestros":
            prompt_generado = siniestros()
            image_path = "./src/data/siniestros_image.png"
        else:
            st.error("Tipo de botón no reconocido")
            return

        with st.spinner("Generando respuesta..."):
            response, updated_history = st.session_state.gemini_chat.send_message(
                prompt_generado,
                st.session_state.messages
            )
            st.session_state.messages = updated_history
            st.session_state.last_image_path = image_path

        if "pending_buttons" in st.session_state:
            del st.session_state.pending_buttons
        if "button_type" in st.session_state:
            del st.session_state.button_type

        st.rerun()

    except Exception as e:
        st.error(f"Error al procesar la selección: {e}")

# Banner y título
banner_path = "./image/banner.png"
if os.path.exists(banner_path):
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(banner_path, use_container_width=True)
else:
    st.warning("No se encontró la imagen del banner en ./image/banner.png")
st.title("💬 Financial Chatbot")

# Inicializar el chat
if "gemini_chat" not in st.session_state:
    try:
        st.session_state.gemini_chat = GeminiChat()
        st.session_state.messages = st.session_state.gemini_chat.start_chat()
        st.session_state.last_image_path = None
    except Exception as e:
        st.error(f"Error al configurar Gemini: {e}")
        st.stop()

# Mostrar mensajes
for idx, message in enumerate(st.session_state.messages):
    role_for_display = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role_for_display):
        st.markdown(message["content"])

        # Solo muestra la imagen si es el último mensaje del modelo
        if (
            role_for_display == "assistant"
            and idx == len(st.session_state.messages) - 1
            and st.session_state.get("last_image_path")
            and os.path.exists(st.session_state["last_image_path"])
        ):
            st.image(st.session_state["last_image_path"], caption="📊 Gráfico generado", use_container_width=True)

# Mostrar botones dinámicos si hay
if "pending_buttons" in st.session_state and st.session_state.pending_buttons:
    st.markdown("### Selecciona una opción:")
    cols = st.columns(len(st.session_state.pending_buttons))
    for idx, button_text in enumerate(st.session_state.pending_buttons):
        with cols[idx]:
            if st.button(button_text, key=f"btn_{idx}"):
                handle_button_click(button_text, st.session_state.button_type)

# Entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    if not prompt.strip():
        st.warning("Por favor, escribe un mensaje válido.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        resultado_evaluacion = evaluar_pregunta(prompt)
        config_botones = get_buttons_config(resultado_evaluacion)

        if config_botones["buttons"]:
            st.session_state.pending_buttons = config_botones["buttons"]
            st.session_state.button_type = config_botones["type"]
            st.session_state.messages.append({"role": "model", "content": "🔍 He analizado tu mensaje. Elige una opción para continuar:"})
            st.rerun()
        else:
            with st.spinner("Pensando..."):
                response, updated_history = st.session_state.gemini_chat.send_message(prompt, st.session_state.messages)
                st.session_state.messages = updated_history
                st.session_state.last_image_path = None
                st.rerun()
    except Exception as e:
        st.error(f"Error al evaluar la pregunta: {e}")