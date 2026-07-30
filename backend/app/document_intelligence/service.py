"""
Document Intelligence Service
"""

from fastapi import UploadFile

from app.ai_agent.core.agent_context import AgentContext
from app.ai_agent.agents.document_intelligence.agent import (
    DocumentIntelligenceAgent,
)


class DocumentIntelligenceService:

    def __init__(self):
        self.agent = DocumentIntelligenceAgent()

    async def analyze_document(
        self,
        uploaded_file: UploadFile,
        user_request: str = "Analyze this document",
    ):
        """
        Analyze an uploaded document.
        """

        raise NotImplementedError