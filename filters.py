import streamlit as st
import re
import json
import logging
from model_loader import load_gemini_pro

logger = logging.getLogger(__name__)

def get_default_filters() -> dict:
    st.subheader("Default Filters")

    answer_format = st.radio(
        "Preferred answer format:",
        options=["Paragraph", "Bullet Points"],
        key="default_answer_format"
    )

    explanation_length = st.radio(
        "Explanation length:",
        options=["Short", "Long"],
        key="default_explanation_length"
    )

    return {
        "Answer Format": answer_format,
        "Explanation Length": explanation_length
    }

def generate_dynamic_filters(naive_prompt: str) -> dict:
    system_instruction = """
IMPORTANT: Output must be strictly valid JSON. Do NOT include code blocks, disclaimers, 
or additional commentary. No markdown formatting or extra text. 
... [same as before] ...
"""

    full_prompt = f"{system_instruction}\n\nNaive Prompt:\n{naive_prompt}"

    model = load_gemini_pro("gemini-1.5-flash")
    if not model:
        st.error("Gemini Pro model not loaded successfully.")
        return {"custom_filters": []}

    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        ...
        # same logic as before
        ...

    # Fallback
    return {
        "custom_filters": [
            {
                "type": "text_input",
                "label": "Fallback: Please specify your main goal",
                "key": "fallback_goal"
            }
        ]
    }

def display_custom_filters(custom_filters: list) -> dict:
    st.subheader("Custom Filters")
    ...
    # same logic as before
    ...
    return user_custom_choices
