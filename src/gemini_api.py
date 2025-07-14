# gemini_api.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiChat:
    def __init__(self, model_name='gemini-1.5-flash'):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def start_chat(self, initial_message="¡Hola! ¿En qué puedo ayudarte? 😊"):
        return [{"role": "model", "content": initial_message}]

    def send_message(self, user_message, chat_history):
        try:
            history_for_api = [{"role": msg["role"], "parts": [msg["content"]]} for msg in chat_history]
            history_for_api.append({"role": "user", "parts": [user_message]})

            response = self.model.generate_content(contents=history_for_api)
            response_text = response.text

            updated_history = chat_history + [
                {"role": "model", "content": response_text}
            ]

            return response_text, updated_history

        except Exception as e:
            raise Exception(f"Error al obtener respuesta de Gemini: {e}")