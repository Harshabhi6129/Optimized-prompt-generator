import logging
from model_loader import load_gemini_pro
import streamlit as st

logger = logging.getLogger(__name__)

def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    refinement_instruction = """
You are an expert prompt optimizer. Your task is to transform the given naive prompt into a highly detailed, 
structured, and clear prompt that maximizes response quality from an AI model. Follow these rules strictly:

1. **Output Format**: 
   - Generate ONLY the refined prompt. 
   - Do NOT include any additional text, explanations, disclaimers, or markdown formatting.
   - Do NOT include phrases like "Here is the refined prompt" or "This is the optimized prompt."
   - The output must be a clean, direct, and usable prompt.

2. **Refinement Rules**:
   - Ensure the refined prompt is comprehensive and includes all necessary details to guide the AI model effectively.
   - If user preferences are provided, incorporate them seamlessly into the refined prompt.
   - Maintain the original intent of the naive prompt while enhancing its clarity and specificity.

3. **Output**:
   - Return ONLY the refined prompt. Nothing else.
"""

    user_preferences_text = ""
    if user_choices:
        user_preferences_text = "\nUser Preferences:\n"
        for section_label, prefs_dict in user_choices.items():
            if prefs_dict:  # Only add sections with non-empty preferences
                user_preferences_text += f"\n[{section_label}]\n"
                for k, v in prefs_dict.items():
                    user_preferences_text += f"- {k}: {v}\n"

    full_prompt = f"{refinement_instruction}\nNaive Prompt: {naive_prompt}\n{user_preferences_text}"

    model = load_gemini_pro("gemini-1.5-flash")
    if not model:
        raise Exception("Gemini Pro model not loaded successfully.")

    response = model.generate_content(full_prompt)
    return response.text.strip()
