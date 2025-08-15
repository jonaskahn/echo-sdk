"""Base interfaces and types for ECHO plugins."""

from .agent import BasePluginAgent
from .metadata import PluginMetadata, ModelConfig
from .plugin import BasePlugin

__all__ = ["BasePluginAgent", "PluginMetadata", "ModelConfig", "BasePlugin"]
