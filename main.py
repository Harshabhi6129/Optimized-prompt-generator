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
    /* Global styles */
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
    /* Two-column layout */
    div[data-testid="stHorizontalBlock"] {
        margin: 0;
        padding: 0;
        width: 100%;
        height: calc(100vh - 80px);
        display: flex;
        flex-direction: row;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1;
        height: 100%;
        overflow-y: auto;
        padding: 10px;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 10px;
        margin: 0;
    }
    /* Chat Interface Styles */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        background-color: #f5f5f5;
        border-bottom: 1px solid #ccc;
    }
    .user-message {
        background-color: #DCF8C6;
        color: #000;
        padding: 8px 12px;
        border-radius: 10px;
        margin: 5px 0;
        align-self: flex-end;
        max-width: 80%;
    }
    .ai-message {
        background-color: #FFFFFF;
        color: #000;
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
    # Ensure chat_history exists in session_state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    col_left, col_right = st.columns([2, 3])
    
    # -----------------------
    # Left Column: Inputs, File Upload & Prompt Refinement
    # -----------------------
    with col_left:
        st.markdown(
            """
            **Instructions:**  
            1. Enter a naive prompt below.  
            2. Upload images and documents to analyze.  
            3. Click **Generate Custom Filters** or **Refine Prompt Directly**.  
            4. Adjust the **Default Filters** and fill out the **Custom Filters** if needed.  
            5. The refined prompt and final output will appear on the right side.
            """
        )
        naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120, key="naive_prompt")
        
        st.markdown("### 📤 Upload Files")
        uploaded_images = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="image_upload")
        uploaded_documents = st.file_uploader("Upload Documents", type=["pdf", "docx", "txt"], accept_multiple_files=True, key="document_upload")
        
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
        
        # Combine naive prompt and extracted text
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
        
        default_filters = get_default_filters()
        
        custom_choices = {}
        if "custom_filters_data" in st.session_state:
            custom_definitions = st.session_state["custom_filters_data"].get("custom_filters", [])
            custom_choices = display_custom_filters(custom_definitions)
        
        if st.button("Refine Prompt with Filters", key="refine_with_filters"):
            if not combined_prompt.strip():
                st.error("Please enter a valid naive prompt or upload content.")
            else:
                filters_all = {"Default": default_filters, "Custom": custom_choices}
                with st.spinner("Refining your prompt using your preferences and uploaded content..."):
                    refined = refine_prompt_with_google_genai(combined_prompt, filters_all)
                    st.session_state["refined_prompt"] = refined
                    st.success("Prompt refined successfully!")
    
    # -----------------------
    # Right Column: Chat Interface
    # -----------------------
    with col_right:
        st.markdown("### 💬 Chat Interface")
        
        # Pre-populate chat input with the refined prompt, if available, but do not auto-send it.
        refined_text = st.session_state.get("refined_prompt", "")
        if refined_text and not st.session_state.get("chat_input"):
            st.session_state["chat_input"] = refined_text
        
        # Chat container: build HTML from chat history
        chat_container = st.empty()
        chat_html = ""
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                chat_html += f"<div class='user-message'>{message['content']}</div>"
            else:
                chat_html += f"<div class='ai-message'>{message['content']}</div>"
        chat_container.markdown(chat_html, unsafe_allow_html=True)
        
        # Function to send a chat message and update chat history
        def send_message():
            if st.session_state.chat_input.strip():
                # 1) Append user message
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": st.session_state.chat_input
                })
                # 2) Generate AI response
                try:
                    gpt_response = generate_response_from_chatgpt(st.session_state.chat_input)
                    st.session_state.chat_history.append({
                        "role": "ai",
                        "content": gpt_response
                    })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "ai",
                        "content": f"Error: {e}"
                    })
                # 3) Clear the text box (no st.experimental_rerun needed)
                st.session_state.chat_input = ""
        
        # Chat input and "Send" button (no st.experimental_rerun to avoid warnings)
        st.text_input("Type your message...", key="chat_input")
        st.button("Send", on_click=send_message, key="chat_send")
        
        # Rebuild chat container HTML after the message is sent
        updated_chat_html = ""
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                updated_chat_html += f"<div class='user-message'>{message['content']}</div>"
            else:
                updated_chat_html += f"<div class='ai-message'>{message['content']}</div>"
        chat_container.markdown(updated_chat_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
