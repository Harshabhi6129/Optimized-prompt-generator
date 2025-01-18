import os
import streamlit as st
import openai
import logging
from dotenv import load_dotenv
import google.generativeai as genai

from filters import get_default_filters, generate_dynamic_filters, display_custom_filters
from prompt_refinement import refine_prompt_with_google_genai
from gpt4o_response import generate_response_from_chatgpt

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(page_title="GPT-4o Advanced Prompt Refinement", layout="wide")

    load_dotenv()

    openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    google_genai_key = st.secrets.get("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))

    if not openai_api_key:
        st.error("OpenAI API Key is missing.")
    else:
        openai.api_key = openai_api_key

    if google_genai_key:
        try:
            genai.configure(api_key=google_genai_key)
        except Exception as e:
            st.error(f"Error configuring Google Generative AI: {e}")
    else:
        st.warning("Google Generative AI key not found.")

    # Center the title
    st.markdown("<h1 style='text-align: center;'>🔬 AI Prompt Refinement 2.1</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")

    col_left, col_center, col_right = st.columns([1,2,1])
    with col_center:
        st.markdown("""
        **Instructions**  
        1. Enter a naive prompt below.  
        2. Click **Generate Custom Filters**. ...  
        """)

        naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

        if st.button("Generate Custom Filters"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                with st.spinner("Analyzing..."):
                    filters_data = generate_dynamic_filters(naive_prompt)
                    st.session_state["custom_filters_data"] = filters_data
                    st.success("Custom filters generated successfully!")

        default_filter_choices = get_default_filters()

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
                with st.spinner("Refining prompt..."):
                    refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                    st.session_state["refined_prompt"] = refined_prompt
                    st.success("Prompt refined successfully!")

        if "refined_prompt" in st.session_state:
            st.markdown("### 📌 Refined Prompt")
            st.text_area("Refined Prompt", st.session_state["refined_prompt"], height=120)

            if st.button("Get Final Answer from GPT-4o Mini"):
                with st.spinner("Generating answer..."):
                    gpt_response = generate_response_from_chatgpt(st.session_state["refined_prompt"])
                st.markdown("### 💬 GPT-4o Mini Response")
                st.write(gpt_response)

if __name__ == "__main__":
    main()