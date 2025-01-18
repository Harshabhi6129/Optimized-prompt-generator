import streamlit as st
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

def load_gemini_pro(model_name: str) -> genai.GenerativeModel:
    try:
        return genai.GenerativeModel(model_name=model_name)
    except Exception as e:
        logger.error(f"Error loading Gemini Pro model {model_name}: {e}")
        st.error(f"Error loading Gemini Pro model: {e}")
        return None
