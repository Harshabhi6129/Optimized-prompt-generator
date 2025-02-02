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
# Generate Dynamic Custom Filters
# -----------------------------------------------------------------------------
def generate_dynamic_filters(naive_prompt: str) -> dict:
    system_instruction = """
IMPORTANT: Output must be strictly valid JSON with no extra text, markdown, or explanations.

Task:
You are an expert in extracting user requirements for optimal prompt design. Analyze the following input prompt and generate a set of highly relevant custom filters. These filters should capture details such as:
- The specific goal or outcome desired.
- The tone, style, or audience preferences.
- The level of detail and any technical constraints.
- Any contextual or domain-specific information.

For each filter, include:
  - "type": one of "text_input", "checkbox", "radio", or "selectbox"
  - "label": a clear, concise question to ask the user
  - "key": a unique identifier for this filter
  - "options": an array of strings (only for "radio", "checkbox", or "selectbox" types)

Return a JSON object exactly in the following structure:
{
  "custom_filters": [
    {
      "type": "text_input",
      "label": "Your question here",
      "key": "unique_key_here"
    },
    {
      "type": "radio",
      "label": "Your question here",
      "key": "unique_key_here",
      "options": ["Option1", "Option2"]
    }
    // Additional filters as needed
  ]
}
"""
    full_prompt = f"{system_instruction}\n\nInput Prompt:\n{naive_prompt}"
    model = load_gemini_pro("gemini-1.5-flash")
    if not model:
        st.error("Gemini Pro model not loaded successfully.")
        return {"custom_filters": []}
    
    attempts = 3
    for attempt in range(attempts):
        try:
            response = model.generate_content(full_prompt)
            text_output = response.text.strip()
            logger.info(f"[Attempt {attempt+1}] LLM output: {text_output}")

            # Attempt to extract the JSON substring (assumes the first {...} block is the valid JSON)
            json_match = re.search(r'\{.*\}', text_output, re.DOTALL)
            if json_match:
                text_output = json_match.group(0)
            parsed_output = json.loads(text_output)
            if "custom_filters" not in parsed_output:
                raise ValueError("Missing 'custom_filters' key in the output.")
            # Validate each filter definition contains required keys
            for filt in parsed_output["custom_filters"]:
                if "type" not in filt or "label" not in filt or "key" not in filt:
                    raise ValueError("A filter is missing one or more required keys.")
            return parsed_output
        except Exception as e:
            logger.error(f"JSON Parsing Error on attempt {attempt+1}: {e}")

    # Fallback filters if generation fails
    fallback_filters = {
        "custom_filters": [
            {
                "type": "radio",
                "label": "What level of detail do you require?",
                "key": "fallback_detail_level",
                "options": ["Basic", "Intermediate", "Advanced"]
            },
            {
                "type": "text_input",
                "label": "Please specify any particular focus area:",
                "key": "fallback_focus_area"
            }
        ]
    }
    return fallback_filters

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
                # Allow multiple selections if options are provided
                user_custom_choices[f_label] = [
                    opt for opt in f_options if st.checkbox(opt, key=f"{f_key}_{opt}")
                ]
        elif f_type == "radio":
            user_custom_choices[f_label] = st.radio(f_label, options=f_options, key=f_key)
        elif f_type == "selectbox":
            user_custom_choices[f_label] = st.selectbox(f_label, options=f_options, key=f_key)
    return user_custom_choices
