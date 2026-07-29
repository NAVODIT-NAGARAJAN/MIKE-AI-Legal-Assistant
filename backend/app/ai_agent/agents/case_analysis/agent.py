"""
Case Analysis Agent implementation.

This agent acts as a thin adapter around the existing LangGraph implementation.
It exposes the standardized BaseAgent interface without changing the existing
application behaviour.
"""

from typing import Any

from ...agent import get_agent_executor
from ...core.agent_context import AgentContext
from ...core.agent_result import AgentResult
from ...core.base_agent import BaseAgent
from ...core.exceptions import AgentExecutionException
# pyrefly: ignore [missing-import]
from .prompts import CASE_ANALYSIS_SYSTEM_PROMPT

class CaseAnalysisAgent(BaseAgent):
    """
    Adapter around the existing LangGraph implementation.

    This class does NOT contain prompts, tools, business logic,
    database access, or conversation management.

    Its only responsibility is to execute the existing LangGraph
    workflow and return a standardized AgentResult.
    """

    def __init__(self) -> None:
        super().__init__()

        # Reuse the existing LangGraph executor.
        # No new LLM, prompts, or tools are created.
        self._executor = get_agent_executor(prompt=CASE_ANALYSIS_SYSTEM_PROMPT)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> AgentResult:
        """
        Execute the existing LangGraph workflow.

        Args:
            context: Standardized AgentContext.

        Returns:
            AgentResult containing the raw LangGraph response.
        """

        # Validate the context before invoking LangGraph.
        if not context.langgraph_messages:
            raise AgentExecutionException(
                "No LangGraph messages found in AgentContext."
            )

        try:
            result = await self._executor.ainvoke(
                {
                    "messages": context.langgraph_messages
                }
            )

            return AgentResult(
                success=True,
                payload=result,
                metadata={
                    "agent": "CaseAnalysisAgent"
                }
            )

        except Exception as exc:
            return AgentResult(
                success=False,
                payload=None,
                error=exc,
                metadata={
                    "agent": "CaseAnalysisAgent"
                }
            )