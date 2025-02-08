import streamlit as st
import os
from dotenv import load_dotenv
from filters import get_default_filters, generate_dynamic_filters, display_custom_filters
from prompt_refinement import refine_prompt_with_google_genai
from gpt4o_response import generate_response_from_chatgpt
from model_loader import configure_genai

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
# Inject Custom CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Ensure the overall page occupies the full viewport and prevent overall scrolling */
    html, body {
      height: 100vh;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }
    /* Remove default padding from Streamlit's main container */
    [data-testid="stAppViewContainer"] {
      padding: 0;
      margin: 0;
    }
    /* Remove any margins/padding from the horizontal block container */
    div[data-testid="stHorizontalBlock"] {
      margin: 0;
      padding: 0;
    }
    /* Style the left and right column containers:
       - Full height (100vh) for container-only scrolling.
       - 10px padding.
       - Rounded edges.
       - Border.
    */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1),
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
         border: 1px solid #ccc;
         height: 100vh;
         overflow-y: auto;
         padding: 10px;
         box-sizing: border-box;
         border-radius: 10px;
         margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def main():
    # Create two main columns; they will fill the width (no extra page margins)
    col_left, col_right = st.columns([2, 3])

    # -----------------------
    # Left Side: Inputs & Filters
    # -----------------------
    with col_left:
        st.markdown(
            "<h1 style='text-align: left;'>🔬 AI Prompt Refinement</h1>",
            unsafe_allow_html=True
        )
        st.write("")  # Vertical spacing

        st.markdown(
            """
            **Instructions**  
            1. Enter a naive prompt below.  
            2. Click **Generate Custom Filters** or **Refine Prompt Directly**.  
            3. Adjust the **Default Filters** and fill out the **Custom Filters** if needed.  
            4. The refined prompt and the final output will appear on the right side.
            """
        )

        naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

        # Buttons: Generate Custom Filters and Refine Prompt Directly
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Generate Custom Filters"):
                if not naive_prompt.strip():
                    st.error("Please enter a valid naive prompt.")
                else:
                    with st.spinner("Analyzing your prompt to generate high-quality custom filters..."):
                        filters_data = generate_dynamic_filters(naive_prompt)
                        st.session_state["custom_filters_data"] = filters_data
                        st.success("Custom filters generated successfully!")
        with col2:
            if st.button("Refine Prompt Directly"):
                if not naive_prompt.strip():
                    st.error("Please enter a valid naive prompt.")
                else:
                    with st.spinner("Refining your prompt..."):
                        refined_prompt = refine_prompt_with_google_genai(naive_prompt, {})
                        st.session_state["refined_prompt"] = refined_prompt
                        st.success("Prompt refined successfully!")

        # Default Filters
        default_filter_choices = get_default_filters()

        # Display Custom Filters (if available)
        user_custom_choices = {}
        if "custom_filters_data" in st.session_state:
            custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
            user_custom_choices = display_custom_filters(custom_definitions)

        # Button: Refine Prompt with Filters
        if st.button("Refine Prompt with Filters"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                all_filters = {
                    "Default": default_filter_choices,
                    "Custom": user_custom_choices
                }
                with st.spinner("Refining your prompt using your preferences..."):
                    refined_prompt = refine_prompt_with_google_genai(naive_prompt, all_filters)
                    st.session_state["refined_prompt"] = refined_prompt
                    st.success("Prompt refined successfully!")

    # -----------------------
    # Right Side: Refined Prompt & Final Output
    # -----------------------
    with col_right:
        if "refined_prompt" in st.session_state:
            st.markdown("### 📌 Editable Refined Prompt")
            editable_refined_prompt = st.text_area(
                "Refined Prompt (Editable)",
                st.session_state["refined_prompt"],
                height=120,
                key="editable_refined_prompt"
            )
            st.session_state["refined_prompt"] = editable_refined_prompt  # Update if the user edits the refined prompt

            if st.button("Submit"):
                with st.spinner("Generating final response..."):
                    gpt_response = generate_response_from_chatgpt(st.session_state["refined_prompt"])
                st.markdown("### 💬 Response")
                st.write(gpt_response)

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
