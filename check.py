from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  # Load from .env file

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

for m in genai.list_models():
    print(m.name)
