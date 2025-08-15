"""ECHO Plugin SDK - Bridge library for ECHO multi-agent system plugins.

This SDK provides the interface between ECHO core system and plugins,
enabling true decoupling and independent plugin bin.

Example usage:
    >>> from echo_sdk import BasePlugin, PluginMetadata, tool
    >>>
    >>> class MyPlugin(BasePlugin):
    ...     @staticmethod
    ...     def get_metadata() -> PluginMetadata:
    ...         return PluginMetadata(name="my_plugin", version="1.0.0")
    ...
    ...     @staticmethod
    ...     def create_agent():
    ...         return MyAgent()
"""

from .base.agent import BasePluginAgent
from .base.metadata import PluginMetadata, ModelConfig
from .base.plugin import BasePlugin
from .registry.contracts import PluginContract
from .registry.plugin_registry import (
    register_plugin,
    discover_plugins,
    get_plugin_registry,
)
from .tools.decorators import tool
from .types.state import AgentState

__version__ = "1.0.0"
__all__ = [
    # Core interfaces
    "BasePlugin",
    "BasePluginAgent",
    "PluginMetadata",
    "ModelConfig",
    # Tools
    "tool",
    # Registry
    "PluginContract",
    "register_plugin",
    "discover_plugins",
    "get_plugin_registry",
    # Types
    "AgentState",
]
