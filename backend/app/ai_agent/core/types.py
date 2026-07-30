"""
Reusable type aliases and enumerations for the multi-agent architecture.
"""
from typing import Dict, Any, List
from enum import Enum

# Example type alias for a standard agent payload
AgentPayload = Dict[str, Any]

# Type alias for conversation history messages
MessageList = List[Dict[str, str]]

class AgentRole(str, Enum):
    """
    Enumeration of common agent roles.
    """
    ORCHESTRATOR = "orchestrator"
    CASE_ANALYSIS = "case_analysis"
    LEGAL_RESEARCH = "legal_research"
    DOCUMENT_INTELLIGENCE = "document_intelligence"
    LEGAL_DRAFTING = "legal_drafting"
    COMPLAINT_DRAFTING = "complaint_drafting"
    LEGAL_ADVISOR = "legal_advisor"
    WEB_SEARCH = "web_search"
    VERIFICATION = "verification"
    DOCUMENT_ANALYSIS = "document_analysis"
