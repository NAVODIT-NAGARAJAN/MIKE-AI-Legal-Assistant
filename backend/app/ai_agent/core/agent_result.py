from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .types import AgentRole

@dataclass
class AgentResult:
    """
    Standardized result object returned by every agent upon execution.
    """
    success: bool
    payload: Any
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    next_agent: Optional[AgentRole] = None
    requires_human_review: bool = False
