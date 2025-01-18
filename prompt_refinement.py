import streamlit as st
import logging
import re
from model_loader import load_gemini_pro

logger = logging.getLogger(__name__)

def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    try:
        refinement_instruction = """
You are an expert prompt optimizer. Transform the given naive prompt ...
... [same as before] ...
"""
        user_preferences_text = "\nUser Preferences:\n"
        for section_label, prefs_dict in user_choices.items():
            user_preferences_text += f"\n[{section_label}]\n"
            for k, v in prefs_dict.items():
                user_preferences_text += f"- {k}: {v}\n"

        full_prompt = (
            f"{refinement_instruction}\nNaive Prompt: {naive_prompt}\n"
            f"{user_preferences_text}\n"
        )

        model = load_gemini_pro("gemini-1.5-flash")
        if not model:
            raise Exception("Gemini Pro model not loaded successfully.")

        response = model.generate_content(full_prompt)
        refined_text = response.text.strip()
        logger.info("Prompt refined successfully with Google Generative AI.")
        return refined_text

    except Exception as e:
        logger.error(f"Error refining prompt with Google GenAI: {e}")
        st.error(f"Error refining prompt with Google GenAI: {e}")
        return naive_prompt
