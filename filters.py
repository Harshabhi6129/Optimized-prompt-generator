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
    """
    Uses the Gemini Pro model to generate custom filters that capture maximum insight 
    into what the user wants based on their naive prompt. The returned JSON will include:
      - Exactly one free–form text input (for the user to describe requirements)
      - Additional filters as options (radio, checkbox, or selectbox) for structured responses.
    """
    system_instruction = """
IMPORTANT: Output must be strictly valid JSON with no extra text, markdown, or explanations.

Task:
You are an expert in extracting user requirements for optimal prompt design. Analyze the following input prompt and generate a set of highly relevant custom filters that will capture maximum insight into what the user wants. The requirements are as follows:
- There must be exactly one free-form text input filter for the user to describe their requirements in their own words. Label it clearly (for example, "Describe your requirements:").
- All additional filters must be option-based (using types "radio", "checkbox", or "selectbox") to help the user select specific details.
- The filters should capture details such as the specific goal or outcome desired, tone, style, audience preferences, level of detail, technical constraints, and any domain-specific information.
- Ensure every filter has a unique key and is user-friendly.

Return a JSON object exactly in the following structure:
{
  "custom_filters": [
    {
      "type": "text_input",
      "label": "Describe your requirements:",
      "key": "custom_free_text"
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
                "type": "text_input",
                "label": "Describe your requirements:",
                "key": "fallback_free_text"
            },
            {
                "type": "radio",
                "label": "What level of detail do you require?",
                "key": "fallback_detail_level",
                "options": ["Basic", "Intermediate", "Advanced"]
            },
            {
                "type": "checkbox",
                "label": "Which areas are you most interested in?",
                "key": "fallback_interest_areas",
                "options": ["Design", "Functionality", "Performance", "Usability"]
            }
        ]
    }
    return fallback_filters

# -----------------------------------------------------------------------------
# Display Custom Filters
# -----------------------------------------------------------------------------
def display_custom_filters(custom_filters: list) -> dict:
    """
    Displays the custom filters on the Streamlit UI.
    - Ensures that exactly one free-form text input (displayed as a multi-line text area) is shown.
    - All additional filters are rendered as option–based inputs.
    """
    st.subheader("Custom Input")
    user_custom_choices = {}

    # Separate the free–form text input filter from option–based filters
    free_text_filter = None
    option_filters = []
    for filt in custom_filters:
        if filt.get("type") == "text_input":
            # Only use the first free-form text filter and ignore any extras.
            if free_text_filter is None:
                free_text_filter = filt
            else:
                option_filters.append(filt)
        else:
            option_filters.append(filt)

    # If no free-form text filter exists, add a default one.
    if free_text_filter is None:
        free_text_filter = {
            "type": "text_input",
            "label": "Describe your requirements:",
            "key": "default_custom_text"
        }

    # Use a multi-line text area for free-form input.
    user_custom_choices[free_text_filter["key"]] = st.text_area(
        free_text_filter["label"],
        key=free_text_filter["key"]
    )

    st.subheader("Additional Options")
    # Display all additional option–based filters
    for filt in option_filters:
        f_type = filt.get("type", "radio")
        f_label = filt.get("label", "Filter")
        f_key = filt.get("key", f"custom_{f_label}")
        f_options = filt.get("options", [])

        if f_type == "checkbox":
            if not f_options:
                user_custom_choices[f_key] = st.checkbox(f_label, key=f_key)
            else:
                # For checkboxes with options, allow multiple selections.
                user_custom_choices[f_key] = [
                    opt for opt in f_options if st.checkbox(opt, key=f"{f_key}_{opt}")
                ]
        elif f_type == "radio":
            user_custom_choices[f_key] = st.radio(f_label, options=f_options, key=f_key)
        elif f_type == "selectbox":
            user_custom_choices[f_key] = st.selectbox(f_label, options=f_options, key=f_key)
        # In the unlikely case a text_input type sneaks in here, display it as a single-line input.
        elif f_type == "text_input":
            user_custom_choices[f_key] = st.text_input(f_label, key=f_key)

    return user_custom_choices
