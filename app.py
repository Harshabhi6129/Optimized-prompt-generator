import openai
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

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
openai.api_key = openai_api_key

# Configure Google Generative AI
if google_genai_key:
    genai.configure(api_key=google_genai_key)
else:
    st.warning("Google Generative AI key not found. Please set it in the .env file.")

def refine_prompt_with_google_genai(naive_prompt: str) -> str:
    """
    Use Google Generative AI (gemini-1.5-flash) to refine the naive prompt into a detailed and well-structured prompt.
    """
    try:
        # Ensure the Google API is properly configured
        refinement_instruction = (
            "You are an expert prompt optimizer. Transform the given naive prompt into a highly detailed, structured, "
            "and clear prompt that maximizes response quality from an AI model. Ensure it includes necessary context, "
            "clarifications, and formatting to improve the accuracy of the AI's response."
        )
        full_prompt = f"{refinement_instruction}\n\nNaive Prompt: {naive_prompt}"

        # Use the Google Generative AI SDK's method to call the model
        response = genai.generate_text(
            model="models/text-bison-001",
            prompt=full_prompt,
        )
        refined_text = response.result.strip()
        return refined_text

    except Exception as e:
        st.error(f"Error refining prompt with Google GenAI: {e}")
        return naive_prompt  # Fallback to the naive prompt if there's an error

def generate_response_from_chatgpt(refined_prompt: str) -> str:
    """
    Send the refined prompt to GPT-4o Mini and retrieve the response.
    If the first attempt fails, it falls back to `gpt-4o-mini-2024-07-18`.
    """
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant. Provide clear and precise answers."},
        {"role": "user", "content": refined_prompt},
    ]

    try:
        # Attempt to use the OpenAI API with the specified model
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response['choices'][0]['message']['content'].strip()

    except openai.error.InvalidRequestError:
        return "⚠️ Invalid model or request parameters."

    except Exception as e:
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
