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
    
    # Group 1: Response Settings
    with st.expander("Response Settings", expanded=True):
        answer_format = st.radio(
            "Preferred Answer Format:",
            options=["Paragraph", "Bullet Points"],
            key="default_answer_format"
        )
        tone_of_response = st.radio(
            "Preferred Tone of Response:",
            options=["Formal", "Informal", "Neutral"],
            key="default_tone_of_response"
        )
        output_detail = st.slider(
            "Output Detail Level (1 = Summary, 5 = Detailed):",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            key="default_output_detail"
        )
        
    # Group 2: Audience & Purpose
    with st.expander("Audience & Purpose", expanded=True):
        audience_level = st.radio(
            "Intended Audience:",
            options=["General", "Beginner", "Intermediate", "Expert"],
            key="default_audience_level"
        )
        purpose = st.selectbox(
            "Primary Purpose of Request:",
            options=["Learning/Education", "Professional/Work", "Personal Interest", "Research"],
            key="default_purpose"
        )
    
    # Group 3: Additional Preferences
    with st.expander("Additional Preferences", expanded=False):
        include_visuals = st.checkbox(
            "Include visual aids (charts, diagrams, etc.)",
            key="default_include_visuals"
        )
        response_structure = st.radio(
            "Preferred Response Structure:",
            options=["Concise", "Structured with Headings", "Step-by-Step"],
            key="default_response_structure"
        )
    
    return {
        "Answer Format": answer_format,
        "Tone of Response": tone_of_response,
        "Output Detail": output_detail,
        "Audience Level": audience_level,
        "Purpose": purpose,
        "Include Visuals": include_visuals,
        "Response Structure": response_structure
    }

# -----------------------------------------------------------------------------
# Generate Dynamic Custom Filters
# -----------------------------------------------------------------------------
def generate_dynamic_filters(naive_prompt: str) -> dict:
    """
    Uses the Gemini Pro model to generate custom filters that capture maximum insight 
    into what the user wants based on their naive prompt. The returned JSON will include:
      - Exactly one free-form text input filter for the user to describe requirements.
      - Additional filters (radio, checkbox, or selectbox) relevant to the user’s domain,
        without duplicating default filters (tone, style, etc.).
    """
    system_instruction = """
IMPORTANT: Output must be strictly valid JSON with no extra text, markdown, or explanations.

Task:
You are an expert in extracting user requirements for optimal prompt design. Analyze the following input prompt and generate a set of highly relevant custom filters that will capture maximum insight into what the user wants. The requirements are as follows:

- Avoid repeating existing defaults (tone, style, level of detail).
- Include exactly one free-form text input filter labeled "Describe your requirements:".
- Additional filters (radio, checkbox, selectbox) must be domain-specific, advanced, or uniquely relevant to the user’s prompt.
- Each filter must have a unique 'key' and be user-friendly.
- Provide only truly useful filters based on the prompt.

Return a JSON object in the following structure:
{
  "custom_filters": [
    {
      "type": "text_input",
      "label": "Describe your requirements:",
      "key": "custom_free_text"
    },
    // Additional relevant filters as needed
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

            # Validate each filter definition
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
                "type": "checkbox",
                "label": "Which areas are you most interested in?",
                "key": "fallback_interest_areas",
                "options": ["Design", "Functionality", "Performance", "Usability"]
            },
            {
                "type": "text_input",
                "label": "Describe your requirements:",
                "key": "fallback_free_text"
            }
        ]
    }
    return fallback_filters

# -----------------------------------------------------------------------------
# Display Custom Filters
# -----------------------------------------------------------------------------
def display_custom_filters(custom_filters: list) -> dict:
    """
    Displays the custom filters on the Streamlit UI:
    - Option-based filters (radio, checkbox, selectbox) appear first, each in an expander.
    - The one free-form text_input (or fallback) goes last in a separate expander.
    """
    st.subheader("Custom Filters")
    user_custom_choices = {}

    # Separate free-form text input
    free_text_filter = None
    option_filters = []
    for filt in custom_filters:
        f_type = filt.get("type")
        if f_type == "text_input":
            # Use the first text_input as the free-form entry
            if free_text_filter is None:
                free_text_filter = filt
            else:
                option_filters.append(filt)
        else:
            option_filters.append(filt)

    # Present option-based filters in expanders
    st.markdown("### Select from the options below:")
    for filt in option_filters:
        f_type = filt.get("type", "radio")
        f_label = filt.get("label", "Filter")
        f_key = filt.get("key", f"custom_{f_label}")
        f_options = filt.get("options", [])

        with st.expander(f"Filter: {f_label}", expanded=False):
            if f_type == "checkbox":
                # If no options, treat as a single checkbox
                if not f_options:
                    user_custom_choices[f_key] = st.checkbox(f_label, key=f_key)
                else:
                    # Multiple selectable checkboxes
                    chosen = []
                    for opt in f_options:
                        # 1) If it's dict with "label"/"value", show label, store value
                        if isinstance(opt, dict) and "label" in opt and "value" in opt:
                            display_label = str(opt["label"])[:100]
                            stored_value = opt["value"]
                        else:
                            display_label = str(opt)[:100]
                            stored_value = display_label
                        if st.checkbox(display_label, key=f"{f_key}_{display_label}"):
                            chosen.append(stored_value)
                    user_custom_choices[f_key] = chosen

            elif f_type == "radio":
                display_labels = []
                stored_values = []
                for opt in f_options:
                    if isinstance(opt, dict) and "label" in opt and "value" in opt:
                        display_label = str(opt["label"])[:100]
                        stored_value = opt["value"]
                    else:
                        display_label = str(opt)[:100]
                        stored_value = display_label
                    display_labels.append(display_label)
                    stored_values.append(stored_value)

                selected_label = st.radio(f_label, options=display_labels, key=f_key)
                # Map selected label back to the stored value
                user_custom_choices[f_key] = None
                if selected_label in display_labels:
                    idx = display_labels.index(selected_label)
                    user_custom_choices[f_key] = stored_values[idx]

            elif f_type == "selectbox":
                display_labels = []
                stored_values = []
                for opt in f_options:
                    if isinstance(opt, dict) and "label" in opt and "value" in opt:
                        display_label = str(opt["label"])[:100]
                        stored_value = opt["value"]
                    else:
                        display_label = str(opt)[:100]
                        stored_value = display_label
                    display_labels.append(display_label)
                    stored_values.append(stored_value)

                selected_label = st.selectbox(f_label, options=display_labels, key=f_key)
                user_custom_choices[f_key] = None
                if selected_label in display_labels:
                    idx = display_labels.index(selected_label)
                    user_custom_choices[f_key] = stored_values[idx]

            elif f_type == "text_input":
                # If a filter is text_input but not the designated free_text_filter,
                # display it as a normal text_input
                user_custom_choices[f_key] = st.text_input(f_label, key=f_key)

    # Ensure we have at least one free-form text filter
    if free_text_filter is None:
        free_text_filter = {
            "type": "text_input",
            "label": "Describe your requirements:",
            "key": "default_custom_text"
        }

    # Display free-form text in a final expander
    st.markdown("### Provide Additional Details")
    with st.expander(f"Custom Description: {free_text_filter.get('label')}", expanded=True):
        user_custom_choices[free_text_filter["key"]] = st.text_area(
            free_text_filter["label"],
            key=free_text_filter["key"]
        )

    return user_custom_choices
