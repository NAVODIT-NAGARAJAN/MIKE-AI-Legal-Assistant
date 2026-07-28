"""
LegalEase AI - AI Agent Orchestration
========================================
Defines the LangGraph workflow and the tool-calling AI agent.
"""

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from app.ai_agent.prompts import SYSTEM_PROMPT
from app.config.settings import settings
from app.knowledge.service import KnowledgeBaseService
from app.utils.logger import get_logger

log = get_logger(__name__)


@tool
def search_legal_knowledge(query: str) -> str:
    """
    Search the official Indian Consumer Rights knowledge base.
    Always use this tool to retrieve relevant legal provisions,
    rules, and guidance.
    """

    log.info("Knowledge Search Tool Called")
    log.info(f"Query: {query}")

    try:
        svc = KnowledgeBaseService()
        results = svc.retrieve(query, top_k=5)

        if not results:
            log.info("No knowledge base results found.")
            return "No relevant legal information found in the knowledge base."

        context = []

        for result in results:
            context.append(
                f"[Source: {result.source_file}]\n{result.text}"
            )

        log.info(f"Retrieved {len(results)} knowledge chunks.")

        return "\n\n----------------------\n\n".join(context)

    except Exception as exc:
        log.exception("Knowledge Base Search Failed")
        return f"Error retrieving knowledge: {str(exc)}"


def get_agent_executor():
    """
    Initialize and return the LangGraph ReAct agent.
    """

    log.info("=" * 60)
    log.info(f"Using Gemini Model : {settings.gemini_model}")
    log.info(f"API Key Loaded     : {bool(settings.gemini_api_key)}")
    log.info(f"Temperature        : {settings.gemini_temperature}")
    log.info("=" * 60)

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=settings.gemini_temperature,
    )

    tools = []

    log.info("Creating LangGraph ReAct Agent...")

    agent_executor = create_react_agent(
        model=llm,
        tools=[],
        prompt=SYSTEM_PROMPT,
    )

    log.info("LangGraph Agent Created Successfully.")

    return agent_executor