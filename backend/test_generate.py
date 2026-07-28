from google import genai
from app.config.settings import settings

client = genai.Client(api_key=settings.gemini_api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash",   # Change only this line
    contents="Say hello."
)

print(response.text)