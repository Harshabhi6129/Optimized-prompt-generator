import openai
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def generate_response_from_chatgpt(refined_prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant..."},
        {"role": "user", "content": refined_prompt},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or your actual model name
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
