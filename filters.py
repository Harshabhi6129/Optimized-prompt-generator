import streamlit as st
import re
import json
import logging
from model_loader import load_gemini_pro

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Default Filters
# -----------------------------------------------------------------------------
def get_default_filters() -> dict:
    st.subheader("Default Filters")

    # Preferred Answer Format
    answer_format = st.radio(
        "Preferred answer format:",
        options=["Paragraph", "Bullet Points"],
        key="default_answer_format"
    )

    # Preferred Tone of Response
    tone_of_response = st.radio(
        "Preferred tone of response:",
        options=["Formal", "Informal", "Neutral"],
        key="default_tone_of_response"
    )

    # Length of Output
    output_length = st.slider(
        "Length of output:",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
        format="%d",
        key="default_output_length"
    )

    return {
        "Answer Format": answer_format,
        "Tone of Response": tone_of_response,
        "Output Length": output_length
    }

# -----------------------------------------------------------------------------
# Generate Dynamic Filters
# -----------------------------------------------------------------------------
def generate_dynamic_filters(naive_prompt: str) -> dict:
        system_instruction = """
IMPORTANT: Output must be strictly valid JSON. Do NOT include code blocks, disclaimers, 
or additional commentary. No markdown formatting or extra text. 

Your task: 
- Read the user's naive prompt.
- Identify relevant filter questions or user preferences that would help refine 
  the final answer. 
- Return a JSON object with a "custom_filters" key, which is a list of filter definitions. 
- Each filter definition can have:
    "type" (e.g. "text_input", "checkbox", "radio", "selectbox"),
    "label" (string describing the filter),
    "key"   (unique string key),
    "options" (array of strings, only if type is "radio", "selectbox", or "checkbox" with multiple options).
- Ensure the filters are specifically relevant to the user's prompt. 
- Do NOT include non-relevant or generic filters if they don't make sense.
- Do NOT include any additional text, explanations, or disclaimers.

Structure must look like:
{
  "custom_filters": [
    {
      "type": "...",
      "label": "...",
      "key": "...",
      "options": [...]
    },
    ...
  ]
}
"""

    full_prompt = f"{system_instruction}\n\nNaive Prompt:\n{naive_prompt}"

    model = load_gemini_pro("gemini-1.5-flash")
    if not model:
        st.error("Gemini Pro model not loaded successfully.")
        return {"custom_filters": []}

    for attempt in range(2):
        try:
            response = model.generate_content(full_prompt)
            text_output = response.text.strip()
            logger.info(f"[Attempt {attempt}] LLM output: {text_output}")

            # Extract JSON
            json_match = re.search(r"{.*}", text_output, re.DOTALL)
            if json_match:
                text_output = json_match.group(0)

            parsed_output = json.loads(text_output)
            if "custom_filters" not in parsed_output:
                raise ValueError("No 'custom_filters' key found.")
            return parsed_output
        except Exception as e:
            logger.error(f"JSON Parsing Error: {e}")

    # Fallback Filters
    return {
        "custom_filters": [
            {"type": "text_input", "label": "Specify your goal", "key": "fallback_goal"}
        ]
    }

# -----------------------------------------------------------------------------
# Display Custom Filters
# -----------------------------------------------------------------------------
def display_custom_filters(custom_filters: list) -> dict:
    st.subheader("Custom Filters")

    user_custom_choices = {}
    for filter_def in custom_filters:
        f_type = filter_def.get("type", "text_input")
        f_label = filter_def.get("label", "Filter")
        f_key = filter_def.get("key", f"custom_{f_label}")
        f_options = filter_def.get("options", [])

        if f_type == "text_input":
            user_custom_choices[f_label] = st.text_input(f_label, key=f_key)
        elif f_type == "checkbox":
            if not f_options:
                user_custom_choices[f_label] = st.checkbox(f_label, key=f_key)
            else:
                user_custom_choices[f_label] = [
                    opt for opt in f_options if st.checkbox(opt, key=f"{f_key}_{opt}")
                ]
        elif f_type == "radio":
            user_custom_choices[f_label] = st.radio(f_label, options=f_options, key=f_key)
        elif f_type == "selectbox":
            user_custom_choices[f_label] = st.selectbox(f_label, options=f_options, key=f_key)
    return user_custom_choices
