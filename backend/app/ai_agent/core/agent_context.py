from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path

@dataclass
class AgentContext:
    """
    Canonical context object that travels between all agents in the multi-agent architecture.
    It encapsulates the state, identifiers, and history required for execution.
    """
    # The primary input from the user for the current interaction.
    # Populated by: The 'message' or 'initial_message' arguments passed into service.py.
    user_input: str
    
    # Identifiers
    # Populated by: The conversation UUID managed by ConversationRepository in service.py.
    conversation_id: Optional[str] = None
    
    # Populated by: The authenticated user_id passed into service.py methods.
    user_id: Optional[str] = None
    
    # Populated by: The case UUID if this conversation is linked to an existing Case.
    case_id: Optional[str] = None
    
    # History and State
    # Populated by: The serialized conversation history fetched from the database in service.py.
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Populated by: The LangChain message objects (HumanMessage, AIMessage, SystemMessage) 
    # constructed in service.py prior to LangGraph invocation.
    langgraph_messages: List[Any] = field(default_factory=list)
    
    # Shared Data
    # Populated by: Arbitrary request-level data (e.g., timestamps, client IPs, locale).
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Populated by: Agents during execution to pass extracted facts or intermediate 
    # reasoning down the pipeline (e.g., extracted product name, identified legal violations).
    shared_memory: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Document Intelligence Context
    # ------------------------------------------------------------------

    # Uploaded file path (temporary file on server)
    uploaded_file: Optional[Path] = None

    # Original uploaded filename
    uploaded_filename: Optional[str] = None

    # MIME type
    uploaded_mime_type: Optional[str] = None

    # Text extracted from PDF/OCR/DOCX
    document_text: Optional[str] = None

    # Parsed document object (optional)
    parsed_document: Optional[Any] = None
