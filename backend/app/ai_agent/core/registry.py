from typing import Dict

from .base_agent import BaseAgent
from .exceptions import AgentException
from .types import AgentRole


class AgentRegistry:

    def __init__(self) -> None:

        self._agents: Dict[AgentRole, BaseAgent] = {}

        from ..agents.case_analysis.agent import CaseAnalysisAgent
        from ..agents.legal_research.agent import LegalResearchAgent
        from ..agents.complaint_drafting.agent import ComplaintDraftingAgent
        from ..agents.document_analysis.agent import DocumentAnalysisAgent
        from ..agents.document_intelligence.agent import DocumentIntelligenceAgent

        self.register_agent(
            AgentRole.CASE_ANALYSIS,
            CaseAnalysisAgent(),
        )

        self.register_agent(
            AgentRole.LEGAL_RESEARCH,
            LegalResearchAgent(),
        )

        self.register_agent(
            AgentRole.COMPLAINT_DRAFTING,
            ComplaintDraftingAgent(),
        )
        self.register_agent(
            AgentRole.DOCUMENT_ANALYSIS,
            DocumentAnalysisAgent(),
        )
        self.register_agent(
            AgentRole.DOCUMENT_INTELLIGENCE,
            DocumentIntelligenceAgent(),
        )

    def register_agent(
        self,
        role: AgentRole,
        agent: BaseAgent,
    ) -> None:

        self._agents[role] = agent

    def get_agent(
        self,
        role: AgentRole,
    ) -> BaseAgent:

        agent = self._agents.get(role)

        if agent is None:
            raise AgentException(
                f"Agent '{role}' is not registered."
            )

        return agent