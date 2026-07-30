"""
Complaint Drafting Agent implementation.

This agent is responsible for drafting consumer complaints, legal notices,
and related documents using the LangGraph implementation.
"""

from typing import Any

from ...agent import get_agent_executor
from ...core.agent_context import AgentContext
from ...core.agent_result import AgentResult
from ...core.base_agent import BaseAgent
from ...core.exceptions import AgentExecutionException
from .prompts import COMPLAINT_DRAFTING_SYSTEM_PROMPT


class ComplaintDraftingAgent(BaseAgent):
    """
    Agent responsible for drafting and modifying consumer complaints.

    This class executes the LangGraph workflow with a prompt tailored
    for drafting and information gathering.
    """

    def __init__(self) -> None:
        super().__init__()
        
        # We use the generic executor with our specific system prompt
        self._executor = get_agent_executor(prompt=COMPLAINT_DRAFTING_SYSTEM_PROMPT)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> AgentResult:
        """
        Execute the LangGraph workflow.

        Args:
            context: Standardized AgentContext.

        Returns:
            AgentResult containing the generated draft or questions.
        """
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
                    "agent": "ComplaintDraftingAgent"
                }
            )

        except Exception as exc:
            return AgentResult(
                success=False,
                payload=None,
                error=exc,
                metadata={
                    "agent": "ComplaintDraftingAgent"
                }
            )
