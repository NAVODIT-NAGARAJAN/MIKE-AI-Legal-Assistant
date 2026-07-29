"""
Custom exceptions for the multi-agent architecture.
"""

class AgentException(Exception):
    """
    Base exception for all agent-related errors.
    """
    pass


class AgentExecutionException(AgentException):
    """
    Exception raised when an agent fails during execution.
    """
    pass


class AgentValidationException(AgentException):
    """
    Exception raised when input validation fails for an agent.
    """
    pass
