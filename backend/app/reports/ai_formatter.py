"""
LegalEase AI - AI Formatter
==============================
Takes the conversation transcript and uses LLM structured output
to format it into a ReportGenerationDataSchema.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.config.settings import settings
from app.reports.schemas import ReportGenerationDataSchema
from app.utils.logger import get_logger

log = get_logger(__name__)

FORMATTER_PROMPT = """You are a legal summarizer for LegalEase AI.
Your task is to take the transcript of an AI consultation and generate a structured consumer guidance report.
Extract all necessary information from the transcript and map it directly into the required schema.

Transcript:
{transcript}

Rules:
- Be concise but comprehensive.
- Only include rights, steps, and evidence that were actually discussed or implied in the transcript.
- Use simple, empowering language.
- Ensure the steps are ordered logically (1, 2, 3...).
"""

class AIFormatter:
    @staticmethod
    async def format_conversation(messages: list) -> dict:
        """Process conversation messages into a structured dictionary for report generation."""
        log.info("Formatting conversation transcript via AI structured output.")
        
        # Build transcript string
        transcript = ""
        for m in messages:
            role = "Consumer" if m["role"] == "user" else "AI"
            transcript += f"{role}: {m['content']}\n\n"

        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.1,  # Low temp for structured extraction
        )

        # Bind schema
        structured_llm = llm.with_structured_output(ReportGenerationDataSchema)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template(FORMATTER_PROMPT)
        chain = prompt | structured_llm
        
        try:
            result = await chain.ainvoke({"transcript": transcript})
            # Convert Pydantic object back to dict for the repository
            return result.model_dump()
        except Exception as exc:
            log.error(f"Failed to format conversation via AI: {exc}")
            raise RuntimeError(f"Report generation failed: {exc}")
