"""Echo Plugin SDK - Bridge library for Echo multi-agent system plugins.

This SDK provides the interface between Echo core system and plugins,
enabling true decoupling and independent plugin bin.

Example usage:
    >>> from echo_sdk import BasePlugin, PluginMetadata, tool
    >>>
    >>> class MyPlugin(BasePlugin):
    ...     @staticmethod
    ...     def get_metadata() -> PluginMetadata:
    ...         return PluginMetadata(name="my_plugin", version="0.1.0")
    ...
    ...     @staticmethod
    ...     def create_agent():
    ...         return MyAgent()
"""

from .base.agent import BasePluginAgent
from .base.metadata import ModelConfig, PluginMetadata
from .base.plugin import BasePlugin
from .registry.contracts import PluginContract
from .registry.plugin_registry import (
    discover_plugins,
    get_plugin_registry,
    register_plugin,
)
from .tools.decorators import tool
from .types.state import AgentState
from .utils.hybrid_discovery import (
    auto_discover_all_plugins,
    get_configured_plugin_directories,
    get_hybrid_discovery_stats,
    is_directory_discovery_enabled,
    reset_hybrid_discovery,
)
from .utils.plugin_discovery import (
    auto_discover_plugins,
    get_plugin_discovery_stats,
    list_installed_plugin_packages,
    reset_discovery_manager,
)

__version__ = "0.1.0"
__all__ = [
    # Core interfaces
    "BasePlugin",
    "BasePluginAgent",
    "PluginMetadata",
    "ModelConfig",
    # Tools
    "tool",
    # Registry
    PluginContract,
    "register_plugin",
    "discover_plugins",
    "get_plugin_registry",
    # Plugin Discovery
    "auto_discover_plugins",
    "get_plugin_discovery_stats",
    "list_installed_plugin_packages",
    "reset_discovery_manager",
    # Hybrid Discovery
    "auto_discover_all_plugins",
    "get_hybrid_discovery_stats",
    "is_directory_discovery_enabled",
    "get_configured_plugin_directories",
    "reset_hybrid_discovery",
    # Types
    "AgentState",
]
