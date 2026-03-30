# Save as check_models.py in your root folder
import google.generativeai as genai
from app.utils.config import config

genai.configure(api_key=config.GEMINI_API_KEY)

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)