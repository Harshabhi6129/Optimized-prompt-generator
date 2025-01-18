import openai
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def generate_response_from_chatgpt(refined_prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant."},
        {"role": "user", "content": refined_prompt}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"GPT-4o Mini Error: {e}")
        return "Error generating response."
