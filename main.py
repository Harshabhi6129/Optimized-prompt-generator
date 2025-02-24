import streamlit as st
import os
from dotenv import load_dotenv
import openai
import time
from filters import get_default_filters, generate_dynamic_filters, display_custom_filters
from prompt_refinement import refine_prompt_with_google_genai
from gpt4o_response import generate_response_from_chatgpt
from model_loader import configure_genai
from PIL import Image
import PyPDF2

# -----------------------------------------------------------------------------
# Streamlit Setup
# -----------------------------------------------------------------------------
st.set_page_config(page_title="GPT-4o Advanced Prompt Refinement", layout="wide")
load_dotenv()

# Retrieve API keys from secrets or environment variables
openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
google_genai_key = st.secrets.get("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))

if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.error("OpenAI API key not provided. Please set OPENAI_API_KEY in your secrets or environment variables.")

configure_genai(openai_api_key, google_genai_key)

# -----------------------------------------------------------------------------
# Inject Custom CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body {
        height: 100vh;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0;
        margin: 0;
        width: 100%;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stHorizontalBlock"] {
        margin: 0;
        padding: 0;
        width: 100%;
        height: calc(100vh - 80px);
        display: flex;
        flex-direction: row;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1),
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 1;
        height: 100%;
        overflow-y: auto;
        padding: 10px;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 10px;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------
st.markdown(
    "<h1 style='text-align: center; margin: 10px 0;'>🔬 AI Prompt Refinement</h1>",
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def main():
    col_left, col_right = st.columns([2, 3])

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

        uploaded_images = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        uploaded_documents = st.file_uploader("Upload Documents", type=["pdf", "docx", "txt"], accept_multiple_files=True)

        if st.button("Generate Custom Filters", key="gen_custom_filters"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                with st.spinner("Analyzing your prompt to generate high-quality custom filters..."):
                    filters_data = generate_dynamic_filters(naive_prompt)
                    st.session_state["custom_filters_data"] = filters_data
                    st.success("Custom filters generated successfully!")

        if st.button("Refine Prompt Directly", key="refine_directly"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                with st.spinner("Refining your prompt..."):
                    refined = refine_prompt_with_google_genai(naive_prompt, {})
                    st.session_state["refined_prompt"] = refined
                    st.success("Prompt refined successfully!")

        default_filters = get_default_filters()

        custom_choices = {}
        if "custom_filters_data" in st.session_state:
            custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
            custom_choices = display_custom_filters(custom_definitions)

        if st.button("Refine Prompt with Filters", key="refine_with_filters"):
            if not naive_prompt.strip():
                st.error("Please enter a valid naive prompt.")
            else:
                filters_all = {"Default": default_filters, "Custom": custom_choices}
                with st.spinner("Refining your prompt using your preferences..."):
                    refined = refine_prompt_with_google_genai(naive_prompt, filters_all)
                    st.session_state["refined_prompt"] = refined
                    st.success("Prompt refined successfully!")

    with col_right:
        refined_text = st.session_state.get("refined_prompt", "")
        if refined_text:
            st.markdown("### 📌 Editable Refined Prompt")
            editable_prompt = st.text_area(
                "Refined Prompt (Editable)",
                refined_text,
                height=120,
                key="editable_refined_prompt"
            )
            st.session_state["refined_prompt"] = editable_prompt

            if st.button("Submit", key="submit_final"):
                final_prompt = st.session_state.get("refined_prompt", "").strip()
                if not final_prompt:
                    st.error("Refined prompt is empty. Please refine the prompt before submitting.")
                else:
                    with st.spinner("Generating final response..."):
                        retries = 0
                        success = False
                        while retries < 3 and not success:
                            try:
                                gpt_response = generate_response_from_chatgpt(final_prompt)
                                success = True
                            except Exception as e:
                                if "502" in str(e):
                                    retries += 1
                                    time.sleep(2)
                                else:
                                    st.error(f"Error generating response: {e}")
                                    break
                        if success:
                            st.markdown("### 💬 Response")
                            st.markdown(gpt_response)
                        else:
                            st.error("Failed to generate response after multiple attempts.")
        else:
            st.info("Your refined prompt will appear here once generated.")

        if uploaded_images:
            st.markdown("### 🖼️ Uploaded Images")
            for img_file in uploaded_images:
                img = Image.open(img_file)
                st.image(img, caption=img_file.name)

        if uploaded_documents:
            st.markdown("### 📄 Uploaded Documents")
            for doc_file in uploaded_documents:
                st.write(f"**{doc_file.name}**")
                if doc_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(doc_file)
                    for page in pdf_reader.pages:
                        st.text(page.extract_text())
                elif doc_file.type == "text/plain":
                    st.text(doc_file.read().decode("utf-8"))
                else:
                    st.write("Preview not supported for this file type.")

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
