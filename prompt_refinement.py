import logging
from model_loader import load_gemini_pro
import streamlit as st

logger = logging.getLogger(__name__)

def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    refinement_instruction = """
You are an expert prompt optimizer. Transform the given naive prompt into a highly detailed, structured, and optimized prompt that will maximize the quality of the final AI response. Follow these rules strictly:

1. Output ONLY the refined prompt without any extra text, explanations, or markdown formatting.
2. Incorporate all essential details from the naive prompt.
3. Seamlessly integrate any user preferences provided below (including default and custom filter responses) into the refined prompt.
4. Ensure the refined prompt is clear, comprehensive, and precise while preserving the original intent.

Return only the refined prompt.
"""

    # Prepare a consolidated string for user preferences
    user_preferences_text = ""
    if user_choices:
        for section_label, prefs in user_choices.items():
            if prefs:
                user_preferences_text += f"\n[{section_label}]\n"
                for key, value in prefs.items():
                    user_preferences_text += f"{key}: {value}\n"

    full_prompt = f"{refinement_instruction}\nNaive Prompt: {naive_prompt}\nUser Preferences: {user_preferences_text}"
    model = load_gemini_pro("gemini-1.5-flash")
    if not model:
        raise Exception("Gemini Pro model not loaded successfully.")
    response = model.generate_content(full_prompt)
    refined_text = response.text.strip()
    logger.info(f"Refined prompt: {refined_text}")
    return refined_text
