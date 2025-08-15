"""Plugin registry and discovery system."""

from .contracts import PluginContract
from .plugin_registry import PluginRegistry, register_plugin, discover_plugins

__all__ = ["PluginContract", "PluginRegistry", "register_plugin", "discover_plugins"]
