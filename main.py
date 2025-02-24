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
import pytesseract
from docx import Document

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
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        flex: 1;
        height: 100%;
        overflow-y: auto;
        padding: 10px;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 10px;
        margin: 0;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 1;
        height: 100%;
        display: flex;
        flex-direction: column;
        border: 1px solid #ccc;
        border-radius: 10px;
        margin: 0;
    }
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        background-color: #f5f5f5;
        border-bottom: 1px solid #ccc;
    }
    .user-message {
        background-color: #DCF8C6;
        padding: 8px 12px;
        border-radius: 10px;
        margin: 5px 0;
        align-self: flex-end;
        max-width: 80%;
    }
    .ai-message {
        background-color: #FFFFFF;
        padding: 8px 12px;
        border-radius: 10px;
        margin: 5px 0;
        align-self: flex-start;
        max-width: 80%;
        border: 1px solid #ccc;
    }
    .chat-input {
        display: flex;
        padding: 10px;
        background-color: #fff;
    }
    .chat-input textarea {
        flex: 1;
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .chat-input button {
        margin-left: 10px;
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
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    col_left, col_right = st.columns([2, 3])

    # -----------------------
    # Left Column: Prompt Refinement
    # -----------------------
    with col_left:
        st.markdown(
            """
            **Instructions:**  
            1. Enter a naive prompt below.  
            2. Upload images and documents to analyze.  
            3. Click **Generate Custom Filters** or **Refine Prompt Directly**.  
            4. Adjust the **Default Filters** and fill out the **Custom Filters** if needed.  
            """
        )
        naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120, key="naive_prompt")

        st.markdown("### 📤 Upload Files")
        uploaded_images = st.file_uploader("", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="image_upload")
        uploaded_documents = st.file_uploader("", type=["pdf", "docx", "txt"], accept_multiple_files=True, key="document_upload")

        extracted_text = ""

        # Extract text from images
        if uploaded_images:
            st.markdown("### 🖼️ Extracted Text from Images")
            for img_file in uploaded_images:
                img = Image.open(img_file)
                text = pytesseract.image_to_string(img)
                extracted_text += text + "\n"
                st.text_area(f"Text from {img_file.name}", text, height=100)

        # Extract text from documents
        if uploaded_documents:
            st.markdown("### 📄 Extracted Text from Documents")
            for doc_file in uploaded_documents:
                doc_text = ""
                if doc_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(doc_file)
                    for page in pdf_reader.pages:
                        doc_text += page.extract_text() + "\n"
                elif doc_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(doc_file)
                    for para in doc.paragraphs:
                        doc_text += para.text + "\n"
                elif doc_file.type == "text/plain":
                    doc_text = doc_file.read().decode("utf-8")
                else:
                    doc_text = "Preview not supported for this file type."

                extracted_text += doc_text + "\n"
                st.text_area(f"Text from {doc_file.name}", doc_text, height=100)

        # Combine user prompt with extracted text for custom filter generation
        combined_prompt = naive_prompt + "\n" + extracted_text

        if st.button("Generate Custom Filters", key="gen_custom_filters"):
            if not combined_prompt.strip():
                st.error("Please enter a valid naive prompt or upload content.")
            else:
                with st.spinner("Analyzing your prompt and uploaded content to generate high-quality custom filters..."):
                    filters_data = generate_dynamic_filters(combined_prompt)
                    st.session_state["custom_filters_data"] = filters_data
                    st.success("Custom filters generated successfully!")

        if st.button("Refine Prompt Directly", key="refine_directly"):
            if not combined_prompt.strip():
                st.error("Please enter a valid naive prompt or upload content.")
            else:
                with st.spinner("Refining your prompt and uploaded content..."):
                    refined = refine_prompt_with_google_genai(combined_prompt, {})
                    st.session_state["refined_prompt"] = refined
                    st.success("Prompt refined successfully!")

    # -----------------------
    # Right Column: Chat Interface
    # -----------------------
    with col_right:
        st.markdown("### 💬 Chat Interface")

        # Chat container
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='ai-message'>{message['content']}</div>", unsafe_allow_html=True)

        # Chat input at the bottom
        with st.container():
            user_input = st.text_input("Type your message...", key="chat_input")
            if st.button("Send"):
                if user_input.strip():
                    # Append user message
                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                    # Generate AI response
                    with st.spinner("Generating response..."):
                        try:
                            gpt_response = generate_response_from_chatgpt(user_input)
                            st.session_state.chat_history.append({"role": "ai", "content": gpt_response})
                        except Exception as e:
                            st.session_state.chat_history.append({"role": "ai", "content": f"Error: {e}"})

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
