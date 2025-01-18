import openai
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import json

# -----------------------------------------------------------------------------
# Basic Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="GPT-4o Advanced Prompt Refinement",
    layout="wide"
)

load_dotenv()

openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
google_genai_key = st.secrets.get("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))

if not openai_api_key:
    logger.error("OpenAI API Key is missing.")
    st.error("OpenAI API Key is missing. Please set it in the environment.")
else:
    openai.api_key = openai_api_key
    logger.info("OpenAI API Key loaded successfully.")

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
# Load Gemini Pro Model
# -----------------------------------------------------------------------------
def load_gemini_pro(model_name: str) -> genai.GenerativeModel:
    try:
        return genai.GenerativeModel(model_name=model_name)
    except Exception as e:
        logger.error(f"Error loading Gemini Pro model {model_name}: {e}")
        st.error(f"Error loading Gemini Pro model: {e}")
        return None


# -----------------------------------------------------------------------------
# 1) Default Filters (Always Present)
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# 2) Generate Dynamic (Custom) Filters
# -----------------------------------------------------------------------------
def generate_dynamic_filters(naive_prompt: str) -> dict:
    """
    Asks the LLM to produce strictly valid JSON that defines custom filters
    relevant to the user's naive prompt.
    """

    # IMPORTANT: We strongly instruct the model to return ONLY JSON,
    # with no disclaimers or additional text.
    # We also remind it to keep the custom filters relevant to the prompt.
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

    # We embed the user prompt in the full_prompt
    full_prompt = f"{system_instruction}\n\nNaive Prompt:\n{naive_prompt}"

    model = load_gemini_pro("gemini-1.5-flash")
    if not model:
        st.error("Gemini Pro model not loaded successfully.")
        return {"custom_filters": []}

    # We'll try up to two attempts at generating valid JSON.
    # If it fails both times, we fallback.
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            response = model.generate_content(full_prompt)
            text_output = response.text.strip()
            logger.info(f"[Attempt {attempt}] LLM output: {text_output}")

            # Attempt to parse the model output as JSON
            parsed_output = json.loads(text_output)
            if "custom_filters" not in parsed_output:
                raise ValueError("No 'custom_filters' key found in JSON.")

            # If we get here, we have valid JSON with a 'custom_filters' list
            return parsed_output

        except Exception as e:
            logger.error(f"[Attempt {attempt}] JSON parse error: {e}")
            if attempt < max_attempts:
                st.warning("LLM returned invalid JSON. Retrying...")
            else:
                st.error(f"All attempts to parse filters failed. Using fallback filters.")

    # Final fallback if both attempts fail:
    return {
        "custom_filters": [
            {
                "type": "text_input",
                "label": "Fallback: Please specify your main goal",
                "key": "fallback_goal"
            }
        ]
    }


# -----------------------------------------------------------------------------
# 3) Display Custom Filters in the UI
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
            val = st.text_input(f_label, key=f_key)
            user_custom_choices[f_label] = val

        elif f_type == "checkbox":
            # If a single checkbox, user can either check or not
            if not f_options:
                # single checkbox
                val = st.checkbox(f_label, key=f_key)
                user_custom_choices[f_label] = val
            else:
                # multiple checkbox options
                # For multiple checkboxes you might want a multi_select approach,
                # but let's keep it simple: show each as a separate checkbox
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


# -----------------------------------------------------------------------------
# 4) Refine Prompt
# -----------------------------------------------------------------------------
def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    try:
        refinement_instruction = """
You are an expert prompt optimizer. Transform the given naive prompt into a highly detailed, 
structured, and clear prompt that maximizes response quality from an AI model.
Incorporate the user preferences below where relevant.
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


# -----------------------------------------------------------------------------
# 5) Generate Final Answer from GPT-4o
# -----------------------------------------------------------------------------
def generate_response_from_chatgpt(refined_prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant. Provide clear and precise answers."},
        {"role": "user", "content": refined_prompt},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Or replace with the relevant model name
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
    st.title("🔬 AI Prompt Refinement 2.1 — Strict JSON & Relevant Filters")

    st.markdown("""
        **Instructions**  
        1. Enter a naive prompt below.  
        2. Click **Generate Custom Filters**. The system tries to produce strictly valid JSON filter definitions.  
        3. Adjust the **Default Filters** (always present) and fill out the **Custom Filters**.  
        4. Click **Refine Prompt**, then **Get Final Answer** from GPT-4o Mini.
        
        If you see an error about invalid JSON, the model might have output extra text. We re-attempt once. If it still fails, you'll get fallback filters.
    """)

    # Naive Prompt
    naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

    # 2. Generate Custom Filters
    if st.button("Generate Custom Filters"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            with st.spinner("Analyzing your prompt to suggest custom filters..."):
                filters_data = generate_dynamic_filters(naive_prompt)
                st.session_state["custom_filters_data"] = filters_data
                st.success("Custom filters generated successfully!")

    # 1. Default Filters
    default_filter_choices = get_default_filters()

    # 3. Show Custom Filters if available
    user_custom_choices = {}
    if "custom_filters_data" in st.session_state:
        custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
        user_custom_choices = display_custom_filters(custom_definitions)

    # 4. Refine Prompt
    if st.button("Refine Prompt"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            # Combine both sets
            all_filters = {
                "Default": default_filter_choices,
                "Custom": user_custom_choices
            }
            with st.spinner("Refining your prompt with Google Generative AI..."):
                refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                st.session_state["refined_prompt"] = refined_prompt
                st.success("Prompt refined successfully!")

    # 5. If refined prompt is ready, show it & let user request final answer
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
