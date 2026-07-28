from app.config.settings import settings
from google import genai

client = genai.Client(api_key=settings.gemini_api_key)

print("Connected successfully!")
print("Available models:\n")

for model in client.models.list():
    print(model.name)