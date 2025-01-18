import openai
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from PIL import Image
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="GPT-4o Advanced Prompt Refinement",
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


# -----------------------------------------------------------------------------
# Utility: Load Gemini Pro Model
# -----------------------------------------------------------------------------
def load_gemini_pro(model_name: str) -> genai.GenerativeModel:
    """Returns the Gemini Pro Generative model."""
    try:
        model = genai.GenerativeModel(model_name=model_name)
        return model
    except Exception as e:
        logger.error(f"Error loading Gemini Pro model {model_name}: {e}")
        st.error(f"Error loading Gemini Pro model: {e}")
        return None


# -----------------------------------------------------------------------------
# Step 1: Generate Dynamic Filters from LLM
# -----------------------------------------------------------------------------
def generate_dynamic_filters(naive_prompt: str) -> dict:
    """
    Use Google Generative AI (or any other LLM) to generate
    possible filters/questions for refining the naive prompt.

    Returns a dictionary with keys like:
      {
        "filters": [
            "Long explanation vs. short explanation",
            "Layman-friendly vs. technical depth",
            ...
        ],
        "questions": [
            "What is the target audience?",
            "Preferred format: bullet points, paragraphs, etc.?"
            ...
        ]
      }
    You can choose your own structure for the JSON.

    NOTE: This is just an example prompt and parsing structure.
    """
    try:
        # Instruction: we want the model to analyze the naive prompt and propose dynamic refinement options
        filter_prompt = f"""
            You are an AI assistant that helps refine user prompts. 
            Based on the naive prompt below, propose a set of possible "filters" or user preferences 
            that would help clarify or improve the final answer. Also propose clarifying questions
            the user might need to answer.

            Naive prompt: {naive_prompt}

            Return your answer in valid JSON with two keys: 
            "filters" (an array of strings) and "questions" (an array of strings).
        """

        model = load_gemini_pro("gemini-1.5-flash")
        if not model:
            raise Exception("Gemini Pro model not loaded successfully.")

        response = model.generate_content(filter_prompt)
        text_output = response.text.strip()

        # Attempt to parse the output as JSON.
        # If the model output is not strictly valid JSON, 
        # you might do some fallback or cleansing here.
        parsed_output = json.loads(text_output)

        # Example of structure: {
        #    "filters": ["Long explanation vs short explanation", "Level: Basic vs. Expert", ...],
        #    "questions": ["Who is the target audience?", "Preferred format (bullets, paragraphs)?", ...]
        # }
        return parsed_output

    except Exception as e:
        logger.error(f"Error generating dynamic filters: {e}")
        st.error(f"Error generating dynamic filters: {e}")

        # Return a default set if there's an error
        return {
            "filters": [
                "Long explanation vs short explanation",
                "Layman vs technical detail"
            ],
            "questions": [
                "What is the target audience?",
                "Preferred format?"
            ]
        }


# -----------------------------------------------------------------------------
# Step 2: Refine Prompt with Google Generative AI + User Filters
# -----------------------------------------------------------------------------
def refine_prompt_with_google_genai(naive_prompt: str, user_choices: dict) -> str:
    """
    Use Google Generative AI to refine the naive prompt into a detailed
    and well-structured prompt, now *including* user choices from the dynamic filters.

    :param naive_prompt: Original user prompt
    :param user_choices: Dictionary containing user’s selected filters or answers
    :return: Refined prompt (string)
    """
    try:
        # Build an instruction that includes the user filters and choices
        refinement_instruction = """
        You are an expert prompt optimizer. 
        Transform the given naive prompt into a highly detailed, structured, and clear prompt 
        that maximizes response quality from an AI model. 
        Incorporate the following user preferences where appropriate.
        Ensure it includes necessary context, clarifications, and formatting 
        to improve the accuracy of the AI's response.
        """

        # Convert user_choices to text
        # For example, user_choices might contain:
        # {
        #   "Selected Filters": ["Long explanation", "Technical depth"],
        #   "Answers": {
        #       "Preferred format?": "Bullets",
        #       "Target audience?": "High-school students"
        #   }
        # }
        # We'll format that into a readable string to pass to the LLM.
        user_filters_text = ""
        for key, val in user_choices.items():
            user_filters_text += f"\n- **{key}**: {val}"

        full_prompt = (
            f"{refinement_instruction}\n\n"
            f"Naive Prompt: {naive_prompt}\n\n"
            f"User-Selected Preferences:\n{user_filters_text}\n"
        )

        model = load_gemini_pro("gemini-1.5-flash")
        if not model:
            raise Exception("Gemini Pro model not loaded successfully.")

        response = model.generate_content(full_prompt)
        refined_text = response.text.strip()
        logger.info("Prompt refined successfully with Google Generative AI.")
        return refined_text

    except Exception as e:
        logger.error(f"Error refining prompt with Google GenAI: {e}")
        st.error(f"Error refining prompt with Google GenAI: {e}")
        return naive_prompt


