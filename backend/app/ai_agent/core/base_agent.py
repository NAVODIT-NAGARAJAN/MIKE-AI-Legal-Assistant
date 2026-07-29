from abc import ABC, abstractmethod
from typing import Any
from .agent_context import AgentContext
from .agent_result import AgentResult

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the multi-agent architecture.
    Defines the standard asynchronous interface that every specialized agent must implement.
    """

    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs: Any) -> AgentResult:
        """
        Execute the agent's core logic.
        
        Args:
            context (AgentContext): The generic context travelling between agents.
            **kwargs: Additional optional arguments.

        Returns:
            AgentResult: The standardized result of the agent's execution.
        """
        pass
