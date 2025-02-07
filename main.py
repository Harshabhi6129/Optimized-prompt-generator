import streamlit as st
from dotenv import load_dotenv
from filters import get_default_filters, generate_dynamic_filters, display_custom_filters
from prompt_refinement import refine_prompt_with_google_genai
from gpt4o_response import generate_response_from_chatgpt
from model_loader import configure_genai
import os

# -----------------------------------------------------------------------------
# Streamlit Setup
# -----------------------------------------------------------------------------
st.set_page_config(page_title="GPT-4o Advanced Prompt Refinement", layout="wide")
load_dotenv()

# Configure Generative AI
openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
google_genai_key = st.secrets.get("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))
configure_genai(openai_api_key, google_genai_key)

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def main():
    # Create two main columns for layout: left (prompt area) and right (result area)
    col_left, col_right = st.columns([2, 3])  # Adjust width ratio as needed

    # -----------------------------
    # Left Side: Prompt Area
    # -----------------------------
    with col_left:
        st.markdown("<h1 style='text-align: left;'>🔬 AI Prompt Refinement </h1>", unsafe_allow_html=True)
        st.write("")  # Vertical spacing

        # Divide the left area into two subcolumns: one for prompt input and one for filter settings.
        left_prompt_col, left_filters_col = st.columns(2)

        # --- Left Prompt Column: Naive Prompt & Action Buttons ---
        with left_prompt_col:
            st.markdown("### Enter Your Naive Prompt")
            st.markdown(
                """
                **Instructions:**  
                1. Enter your naive prompt below.  
                2. Use the buttons to generate custom filters or refine the prompt directly.
                """
            )
            naive_prompt = st.text_area("Naive Prompt:", "", height=120)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Generate Custom Filters"):
                    if not naive_prompt.strip():
                        st.error("Please enter a valid naive prompt.")
                    else:
                        with st.spinner("Analyzing your prompt to generate high-quality custom filters..."):
                            filters_data = generate_dynamic_filters(naive_prompt)
                            st.session_state["custom_filters_data"] = filters_data
                            st.success("Custom filters generated successfully!")
            with col_btn2:
                if st.button("Refine Prompt Directly"):
                    if not naive_prompt.strip():
                        st.error("Please enter a valid naive prompt.")
                    else:
                        with st.spinner("Refining your prompt..."):
                            refined_prompt = refine_prompt_with_google_genai(naive_prompt, {})
                            st.session_state["refined_prompt"] = refined_prompt
                            st.success("Prompt refined successfully!")

        # --- Left Filters Column: Default & Custom Filters ---
        with left_filters_col:
            st.markdown("### Set Your Preferences")
            default_filter_choices = get_default_filters()
            user_custom_choices = {}
            if "custom_filters_data" in st.session_state:
                custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
                user_custom_choices = display_custom_filters(custom_definitions)
            if st.button("Refine Prompt with Filters"):
                if not naive_prompt.strip():
                    st.error("Please enter a valid naive prompt.")
                else:
                    # Combine Default and Custom Filters and refine the prompt.
                    all_filters = {
                        "Default": default_filter_choices,
                        "Custom": user_custom_choices
                    }
                    with st.spinner("Refining your prompt using your preferences..."):
                        refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                        st.session_state["refined_prompt"] = refined_prompt
                        st.success("Prompt refined successfully!")

    # -----------------------------
    # Right Side: Result Area
    # -----------------------------
    with col_right:
        # Divide the right area into two subcolumns: one for the editable refined prompt and one for final output.
        refined_col, final_col = st.columns(2)

        # --- Refined Prompt Column ---
        with refined_col:
            st.markdown("### 📌 Editable Refined Prompt")
            if "refined_prompt" in st.session_state:
                editable_refined_prompt = st.text_area(
                    "Refined Prompt (Editable)", 
                    st.session_state["refined_prompt"], 
                    height=120, 
                    key="editable_refined_prompt"
                )
                st.session_state["refined_prompt"] = editable_refined_prompt  # Update if user edits the refined prompt
            if st.button("Submit"):
                with st.spinner("Generating final response..."):
                    gpt_response = generate_response_from_chatgpt(st.session_state["refined_prompt"])
                    st.session_state["final_response"] = gpt_response

        # --- Final Response Column ---
        with final_col:
            st.markdown("### 💬 Final Response")
            if "final_response" in st.session_state:
                st.write(st.session_state["final_response"])

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
