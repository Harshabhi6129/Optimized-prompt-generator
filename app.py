import openai
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="GPT-4o Mini Prompt Refinement Experiment", 
    layout="wide"
)

# Load environment variables
load_dotenv()

# Set API keys
openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
google_genai_key = st.secrets.get("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))

# Configure OpenAI
if not openai_api_key:
    logger.error("OpenAI API Key is missing.")
    st.error("OpenAI API Key is missing. Please set it in the environment.")
else:
    openai.api_key = openai_api_key
    logger.info("OpenAI API Key loaded successfully.")

# Configure Google Generative AI
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

def refine_prompt_with_google_genai(naive_prompt: str) -> str:
    """
    Use Google Generative AI (text-bison-001) to refine the naive prompt into a detailed and well-structured prompt.
    """
    try:
        refinement_instruction = (
            "You are an expert prompt optimizer. Transform the given naive prompt into a highly detailed, structured, "
            "and clear prompt that maximizes response quality from an AI model. Ensure it includes necessary context, "
            "clarifications, and formatting to improve the accuracy of the AI's response."
        )
        full_prompt = f"{refinement_instruction}\n\nNaive Prompt: {naive_prompt}"

        # Use a valid Google Generative AI model
        response = genai.generate_text(prompt=full_prompt, model="models/text-bison-001")
        refined_text = response.result.strip()
        logger.info("Prompt refined successfully with Google Generative AI.")
        return refined_text

    except AttributeError as e:
        logger.error(f"Google Generative AI AttributeError: {e}")
        st.error("The Google Generative AI library may be incorrectly used. Please check the library documentation.")
        return naive_prompt  # Fallback to the naive prompt if there's an error

    except Exception as e:
        logger.error(f"Error refining prompt with Google GenAI: {e}")
        st.error(f"Error refining prompt with Google GenAI: {e}")
        return naive_prompt

def generate_response_from_chatgpt(refined_prompt: str) -> str:
    """
    Send the refined prompt to GPT-4o Mini and retrieve the response.
    """
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant. Provide clear and precise answers."},
        {"role": "user", "content": refined_prompt},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        logger.info("Response generated successfully with GPT-4o Mini.")
        return response['choices'][0]['message']['content'].strip()

    except openai.error.InvalidRequestError as e:
        logger.error(f"InvalidRequestError: {e}")
        return "⚠️ Invalid model or request parameters."

    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return f"Error in generating response: {str(e)}"

def main():
    st.title("🔬 AI Prompt Refinement Experiment with GPT-4o Mini")

    st.markdown("""
       **Goal:** This experiment tests whether a well-structured prompt can make a normal AI model (GPT-4o Mini) 
       generate high-quality responses, comparable to more powerful models.
       
       1. Enter a naive prompt below.
       2. The system will refine it using Google Generative AI.
       3. The refined prompt will then be passed to **GPT-4o Mini**.
       4. Compare the results!
       """)

    naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=150)

    if st.button("Submit"):
        if not naive_prompt.strip():
            st.error("Please enter a valid prompt.")
            return

        with st.spinner("🔄 Refining your prompt using Google Generative AI..."):
            refined_prompt = refine_prompt_with_google_genai(naive_prompt)

        with st.spinner("🤖 Generating response from GPT-4o Mini..."):
            gpt_response = generate_response_from_chatgpt(refined_prompt)

        # Display Refined Prompt
        st.markdown("### 📌 Refined Prompt")
        st.text_area("Refined Prompt:", refined_prompt, height=100)

        st.markdown("### 💬 GPT-4o Mini Response")
        st.write(gpt_response)

if __name__ == "__main__":
    main()
