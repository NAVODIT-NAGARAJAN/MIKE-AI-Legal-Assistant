"""
Document Intelligence Agent implementation.
"""

import json
import re
import time
from typing import Any

from ...agent import get_agent_executor
from ...core.agent_context import AgentContext
from ...core.agent_result import AgentResult
from ...core.base_agent import BaseAgent
from ...core.exceptions import AgentExecutionException
from .prompt import DOCUMENT_INTELLIGENCE_SYSTEM_PROMPT
from .schema import DocumentIntelligenceResult
from app.utils.logger import get_logger
from langchain_core.messages import AIMessage

log = get_logger(__name__)


class DocumentIntelligenceAgent(BaseAgent):
    """
    Document Intelligence Agent.

    Responsibilities:
    - Receive pre-extracted document text from the caller via AgentContext
    - Invoke Gemini with the document intelligence prompt
    - Validate the JSON response against DocumentIntelligenceResult
    - Return a structured AgentResult

    This agent does NOT perform file I/O, OCR, or parsing.
    Those responsibilities belong to tools/ and services/.

    This agent DOES NOT provide legal advice.
    """

    def __init__(self) -> None:
        super().__init__()

        log.info("=" * 60)
        log.info("Initializing DocumentIntelligenceAgent...")

        self._executor = get_agent_executor(
            prompt=DOCUMENT_INTELLIGENCE_SYSTEM_PROMPT
        )

        log.info("DocumentIntelligenceAgent initialized successfully.")
        log.info("=" * 60)

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Extract the first JSON object from the LLM response text.

        Handles:
        - Raw JSON responses
        - Responses wrapped in ```json ... ``` markdown fences
        - Responses with leading/trailing explanatory text
        """

        text = text.strip()

        # Remove markdown fences
        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"^```", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

        # Extract first JSON object (greedy, handles nested objects)
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise AgentExecutionException(
                "No JSON object found in DocumentIntelligenceAgent response."
            )

        return match.group(0)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> AgentResult:
        """
        Execute the Document Intelligence Agent.

        Validates the context, invokes the LangGraph executor, parses the
        LLM JSON response, and returns a validated DocumentIntelligenceResult
        wrapped in a standardized AgentResult.
        """
        if not context.uploaded_file:
            return AgentResult(
                success=True,
                payload={
                    "messages": [
                        AIMessage(
                            content=(
                                "Please upload your bill, invoice, receipt, warranty card, "
                                "or other document in PDF, DOCX, JPG, JPEG, or PNG format. "
                                "Once uploaded, I'll verify and analyze it."
                            )
                        )
                    ]
                },
                metadata={
                    "agent": "DocumentIntelligenceAgent"
                },
            )

        if not context.langgraph_messages:
            raise AgentExecutionException(
                "No LangGraph messages found in AgentContext."
            )

        # Validate user request
        if not context.user_input or not context.user_input.strip():
            return AgentResult(
                success=False,
                payload=None,
                error="Please tell me what you would like me to do with the document.",
                metadata={
                    "agent": "DocumentIntelligenceAgent"
                },
            )

        # Validate extracted document text
        # if not context.document_text:
        #    return AgentResult(
        #        success=False,
        #        payload=None,
        #        error=(
        #            "No document was found. "
        #            "Please upload a PDF, image, or DOCX file before requesting document analysis."
        #            ),
        #        metadata={
        #            "agent": "DocumentIntelligenceAgent"
        #        },
        #    )

        try:
            log.info("=" * 60)
            log.info("DocumentIntelligenceAgent started.")
            log.info("Conversation ID : %s", context.conversation_id)
            log.info("Messages Count  : %d", len(context.langgraph_messages))

            start_time = time.time()

            result = await self._executor.ainvoke(
                {
                    "messages": context.langgraph_messages
                }
            )

            execution_time = round(time.time() - start_time, 2)

            log.info(
                "LangGraph invocation completed in %.2f seconds.",
                execution_time,
            )

            # ------------------------------------------------------------------
            # Extract and validate structured output
            # ------------------------------------------------------------------
            messages = result.get("messages")

            if not messages:
                raise AgentExecutionException(
                    "No response messages returned by LangGraph."
                )

            final_message = messages[-1].content

            log.info("Raw LLM response length : %d characters.", len(final_message))

            try:
                json_text = self._extract_json(final_message)
            except AgentExecutionException:
                return AgentResult(
                    success=False,
                    payload=None,
                    error=(
                        "The AI did not return a valid structured response. "
                        "Please try again or upload a clearer document."
                    ),
                    metadata={
                        "agent": "DocumentIntelligenceAgent"
                    },
                )

            try:
                parsed = json.loads(json_text)

            except json.JSONDecodeError as exc:
                raise AgentExecutionException(
                    f"LLM returned malformed JSON: {exc}"
                )

            try:
                validated_result = DocumentIntelligenceResult.model_validate(parsed)

            except Exception as exc:
                raise AgentExecutionException(
                    f"Failed to validate DocumentIntelligenceResult schema: {exc}"
                )

            log.info(
                "DocumentIntelligenceResult validated. "
                "Document type: %s | Confidence: %.2f | Risks: %d",
                validated_result.document_type,
                validated_result.confidence_score,
                validated_result.risks.risk_count,
            )
            log.info("=" * 60)

            return AgentResult(
                success=True,
                payload=validated_result,
                metadata={
                    "agent": "DocumentIntelligenceAgent",
                    "execution_time": execution_time,
                    "document_type": validated_result.document_type,
                    "confidence_score": validated_result.confidence_score,
                    "overall_risk_level": validated_result.risks.overall_risk_level,
                    "structured_data": validated_result.model_dump(),
                },
            )

        except AgentExecutionException:
            log.exception("DocumentIntelligenceAgent execution error.")

            return AgentResult(
                success=False,
                payload=None,
                error=None,
                metadata={
                    "agent": "DocumentIntelligenceAgent",
                },
            )

        except Exception as exc:
            import traceback

            traceback.print_exc()

            log.exception("DocumentIntelligenceAgent unexpected failure.")

            raise
