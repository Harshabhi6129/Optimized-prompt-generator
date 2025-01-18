import logging
import streamlit as st
from model_loader import load_gemini_pro

logger = logging.getLogger(__name__)

def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    try:
        refinement_instruction = """
You are an expert prompt optimizer. Transform the given naive prompt into a highly detailed, 
structured, and clear prompt that maximizes response quality from an AI model.
...
"""
        user_preferences_text = "\nUser Preferences:\n"
        for section_label, prefs in user_choices.items():
            user_preferences_text += f"[{section_label}]\n" + "\n".join(f"- {k}: {v}" for k, v in prefs.items())

        full_prompt = f"{refinement_instruction}\nNaive Prompt: {naive_prompt}\n{user_preferences_text}"
        model = load_gemini_pro("gemini-1.5-flash")
        if not model:
            raise Exception("Gemini Pro model not loaded successfully.")

        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error refining prompt: {e}")
        st.error(f"Error refining prompt: {e}")
        return naive_prompt
