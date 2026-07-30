"""
Routing logic for the Orchestrator.

This module is responsible for selecting the most appropriate
specialized agent based on the user's request.
"""

from typing import Optional

from ..core.agent_context import AgentContext
from ..core.types import AgentRole


class OrchestratorRouter:
    """
    Determines the next specialized agent that should handle
    the current user request.
    """

    # ---------------------------------------------------------
    # Keywords for Complaint Drafting
    # Highest Priority
    # ---------------------------------------------------------
    COMPLAINT_DRAFTING_KEYWORDS = [
        "draft complaint",
        "draft a complaint",
        "generate complaint",
        "create complaint",
        "write complaint",
        "prepare complaint",
        "prepare a complaint",
        "complaint letter",
        "consumer complaint",
        "modify complaint",
        "edit complaint",
        "rewrite complaint",
        "redraft complaint",
        "legal notice",
        "generate legal notice",
    ]

    # ---------------------------------------------------------
    # Keywords for Document Analysis
    # ---------------------------------------------------------
    DOCUMENT_ANALYSIS_KEYWORDS = [
        "document analysis",
        "analyze document",
        "analyse document",
        "analyze receipt",
        "analyse receipt",
        "receipt",
        "invoice",
        "bill",
        "purchase bill",
        "purchase receipt",
        "warranty card",
        "order confirmation",
        "product invoice",
        "upload receipt",
        "upload invoice",
        "uploaded receipt",
        "uploaded invoice",
        "uploaded document",
        "extract document",
        "extract information",
        "document summary",
        "summarize document",
    ]

    # ---------------------------------------------------------
    # Keywords for Case Analysis
    # ---------------------------------------------------------
    CASE_ANALYSIS_KEYWORDS = [
        "complaint analysis",
        "analyze complaint",
        "analyse complaint",
        "analyze my complaint",
        "analyse my complaint",
        "review complaint",
        "review my complaint",
        "ocr",
        "pdf",
        "case preparation",
    ]

    # ---------------------------------------------------------
    # Keywords for Legal Research
    # ---------------------------------------------------------
    LEGAL_RESEARCH_KEYWORDS = [
        # Consumer Rights
        "consumer right",
        "consumer rights",
        "consumer protection",
        "consumer protection act",
        "consumer protection act 2019",
        "consumer law",

        # Legal Information
        "legal section",
        "legal sections",
        "legal provision",
        "legal provisions",
        "legal concept",
        "legal concepts",
        "legal guidance",
        "legal advice",
        "legal terminology",

        # Procedures
        "jurisdiction",
        "limitation",
        "limitation period",
        "appeal",
        "appeal process",
        "mediation",
        "filing",
        "filing procedure",
        "consumer commission",
        "district commission",
        "state commission",
        "national commission",

        # Compensation
        "compensation",
        "refund",
        "replacement",
        "warranty",
        "guarantee",

        # Consumer Disputes
        "deficiency of service",
        "unfair trade practice",
        "product liability",

        # General Legal Questions
        "explain",
        "what is",
        "rights",
        "law",
        "act",
        "section",
        "rule",
        "procedure",
    ]

    def __init__(self) -> None:
        """Initialize the router."""
        pass

    async def determine_next_agent(
        self,
        context: AgentContext,
    ) -> Optional[AgentRole]:
        """
        Determine which specialized agent should process
        the current user request.

        Args:
            context: Current conversation context.

        Returns:
            AgentRole representing the selected agent.
        """

        user_input = context.user_input.lower().strip()

        # -----------------------------------------------------
        # Complaint Drafting
        # -----------------------------------------------------
        for keyword in self.COMPLAINT_DRAFTING_KEYWORDS:
            if keyword in user_input:
                return AgentRole.COMPLAINT_DRAFTING

        # -----------------------------------------------------
        # Document Intelligence (Upload Requests)
        # -----------------------------------------------------
        if (
            "upload" in user_input
            or "shall i upload" in user_input
            or "should i upload" in user_input
            or "can i upload" in user_input
        ):
            return AgentRole.DOCUMENT_INTELLIGENCE
        
        # -----------------------------------------------------
        # Document Analysis
        # -----------------------------------------------------
        for keyword in self.DOCUMENT_ANALYSIS_KEYWORDS:
            if keyword in user_input:
                return AgentRole.DOCUMENT_ANALYSIS

        # -----------------------------------------------------
        # Case Analysis
        # -----------------------------------------------------
        for keyword in self.CASE_ANALYSIS_KEYWORDS:
            if keyword in user_input:
                return AgentRole.CASE_ANALYSIS

        # -----------------------------------------------------
        # Legal Research
        # -----------------------------------------------------
        for keyword in self.LEGAL_RESEARCH_KEYWORDS:
            if keyword in user_input:
                return AgentRole.LEGAL_RESEARCH

        # -----------------------------------------------------
        # Default Agent
        # -----------------------------------------------------
        return AgentRole.CASE_ANALYSIS