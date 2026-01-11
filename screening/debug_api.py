"""Debug with actual Layer 1 prompt."""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
from prompts import format_layer1_prompt

api_key = os.environ.get("GEMINI_API_KEY")
print(f"API Key found: {bool(api_key)}")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={
        "temperature": 0.0,
        "top_p": 0.95,
        "max_output_tokens": 2000,
        "response_mime_type": "application/json",
    }
)

# Test with actual screening data
title = "Hypothermic machine perfusion versus cold storage for liver transplantation"
abstract = "Background: Machine perfusion has emerged as an alternative to static cold storage. Methods: We compared outcomes. Results: Machine perfusion showed improved results."

prompt = format_layer1_prompt(title, abstract)
print(f"\n--- Prompt (first 500 chars) ---")
print(prompt[:500])

print(f"\n--- Sending to Gemini ---")
try:
    response = model.generate_content(prompt)
    print(f"Response text:\n{response.text}")
    
    # Try parsing
    import json
    parsed = json.loads(response.text)
    print(f"\nParsed successfully!")
    print(f"Decision: {parsed.get('decision')}")
    print(f"Input tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Output tokens: {response.usage_metadata.candidates_token_count}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
