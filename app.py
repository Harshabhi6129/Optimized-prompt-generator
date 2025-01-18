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

openai_api_key = os.getenv("OPENAI_API_KEY", "")
google_genai_key = os.getenv("GOOGLE_GENAI_API_KEY", "")

if openai_api_key:
    openai.api_key = openai_api_key
    logger.info("OpenAI API Key loaded successfully.")
else:
    logger.error("OpenAI API Key is missing.")
    st.error("OpenAI API Key is missing. Please set it in the environment.")

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
    Asks the LLM to produce filter definitions relevant to the user's naive prompt.
    Returns a JSON with a "custom_filters" key containing the filter definitions.
    """
    system_instruction = """
Please read the user's naive prompt and propose relevant filters or questions 
that would help refine the final answer. Return a JSON object with a "custom_filters" 
key, which should be a list of filter definitions. Each definition includes:
- "type": one of ["text_input", "checkbox", "radio", "selectbox"]
- "label": short descriptive label
- "key": unique string key
- "options": array of strings (only if type is radio/selectbox or multi checkbox)
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

            parsed_output = json.loads(text_output)
            if "custom_filters" not in parsed_output:
                raise ValueError("No 'custom_filters' key found.")
            return parsed_output

        except Exception as e:
            logger.error(f"[Attempt {attempt}] JSON parse error: {e}")
            if attempt < max_attempts:
                st.warning("LLM returned invalid JSON. Retrying...")
            else:
                st.error("All attempts to parse filters failed. Using fallback.")

    return {
        "custom_filters": [
            {
                "type": "text_input",
                "label": "Fallback Filter",
                "key": "fallback_filter"
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
            # If there's a list of options, treat each as a separate checkbox
            if f_options:
                st.write(f_label)
                selected_options = []
                for opt in f_options:
                    cb_key = f"{f_key}_{opt}"
                    cb_value = st.checkbox(opt, key=cb_key)
                    if cb_value:
                        selected_options.append(opt)
                user_custom_choices[f_label] = selected_options
            else:
                # single checkbox
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
# 4) Conversation Memory
# -----------------------------------------------------------------------------
def init_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

def add_message_to_history(role: str, content: str):
    st.session_state["chat_history"].append({"role": role, "content": content})
    if len(st.session_state["chat_history"]) > 10:  # Limit history to 10 messages
        st.session_state["chat_history"].pop(0)

def display_conversation_history():
    st.sidebar.header("Conversation History")
    if "chat_history" in st.session_state and st.session_state["chat_history"]:
        for i, msg in enumerate(reversed(st.session_state["chat_history"])):
            role_label = "You" if msg["role"] == "user" else "Assistant"
            st.sidebar.write(f"**{role_label}:** {msg['content']}")


# -----------------------------------------------------------------------------
# Main Streamlit App
# -----------------------------------------------------------------------------
def main():
    init_chat_history()

    st.title("🔬 AI Prompt Refinement")

    st.markdown("""
        **Instructions:**  
        1. Enter a naive prompt below.  
        2. Generate custom filters based on your input.  
        3. Refine your prompt and receive an answer!  
        
        Previous messages are displayed in the sidebar on the left for easy navigation.
    """)

    # Naive Prompt
    naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

    if st.button("Generate Custom Filters"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            add_message_to_history("user", naive_prompt)
            with st.spinner("Analyzing your prompt to suggest custom filters..."):
                filters_data = generate_dynamic_filters(naive_prompt)
                st.session_state["custom_filters_data"] = filters_data
            st.success("Custom filters generated successfully!")

    # Default Filters
    default_filter_choices = get_default_filters()

    # If we have custom filter definitions, display them
    user_custom_choices = {}
    if "custom_filters_data" in st.session_state:
        custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
        user_custom_choices = display_custom_filters(custom_definitions)

    if st.button("Refine Prompt"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            all_filters = {
                "Default": default_filter_choices,
                "Custom": user_custom_choices
            }
            with st.spinner("Refining your prompt..."):
                refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                st.session_state["refined_prompt"] = refined_prompt
            st.success("Prompt refined successfully!")
            add_message_to_history("assistant", refined_prompt)

    if "refined_prompt" in st.session_state:
        st.markdown("### 📌 Refined Prompt")
        st.text_area("Refined Prompt", st.session_state["refined_prompt"], height=120)

        if st.button("Get Final Answer"):
            with st.spinner("Generating response..."):
                final_answer = generate_response_from_chatgpt(st.session_state["refined_prompt"])
                st.session_state["final_answer"] = final_answer
            st.markdown("### 💬 GPT-4o Mini Response")
            st.write(st.session_state["final_answer"])
            add_message_to_history("assistant", st.session_state["final_answer"])

    # Display conversation history in the sidebar
    display_conversation_history()


if __name__ == "__main__":
    main()
