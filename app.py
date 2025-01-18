import openai
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="GPT-4o Advanced Prompt Refinement",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Set API keys
openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
google_genai_key = st.secrets.get("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))

# Configure OpenAI
if not openai_api_key:
    logger.error("OpenAI API Key is missing.")
    st.error("OpenAI API Key is missing. Please set it in the environment.")
else:
    openai.api_key = openai_api_key
    logger.info("OpenAI API Key loaded successfully.")

# Configure Google Generative AI
if google_genai_key:
    try:
        genai.configure(api_key=google_genai_key)
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Error configuring Google Generative AI: {e}")
        st.error(f"Error configuring Google Generative AI: {e}")
else:
    logger.warning("Google Generative AI key not found.")
    st.warning("Google Generative AI key not found. Please set it in the environment.")


# -----------------------------------------------------------------------------
# Utility: Load Gemini Pro Model
# -----------------------------------------------------------------------------
def load_gemini_pro(model_name: str) -> genai.GenerativeModel:
    """Returns the Gemini Pro Generative model."""
    try:
        model = genai.GenerativeModel(model_name=model_name)
        return model
    except Exception as e:
        logger.error(f"Error loading Gemini Pro model {model_name}: {e}")
        st.error(f"Error loading Gemini Pro model: {e}")
        return None


# -----------------------------------------------------------------------------
# Part A: Default Filters
# -----------------------------------------------------------------------------
def get_default_filters() -> dict:
    """
    Display always-present filters in the UI (e.g., answer format, length).
    Returns a dict of user-selected default filter options.
    """
    st.subheader("Default Filters")

    # For answer format, we use a radio or selectbox to choose between bullet points or paragraphs
    answer_format = st.radio(
        "Preferred answer format:",
        options=["Paragraph", "Bullet Points"],
        key="default_answer_format"
    )

    # For explanation length, again a radio to pick short vs. long
    explanation_length = st.radio(
        "Explanation length:",
        options=["Short", "Long"],
        key="default_explanation_length"
    )

    # You can add more default filters if needed
    # For example:
    # tone = st.selectbox("Tone:", ["Informal", "Formal", "Enthusiastic"], key="default_tone")

    return {
        "Answer Format": answer_format,
        "Explanation Length": explanation_length,
        # "Tone": tone
    }


# -----------------------------------------------------------------------------
# Part B: Generate Custom Filters from LLM
# -----------------------------------------------------------------------------
def generate_dynamic_filters(naive_prompt: str) -> dict:
    """
    Use Google Generative AI (or any LLM) to generate possible custom filters/questions
    for refining the naive prompt. This returns a structure for custom filters.

    Example JSON structure returned:
      {
        "custom_filters": [
            {
                "type": "text_input",
                "label": "Number of days",
                "key": "num_days"
            },
            {
                "type": "selectbox",
                "label": "Travel style",
                "key": "travel_style",
                "options": ["Luxury", "Backpacking", "Moderate"]
            },
            ...
        ]
      }
    """
    try:
        # We'll ask the model to propose any relevant filters in a structured JSON format
        filter_prompt = f"""
            You are an AI assistant for prompt refinement.
            From the naive prompt below, propose any relevant custom filters or questions 
            (like number of days, audience, level of detail, specialized preferences, etc.).
            Return a JSON with a "custom_filters" key, which should be an array of filter definitions.

            Each filter definition can include:
             - type: (e.g., "checkbox", "text_input", "radio", "selectbox")
             - label: a short descriptive label
             - key: a unique key to store the user’s selection
             - options: an array of possible options (if relevant, for radio/selectbox)

            Naive prompt: {naive_prompt}

            Example structure to return:
            {{
              "custom_filters": [
                {{
                  "type": "text_input",
                  "label": "Number of days",
                  "key": "num_days"
                }},
                {{
                  "type": "radio",
                  "label": "Travel style",
                  "key": "travel_style",
                  "options": ["Luxury", "Backpacking", "Budget", "Moderate"]
                }},
                ...
              ]
            }}
        """

        model = load_gemini_pro("gemini-1.5-flash")
        if not model:
            raise Exception("Gemini Pro model not loaded successfully.")

        response = model.generate_content(filter_prompt)
        text_output = response.text.strip()

        # Attempt to parse as JSON. If it fails, fallback to an empty structure
        parsed_output = json.loads(text_output)
        return parsed_output

    except Exception as e:
        logger.error(f"Error generating dynamic filters: {e}")
        st.error(f"Error generating dynamic filters: {e}")
        # Fallback example in case of error
        return {
            "custom_filters": [
                {
                    "type": "text_input",
                    "label": "Number of days",
                    "key": "fallback_num_days"
                },
                {
                    "type": "radio",
                    "label": "Travel style",
                    "key": "fallback_travel_style",
                    "options": ["Luxury", "Backpacking", "Budget"]
                }
            ]
        }


# -----------------------------------------------------------------------------
# Part C: Display Custom Filters in the UI
# -----------------------------------------------------------------------------
def display_custom_filters(custom_filters: list) -> dict:
    """
    Renders the custom filters in Streamlit based on the definitions (type, label, options, etc.).
    Returns a dict of the user's selections.
    """
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
            val = st.checkbox(f_label, key=f_key)
            user_custom_choices[f_label] = val

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


# -----------------------------------------------------------------------------
# Part D: Refine Prompt (Using All Filters) with Google Generative AI
# -----------------------------------------------------------------------------
def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    """
    Use Google Generative AI to refine the naive prompt into a detailed and well-structured prompt,
    *incorporating* both default and custom filters.
    """
    try:
        refinement_instruction = """
        You are an expert prompt optimizer. 
        Transform the given naive prompt into a highly detailed, structured, and clear prompt 
        that maximizes response quality from an AI model. 
        Incorporate the user preferences below as needed 
        (e.g., desired format, length, other relevant constraints or clarifications).
        """

        # Convert user_choices to text
        # user_choices might have structure like:
        # {
        #    "Default": {
        #       "Answer Format": "Bullet Points",
        #       "Explanation Length": "Short"
        #    },
        #    "Custom": {
        #       "Number of days": "7",
        #       "Travel style": "Backpacking",
        #       ...
        #    }
        # }
        user_preferences_text = "\n\nUser Preferences:\n"
        for section_label, prefs_dict in user_choices.items():
            user_preferences_text += f"\n[{section_label} Filters]\n"
            for k, v in prefs_dict.items():
                user_preferences_text += f"- {k}: {v}\n"

        full_prompt = (
            f"{refinement_instruction}\n\n"
            f"Naive Prompt: {naive_prompt}\n"
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


# -----------------------------------------------------------------------------
# Part E: Generate Final Answer from GPT-4o (or any chosen model)
# -----------------------------------------------------------------------------
def generate_response_from_chatgpt(refined_prompt: str) -> str:
    """
    Send the refined prompt to GPT-4o Mini (or any model) and retrieve the response.
    """
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant. Provide clear and precise answers."},
        {"role": "user", "content": refined_prompt},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with the actual model you want to use
            messages=messages
        )
        logger.info("Response generated successfully with GPT-4o Mini.")
        return response['choices'][0]['message']['content'].strip()

    except openai.error.InvalidRequestError as e:
        logger.error(f"InvalidRequestError: {e}")
        return "⚠️ Invalid model or request parameters."

    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return f"Error in generating response: {str(e)}"


# -----------------------------------------------------------------------------
# Main Streamlit App
# -----------------------------------------------------------------------------
def main():
    st.title("🔬 AI Prompt Refinement 2.0")

    st.markdown("""
       **Goal:** Demonstrate how a well-structured prompt—based on both *default* and *custom* filters— 
       can help generate a high-quality answer from a normal AI model (GPT-4o Mini).
       
       **Steps**:
       1. Enter a naive prompt below.
       2. Generate custom filters (dynamic suggestions from the LLM).
       3. Adjust the *default filters* (answer format, length) and fill out the custom filters.
       4. Refine your prompt and see the final answer!
    """)

    # Naive Prompt
    naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

    # Button: Generate custom filters
    if st.button("Generate Custom Filters"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            with st.spinner("Analyzing your prompt to suggest custom filters..."):
                filters_data = generate_dynamic_filters(naive_prompt)
                st.session_state["custom_filters_data"] = filters_data
                st.success("Custom filters generated successfully!")

    # Always show default filters (above or below custom filters, your choice)
    default_filter_choices = get_default_filters()

    # If we have custom filter definitions, display them
    user_custom_choices = {}
    if "custom_filters_data" in st.session_state:
        custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
        user_custom_choices = display_custom_filters(custom_definitions)

    # Button: Refine Prompt
    if st.button("Refine Prompt"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            # Combine default + custom filters into a single dict
            all_filters = {
                "Default": default_filter_choices,
                "Custom": user_custom_choices
            }
            with st.spinner("Refining your prompt using Google Generative AI..."):
                refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                st.session_state["refined_prompt"] = refined_prompt
                st.success("Prompt refined successfully!")

    # If we have a refined prompt, show it and offer the final answer
    if "refined_prompt" in st.session_state:
        st.markdown("### 📌 Refined Prompt")
        st.text_area("Refined Prompt", st.session_state["refined_prompt"], height=120)

        if st.button("Get Final Answer from GPT-4o Mini"):
            with st.spinner("Generating response..."):
                gpt_response = generate_response_from_chatgpt(st.session_state["refined_prompt"])
            st.markdown("### 💬 GPT-4o Mini Response")
            st.write(gpt_response)


if __name__ == "__main__":
    main()
