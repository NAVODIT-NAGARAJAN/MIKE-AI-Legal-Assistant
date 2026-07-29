from typing import Dict

from .base_agent import BaseAgent
from .exceptions import AgentException
from .types import AgentRole


class AgentRegistry:

    def __init__(self) -> None:

        self._agents: Dict[AgentRole, BaseAgent] = {}

        from ..agents.case_analysis.agent import CaseAnalysisAgent

        self.register_agent(
            AgentRole.CASE_ANALYSIS,
            CaseAnalysisAgent(),
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