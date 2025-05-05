import os

from google import genai

gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

