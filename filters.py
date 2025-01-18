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
        try:
            response = model.generate_content(full_prompt)
            text_output = response.text.strip()
            logger.info(f"[Attempt {attempt}] LLM output: {text_output}")

            # Clean up any extra text around the JSON using regex
            json_match = re.search(r"{.*}", text_output, re.DOTALL)
            if json_match:
                text_output = json_match.group(0)

            # Attempt to parse the cleaned output as JSON
            parsed_output = json.loads(text_output)

            if "custom_filters" not in parsed_output:
                raise ValueError("No 'custom_filters' key found in JSON.")

            return parsed_output  # Valid JSON parsed successfully

        except Exception as e:
            logger.error(f"[Attempt {attempt}] JSON parse error: {e}")
            if attempt < max_attempts:
                st.warning("LLM returned invalid JSON. Retrying...")
            else:
                st.error("All attempts to parse filters failed. Using fallback filters.")

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
    user_custom_choices = {}
    for filter_def in custom_filters:
        f_type = filter_def.get("type", "text_input")
        f_label = filter_def.get("label", "Filter")
        f_key = filter_def.get("key", f"custom_{f_label}")
        f_options = filter_def.get("options", [])

        if f_type == "text_input":
            val = st.text_input(f_label, key=f_key)
            user_custom_choices[f_label] = val

        elif f_type == "checkbox":
            # If a single checkbox, user can either check or not
            if not f_options:
                val = st.checkbox(f_label, key=f_key)
                user_custom_choices[f_label] = val
            else:
                # multiple checkbox options
                st.write(f_label)
                selected_options = []
                for opt in f_options:
                    cb_key = f"{f_key}_{opt}"
                    cb_value = st.checkbox(opt, key=cb_key)
                    if cb_value:
                        selected_options.append(opt)
                user_custom_choices[f_label] = selected_options

        elif f_type == "radio":
            if not f_options:
                f_options = ["Option 1", "Option 2"]
            val = st.radio(f_label, f_options, key=f_key)
            user_custom_choices[f_label] = val

        elif f_type == "selectbox":
            if not f_options:
                f_options = ["Option 1", "Option 2"]
            val = st.selectbox(f_label, f_options, key=f_key)
            user_custom_choices[f_label] = val

        else:
            # Default fallback if type isn't recognized
            val = st.text_input(f_label, key=f_key)
            user_custom_choices[f_label] = val
    return user_custom_choices
