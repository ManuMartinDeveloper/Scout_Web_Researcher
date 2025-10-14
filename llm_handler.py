# file: llm_handler.py (or wherever your code is)
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError
import os
import dotenv
dotenv.load_dotenv()  # Load variables from .env file if present

# --- Model configured for CONVERSATIONAL task ---
MODEL_URL = "meta-llama/Meta-Llama-3-8B-Instruct" # Or any other conversational model

try:
    client = InferenceClient(api_key=os.environ['HF_API_TOKEN'])
except Exception as e:
    client = None

def get_llm_answer(query: str, context_chunks: list[str]) -> str:
    if client is None:
        return "### 🚨 Error\n**Could not initialize the Hugging Face Inference Client.**"

    context = "\n---\n".join(context_chunks)

    # --- THE FIX: Format input as a list of messages ---
    messages = [
        {
            "role": "system",
            "content": "You are an expert business analyst. Answer the user's question based *only* on the provided text context. If the context does not contain the answer, state that the information is not available."
        },
        {
            "role": "user",
            "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"
        }
    ]

    try:
        # --- THE FIX: Call the chat_completion method ---
        response = client.chat_completion(
            model=MODEL_URL,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        
        # The response structure is slightly different for chat
        return response.choices[0].message.content.strip()

    except HfHubHTTPError as e:
        return f"API Error: Could not connect to the model. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"