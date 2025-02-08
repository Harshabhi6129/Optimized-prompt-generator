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
    /* Ensure the entire page fills the viewport without overall scrolling */
    html, body {
      height: 100vh;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }
    /* Remove default padding/margins from Streamlit’s main container and force full width/height */
    [data-testid="stAppViewContainer"] {
      padding: 0;
      margin: 0;
      width: 100%;
      height: 100vh;
    }
    /* Ensure the horizontal block (columns container) spans full width */
    div[data-testid="stHorizontalBlock"] {
      margin: 0;
      padding: 0;
      width: 100%;
    }
    /* Style the left and right column containers */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1),
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
         border: 1px solid #ccc;
         height: calc(100vh - 80px); /* Adjust if needed */
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
# Title (Outside of the bordered, scrollable divs)
# -----------------------------------------------------------------------------
st.markdown(
    "<h1 style='text-align: center; margin: 10px 0;'>🔬 AI Prompt Refinement</h1>",
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def main():
    # Create two main columns for content that stretch the full width of the page
    col_left, col_right = st.columns([2, 3])
    
    # -----------------------
    # Left Column: Inputs & Filters
    # -----------------------
    with col_left:
        st.markdown(
            """
            **Instructions:**  
            1. Enter a naive prompt below.  
            2. Click **Generate Custom Filters** or **Refine Prompt Directly**.  
            3. Adjust the **Default Filters** and fill out the **Custom Filters** if needed.  
            4. The refined prompt and the final output will appear on the right side.
            """
        )
        naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120, key="naive_prompt")

        # Button: Generate Custom Filters
        if st.button("Generate Custom Filters", key="gen_custom_filters"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                with st.spinner("Analyzing your prompt to generate high-quality custom filters..."):
                    filters_data = generate_dynamic_filters(naive_prompt)
                    st.session_state["custom_filters_data"] = filters_data
                    st.success("Custom filters generated successfully!")

        # Button: Refine Prompt Directly
        if st.button("Refine Prompt Directly", key="refine_directly"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                with st.spinner("Refining your prompt..."):
                    refined = refine_prompt_with_google_genai(naive_prompt, {})
                    st.session_state["refined_prompt"] = refined
                    st.success("Prompt refined successfully!")

        # Default Filters
        default_filters = get_default_filters()

        # Display Custom Filters (if available)
        custom_choices = {}
        if "custom_filters_data" in st.session_state:
            custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
            custom_choices = display_custom_filters(custom_definitions)

        # Button: Refine Prompt with Filters
        if st.button("Refine Prompt with Filters", key="refine_with_filters"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                filters_all = {
                    "Default": default_filters,
                    "Custom": custom_choices
                }
                with st.spinner("Refining your prompt using your preferences..."):
                    refined = refine_prompt_with_google_genai(naive_prompt, filters_all)
                    st.session_state["refined_prompt"] = refined
                    st.success("Prompt refined successfully!")
    
    # -----------------------
    # Right Column: Refined Prompt & Output
    # -----------------------
    with col_right:
        refined_text = st.session_state.get("refined_prompt", "")
        if refined_text:
            st.markdown("### 📌 Editable Refined Prompt")
            # Allow the user to edit the refined prompt
            editable_prompt = st.text_area(
                "Refined Prompt (Editable)",
                refined_text,
                height=120,
                key="editable_refined_prompt"
            )
            # Update the session state with any edits
            st.session_state["refined_prompt"] = editable_prompt

            # Button: Get Final Answer
            if st.button("Submit", key="submit_final"):
                final_prompt = st.session_state.get("refined_prompt", "").strip()
                if not final_prompt:
                    st.error("Refined prompt is empty. Please refine the prompt before submitting.")
                else:
                    # Debug: print out the prompt being submitted
                    st.write("**DEBUG:** Final prompt submitted:", final_prompt)
                    with st.spinner("Generating final response..."):
                        try:
                            gpt_response = generate_response_from_chatgpt(final_prompt)
                            st.markdown("### 💬 Response")
                            st.write(gpt_response)
                        except Exception as e:
                            st.error(f"Error generating response: {e}")
        else:
            st.info("Your refined prompt will appear here once generated.")

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
