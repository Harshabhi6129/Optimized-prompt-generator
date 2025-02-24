import streamlit as st
import os
from dotenv import load_dotenv
import openai
import time

from filters import get_default_filters, generate_dynamic_filters, display_custom_filters
from prompt_refinement import refine_prompt_with_google_genai
from gpt4o_response import generate_response_from_chatgpt
from model_loader import configure_genai

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
    /* Ensure the entire page fits within the viewport and prevent scrolling */
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
    /* Layout for the horizontal block (two columns) */
    div[data-testid="stHorizontalBlock"] {
        margin: 0;
        padding: 0;
        width: 100%;
        height: calc(100vh - 80px);
        display: flex;
        flex-direction: row;
    }
    /* Styling for individual columns */
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
    # Ensure chat_history exists in session_state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    col_left, col_right = st.columns([2, 3])
    
    # -----------------------
    # Left Column: Inputs & Filters
    # -----------------------
    with col_left:
        st.markdown(
            """
            **Instructions:**  
            1. Enter a naive prompt below.  
            2. Upload images and documents to analyze.  
            3. Click **Generate Custom Filters** or **Refine Prompt Directly**.  
            4. Adjust the **Default Filters** and fill out the **Custom Filters** if needed.  
            5. The refined prompt and the final output will appear on the right side.
            """
        )
        naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120, key="naive_prompt")
        
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
    
    # -----------------------
    # Right Column: Chat Interface
    # -----------------------
    with col_right:
        # If a refined prompt exists, add it to the chat history as a user message
        refined_text = st.session_state.get("refined_prompt", "")
        if refined_text:
            if not st.session_state.chat_history or st.session_state.chat_history[-1]["content"] != refined_text:
                st.session_state.chat_history.append({"role": "user", "content": refined_text})
        
        st.markdown("### 💬 Chat Interface")
        
        # Chat container: build chat HTML from chat history
        chat_container = st.empty()
        chat_html = ""
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                chat_html += f"<div class='user-message'>{message['content']}</div>"
            else:
                chat_html += f"<div class='ai-message'>{message['content']}</div>"
        chat_container.markdown(chat_html, unsafe_allow_html=True)
        
        # Function to send message and refresh chat immediately
        def send_message():
            if st.session_state.chat_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": st.session_state.chat_input})
                try:
                    gpt_response = generate_response_from_chatgpt(st.session_state.chat_input)
                    st.session_state.chat_history.append({"role": "ai", "content": gpt_response})
                except Exception as e:
                    st.session_state.chat_history.append({"role": "ai", "content": f"Error: {e}"})
                st.session_state.chat_input = ""
                st.experimental_rerun()
        
        # Chat input at the bottom with a "Send" button
        user_input = st.text_input("Type your message...", key="chat_input")
        if st.button("Send", key="chat_send"):
            send_message()

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
