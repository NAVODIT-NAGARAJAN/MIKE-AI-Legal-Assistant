import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings


async def main():
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
    )

    print("Sending request...")

    response = await llm.ainvoke("What are consumer rights in India?")

    print("Response:")
    print(response.content)


asyncio.run(main())