# -----------------------------------------------------------------------------
# Step 3: Generate Final Answer from GPT-4o (or any chosen model)
# -----------------------------------------------------------------------------
def generate_response_from_chatgpt(refined_prompt: str) -> str:
    """
    Send the refined prompt to GPT-4o Mini (or any other model) and retrieve the response.
    """
    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant. Provide clear and precise answers."},
        {"role": "user", "content": refined_prompt},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Or any other model name you have access to
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


# -----------------------------------------------------------------------------
# Step 4: Main Streamlit App
# -----------------------------------------------------------------------------
def main():
    st.title("🔬 AI Prompt Refinement 2.0")

    st.markdown("""
       **Goal:** Demonstrate how a well-structured prompt, informed by user filters, 
       can make a normal AI model generate high-quality responses (comparable to more powerful models).
       
       **Steps**:
       1. Enter a naive prompt below.
       2. Generate filter suggestions (e.g. level of detail, format, audience).
       3. Customize these suggestions to refine your prompt.
       4. See the final refined prompt and answer from GPT-4o Mini.
    """)

    # Naive Prompt Input
    naive_prompt = st.text_area("Enter Your Naive Prompt:", "", height=120)

    # -----------------------------------------------------------------------------
    # Generate Filter Options Button
    # -----------------------------------------------------------------------------
    if st.button("Generate Filter Suggestions"):
        if not naive_prompt.strip():
            st.error("Please enter a valid prompt.")
        else:
            with st.spinner("Analyzing your prompt to suggest filters..."):
                filters_data = generate_dynamic_filters(naive_prompt)
                # Store the filter suggestions in session state so we can display them
                st.session_state.filters_data = filters_data
                st.success("Filter suggestions generated successfully!")

    # -----------------------------------------------------------------------------
    # If we have filter suggestions, let the user pick
    # -----------------------------------------------------------------------------
    if "filters_data" in st.session_state:
        filters_data = st.session_state.filters_data

        st.markdown("### Potential Filter Options & Clarifying Questions")
        st.write("Below are suggestions from the LLM on how to refine your query:")

        # Display suggested filters as checkboxes
        selected_filters = []
        if "filters" in filters_data:
            st.subheader("Suggested Filters")
            for filt in filters_data["filters"]:
                # We can create a checkbox for each filter
                checkbox_val = st.checkbox(f"• {filt}", value=False, key=f"filter_{filt}")
                if checkbox_val:
                    selected_filters.append(filt)

        # Display clarifying questions as text inputs
        question_answers = {}
        if "questions" in filters_data:
            st.subheader("Clarifying Questions")
            for q_idx, question in enumerate(filters_data["questions"]):
                ans = st.text_input(f"Q: {question}", key=f"question_{q_idx}")
                question_answers[question] = ans

        # Optionally store user selections in session state
        if st.button("Refine Prompt"):
            # Let's store them in session_state to use later
            user_choices = {
                "Selected Filters": selected_filters,
                "Answers": question_answers
            }
            st.session_state.user_choices = user_choices

            with st.spinner("Refining your prompt using your selected filters..."):
                # Call the refine function
                refined_prompt = refine_prompt_with_google_genai(naive_prompt, user_choices)
                st.session_state.refined_prompt = refined_prompt
                st.success("Prompt refined successfully!")

    # -----------------------------------------------------------------------------
    # Show the refined prompt (if available)
    # -----------------------------------------------------------------------------
    if "refined_prompt" in st.session_state:
        st.markdown("### 📌 Refined Prompt")
        st.text_area("Refined Prompt", st.session_state.refined_prompt, height=120)

        # Button to get the final answer from GPT-4o
        if st.button("Get Answer from GPT-4o Mini"):
            with st.spinner("Generating response from GPT-4o Mini..."):
                gpt_response = generate_response_from_chatgpt(st.session_state.refined_prompt)
            st.markdown("### 💬 GPT-4o Mini Response")
            st.write(gpt_response)


if __name__ == "__main__":
    main()
