import google.generativeai as genai
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def configure_genai(openai_key: str, google_genai_key: str):
    if openai_key:
        logger.info("OpenAI API Key loaded successfully.")
    else:
        st.error("OpenAI API Key is missing.")

    if google_genai_key:
        try:
            genai.configure(api_key=google_genai_key)
        except Exception as e:
            st.error(f"Error configuring Google GenAI: {e}")
    else:
        st.warning("Google GenAI key not found.")

def load_gemini_pro(model_name: str):
    try:
        return genai.GenerativeModel(model_name=model_name)
    except Exception as e:
        st.error(f"Error loading Gemini Pro model: {e}")
        return None
