"""
Document Analysis Agent implementation.
"""

import json
import re
import time
from typing import Any

from langchain_core.messages import AIMessage
from ...agent import get_agent_executor
from ...core.agent_context import AgentContext
from ...core.agent_result import AgentResult
from ...core.base_agent import BaseAgent
from ...core.exceptions import AgentExecutionException
from .prompt import DOCUMENT_ANALYSIS_SYSTEM_PROMPT
from .schema import DocumentAnalysisResult
from app.utils.logger import get_logger

log = get_logger(__name__)


class DocumentAnalysisAgent(BaseAgent):
    """
    Document Analysis Agent.

    Responsibilities:
    - Detect document type
    - Extract structured information
    - Summarize uploaded documents
    - Return validated structured output

    This agent DOES NOT provide legal advice.
    """

    def __init__(self) -> None:
        super().__init__()

        log.info("=" * 60)
        log.info("Initializing DocumentAnalysisAgent...")

        self._executor = get_agent_executor(
            prompt=DOCUMENT_ANALYSIS_SYSTEM_PROMPT
        )

        log.info("DocumentAnalysisAgent initialized successfully.")
        log.info("=" * 60)

    
    @staticmethod
    def _extract_json(text):
        """
        Extract JSON from Gemini response.
        Supports:
        - string
        - list of content blocks
        - dict
        """

        # Gemini may return a list of content blocks
        if isinstance(text, list):
            combined = ""

            for item in text:
                if isinstance(item, dict):
                    combined += item.get("text", "")
                else:
                    combined += str(item)

            text = combined

        elif isinstance(text, dict):
            text = text.get("text", str(text))

        elif not isinstance(text, str):
            text = str(text)

        text = text.strip()

        # Remove markdown
        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"^```", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise AgentExecutionException(
                "No JSON object found."
            )

        return match.group(0)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> AgentResult:
        """
        Execute Document Analysis Agent.
        """

        if not context.langgraph_messages:
            raise AgentExecutionException(
                "No LangGraph messages found in AgentContext."
            )

        try:
            log.info("=" * 60)
            log.info("Executing DocumentAnalysisAgent...")

            start_time = time.time()

            result = await self._executor.ainvoke(
                {
                    "messages": context.langgraph_messages
                }
            )

            execution_time = round(time.time() - start_time, 2)

            log.info(
                "DocumentAnalysisAgent completed in %.2f seconds.",
                execution_time,
            )

            final_message = result["messages"][-1].content

            print("\n" + "=" * 80)
            print("RAW LLM RESPONSE:")
            print(final_message)
            print("=" * 80 + "\n")

            # -----------------------------
            # Parse structured output
            # -----------------------------
            json_text = self._extract_json(final_message)

            try:
                parsed = json.loads(json_text)
                validated_result = DocumentAnalysisResult.model_validate(parsed)

            except Exception as e:
                raise AgentExecutionException(
                    f"Failed to validate DocumentAnalysisResult: {e}"
                )

            log.info(
                "Structured document analysis validated successfully."
            )

            return AgentResult(
            success=True,
            payload={
             "messages": [
              AIMessage(
                content=(
                    f"Document Type: {validated_result.document_type}\n\n"
                    f"Summary:\n{validated_result.summary}\n\n"
                    f"The document has been successfully analyzed."
                )
            )
        ]
    },
    metadata={
        "agent": "DocumentAnalysisAgent",
        "execution_time": execution_time,
        "raw_response": result,
        "structured_data": validated_result.model_dump(),
    },
)

        except Exception as exc:

            log.exception("DocumentAnalysisAgent failed.")

            return AgentResult(
                success=False,
                payload=None,
                error=exc,
                metadata={
                    "agent": "DocumentAnalysisAgent",
                },
            )