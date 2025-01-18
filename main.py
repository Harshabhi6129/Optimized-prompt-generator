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

# Custom CSS for Scrollable Divisions
st.markdown("""
    <style>
    /* Main layout container */
    .main-container {
        display: flex;
        height: 85vh; /* Adjust height as needed */
        overflow: hidden;
    }

    /* Left Section Styling */
    .left-container {
        flex: 2; /* Adjust flex ratio to control width */
        overflow-y: auto;
        padding: 1rem;
        border-right: 1px solid #ddd;
    }

    /* Right Section Styling */
    .right-container {
        flex: 3; /* Adjust flex ratio to control width */
        overflow-y: auto;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def main():
    # Create scrollable divisions with custom HTML
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Left Side: Inputs
    st.markdown('<div class="left-container">', unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align: left;'>🔬 AI Prompt Refinement 2.1</h1>",
        unsafe_allow_html=True
    )
    st.write("")  # Vertical spacing

    # Instructions
    st.markdown("""
        **Instructions**  
        1. Enter a naive prompt below.  
        2. Click **Generate Custom Filters**.  
        3. Adjust the **Default Filters** and fill out the **Custom Filters**.  
        4. Refined Prompt and Output will appear on the right side.
    """)

    # Naive Prompt Input
    naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

    # Button: Generate Custom Filters
    if st.button("Generate Custom Filters", key="generate_filters"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            with st.spinner("Analyzing your prompt to suggest custom filters..."):
                filters_data = generate_dynamic_filters(naive_prompt)
                st.session_state["custom_filters_data"] = filters_data
                st.success("Custom filters generated successfully!")

    # Default Filters
    default_filter_choices = get_default_filters()

    # Display Custom Filters
    user_custom_choices = {}
    if "custom_filters_data" in st.session_state:
        custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
        user_custom_choices = display_custom_filters(custom_definitions)

    # Button: Refine Prompt
    if st.button("Refine Prompt", key="refine_prompt"):
        if not naive_prompt.strip():
            st.error("Please enter a valid naive prompt.")
        else:
            # Combine Default and Custom Filters
            all_filters = {
                "Default": default_filter_choices,
                "Custom": user_custom_choices
            }
            with st.spinner("Refining your prompt with Google Generative AI..."):
                refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                st.session_state["refined_prompt"] = refined_prompt
                st.success("Prompt refined successfully!")
    st.markdown('</div>', unsafe_allow_html=True)  # Close left-container

    # Right Side: Outputs
    st.markdown('<div class="right-container">', unsafe_allow_html=True)

    # Refined Prompt Section
    if "refined_prompt" in st.session_state:
        st.markdown("### 📌 Refined Prompt")
        st.text_area("Refined Prompt", st.session_state["refined_prompt"], height=120)

        # Button: Get Final Answer
        if st.button("Get Final Answer from GPT-4o Mini", key="generate_answer"):
            with st.spinner("Generating response..."):
                gpt_response = generate_response_from_chatgpt(st.session_state["refined_prompt"])
            st.markdown("### 💬 GPT-4o Mini Response")
            st.write(gpt_response)
    st.markdown('</div>', unsafe_allow_html=True)  # Close right-container

    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
