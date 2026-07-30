"""
Legal Research Agent implementation.
"""

from typing import Any
import time
from pprint import pformat

from ...agent import get_agent_executor
from ...core.agent_context import AgentContext
from ...core.agent_result import AgentResult
from ...core.base_agent import BaseAgent
from ...core.exceptions import AgentExecutionException
from .prompts import LEGAL_RESEARCH_SYSTEM_PROMPT
from app.utils.logger import get_logger

log = get_logger(__name__)


class LegalResearchAgent(BaseAgent):
    """
    Adapter around the existing LangGraph implementation.
    """

    def __init__(self) -> None:
        super().__init__()

        log.info("=" * 60)
        log.info("Initializing LegalResearchAgent...")

        self._executor = get_agent_executor(
            prompt=LEGAL_RESEARCH_SYSTEM_PROMPT
        )

        log.info("LegalResearchAgent initialized successfully.")
        log.info("=" * 60)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> AgentResult:

        if not context.langgraph_messages:
            raise AgentExecutionException(
                "No LangGraph messages found in AgentContext."
            )

        try:
            log.info("=" * 60)
            log.info("LegalResearchAgent Started")
            log.info(f"Messages Count : {len(context.langgraph_messages)}")

            # -------------------------------------------------
            # DEBUG SECTION
            # -------------------------------------------------
            log.info("=" * 60)
            log.info("LangGraph Messages Debug")
            log.info(f"Type : {type(context.langgraph_messages)}")

            for index, msg in enumerate(context.langgraph_messages):
                log.info("-" * 60)
                log.info(f"Message #{index + 1}")
                log.info(f"Class : {msg.__class__.__name__}")
                log.info(f"Object:\n{pformat(msg)}")

                if hasattr(msg, "content"):
                    log.info(f"Content : {msg.content}")

                if hasattr(msg, "type"):
                    log.info(f"Type : {msg.type}")

            log.info("=" * 60)
            log.info("Before LangGraph ainvoke()")
            # -------------------------------------------------

            start_time = time.time()

            result = await self._executor.ainvoke(
                {
                    "messages": context.langgraph_messages
                    
                }
            )

            elapsed = time.time() - start_time

            log.info("=" * 60)
            log.info("After LangGraph ainvoke()")
            log.info(f"Execution Time : {elapsed:.2f} seconds")

            log.info("Result Type : %s", type(result))
            log.info("Result : %s", pformat(result))
            log.info("=" * 60)

            return AgentResult(
                success=True,
                payload=result,
                metadata={
                    "agent": "LegalResearchAgent",
                    "execution_time": elapsed,
                },
            )

        except Exception as exc:
            log.exception("LegalResearchAgent failed")

            return AgentResult(
                success=False,
                payload=None,
                error=exc,
                metadata={
                    "agent": "LegalResearchAgent",
                },
            )