import openai
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def generate_response_from_chatgpt(refined_prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a knowledgeable assistant. Provide clear and precise answers."},
        {"role": "user", "content": refined_prompt},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Error generating response."
