import os
import requests
import dotenv
dotenv.load_dotenv()  # Load variables from .env file if present

API_URL = "https://router.huggingface.co/hf-inference/models/HuggingFaceTB/SmolLM3-3B"
headers = {
    "Authorization": f"Bearer {os.environ['HF_API_TOKEN']}",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

response = query({
    "messages": "\"Can you please let us know more details about your \"",
    "model": "HuggingFaceTB/SmolLM3-3B:hf-inference"
})

print(response)