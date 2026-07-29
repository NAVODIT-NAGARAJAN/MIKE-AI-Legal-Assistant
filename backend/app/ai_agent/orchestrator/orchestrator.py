"""
Orchestrator Agent implementation.
This module contains the primary Orchestrator responsible for coordinating
specialized agents without containing any business logic or legal knowledge itself.
"""
from typing import Any
from ..core.agent_context import AgentContext
from ..core.agent_result import AgentResult
from ..core.registry import AgentRegistry
from .router import OrchestratorRouter
from ..core.exceptions import AgentExecutionException

class Orchestrator:
    """
    The Orchestrator coordinates the execution of various specialized agents.
    It acts as the entry point for all AI requests.
    
    It uses dependency injection for resolving specialized agents via the AgentRegistry,
    ensuring tight coupling is avoided. It does not generate AI responses or contain
    domain knowledge.
    """
    
    def __init__(self, registry: AgentRegistry, router: OrchestratorRouter) -> None:
        """
        Initialize the Orchestrator with required dependencies.
        
        Args:
            registry (AgentRegistry): The registry used to discover and retrieve specialized agents.
            router (OrchestratorRouter): The routing logic used to determine execution flow.
        """
        self._registry = registry
        self._router = router

    async def execute(self, context: AgentContext, **kwargs: Any) -> AgentResult:
        """
        Execute the orchestration workflow.
        
        Args:
            context (AgentContext): The state and context traveling across agents.
            **kwargs: Additional optional orchestration arguments.
            
        Returns:
            AgentResult: The final result of the orchestration workflow.
            
        Raises:
            AgentExecutionException: If no agent is selected by the router.
        """
        # Ask the router which agent should execute
        next_agent_role = await self._router.determine_next_agent(context)
        
        if not next_agent_role:
            raise AgentExecutionException("OrchestratorRouter returned no agent to execute.")
            
        # Request that agent from the registry
        agent = self._registry.get_agent(next_agent_role)
        
        # Invoke the agent's execute() method and return the resulting AgentResult
        return await agent.execute(context, **kwargs)
