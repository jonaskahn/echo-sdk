"""Base agent interface for ECHO plugin agents."""

from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import Tool
from typing import List, Dict, Any

from .metadata import PluginMetadata


class BasePluginAgent(ABC):
    """Base class for plugin agents used as LangGraph nodes.

    This replaces the direct dependency on echo.plugins.base.BasePluginAgent
    and provides the same interface through the SDK.

    Plugin agents are the core units of work in ECHO. Each agent:
    1. Provides tools for specific domain functionality
    2. Defines a system prompt for LLM behavior
    3. Can be bound to an LLM model with tools attached
    4. Creates a LangGraph node function for orchestration
    """

    def __init__(self, metadata: PluginMetadata):
        """Initialize the plugin agent.

        Args:
            metadata: Plugin metadata containing configuration
        """
        self.metadata = metadata
        self._tools = None
        self._bound_model = None
        self._initialized = False

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """Return the tools that this agent exposes.

        Tools are LangChain Tool instances that define the specific
        functionality this agent can perform (e.g., math operations,
        web search, database queries).

        Returns:
            List[Tool]: Tools to be bound to the LLM
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt used by this agent.

        The system prompt defines the agent's behavior, role, and
        instructions for using its tools effectively.

        Returns:
            str: System prompt for the LLM
        """
        pass

    def bind_model(self, model: BaseChatModel) -> BaseChatModel:
        """Bind the agent's tools to the provided chat model.

        This method is called by the ECHO core system to create
        a specialized model for this agent with its tools attached.

        Args:
            model: Base chat model to be specialized

        Returns:
            BaseChatModel: Tool-bound chat model
        """
        tools = self.get_tools()
        self._bound_model = model.bind_tools(tools)
        return self._bound_model

    def should_continue(self, state: Dict[str, Any]) -> str:
        """Decide whether to call tools or return to the coordinator.

        This method implements the standard ECHO pattern for agent
        decision making in the LangGraph workflow.

        Args:
            state: Current graph state (expects a 'messages' list)

        Returns:
            str: "continue" to call tools, "back" to return to coordinator
        """
        last_msg = state.get("messages", [])[-1] if state.get("messages") else None
        if not last_msg:
            return "back"

        tool_calls = getattr(last_msg, "tool_calls", None)
        return "continue" if tool_calls else "back"

    def create_agent_node(self):
        """Create the callable used as this plugin's agent node.

        This method creates a LangGraph node function that:
        1. Applies the agent's system prompt
        2. Invokes the bound model
        3. Returns appropriate state updates

        Returns:
            callable: Function with signature fn(state: Dict[str, Any]) -> Dict[str, Any]
        """

        def agent_node(state):
            """Agent node function for LangGraph integration."""
            try:
                if not hasattr(self, "_bound_model") or self._bound_model is None:
                    raise RuntimeError(f"No bound model for agent {self.metadata.name}")

                system = SystemMessage(content=self.get_system_prompt())
                response = self._bound_model.invoke([system] + state["messages"])

                agents_used = state.get("agents_used", [])
                if self.metadata.name not in agents_used:
                    agents_used = agents_used + [self.metadata.name]

                plugin_context = state.get("plugin_context", {})
                plugin_context["last_plugin"] = self.metadata.name
                if "routing_history" not in plugin_context:
                    plugin_context["routing_history"] = []
                plugin_context["routing_history"] = plugin_context["routing_history"] + [self.metadata.name]

                return {
                    "messages": [response],
                    "hops": state.get("hops", 0) + 1,
                    "current_agent": self.metadata.name,
                    "agents_used": agents_used,
                    "plugin_context": plugin_context,
                }
            except Exception as e:
                raise RuntimeError(f"Error in agent node for {self.metadata.name}: {e}") from e

        return agent_node

    def initialize(self) -> None:
        """Initialize agent resources (e.g., cache tools).

        Override this method to perform any setup required by your agent,
        such as loading models, connecting to databases, etc.
        """
        self._tools = self.get_tools()
        self._initialized = True

    def cleanup(self) -> None:
        """Cleanup agent resources.

        Override this method to clean up resources when the agent
        is being shut down or reloaded.
        """
        pass
