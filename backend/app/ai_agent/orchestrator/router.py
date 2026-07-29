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

        # Common Questions
        "explain",
        "what is",
        "rights",
        "law",
        "act",
        "section",
        "rule",
        "procedure"
    ]

    # ---------------------------------------------------------
    # Keywords for Case Analysis
    # ---------------------------------------------------------
    CASE_ANALYSIS_KEYWORDS = [
        "draft complaint",
        "draft a complaint",
        "generate complaint",
        "complaint generation",
        "write complaint",
        "create complaint",
        "modify complaint",
        "edit complaint",
        "complaint modification",
        "complaint analysis",
        "analyze complaint",
        "analyse complaint",
        "review complaint",
        "legal notice",
        "generate legal notice",
        "document analysis",
        "analyze document",
        "analyse document",
        "uploaded complaint",
        "uploaded document",
        "ocr",
        "pdf",
        "case preparation"
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
        the current request.

        Args:
            context: Current conversation context.

        Returns:
            AgentRole representing the selected agent.
        """

        user_input = context.user_input.lower().strip()

        # -----------------------------------------------------
        # Case Analysis has higher priority
        # -----------------------------------------------------
        # Example:
        # "Draft a complaint explaining consumer rights"
        # should go to CaseAnalysisAgent.
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
        # Default fallback
        # -----------------------------------------------------
        return AgentRole.CASE_ANALYSIS