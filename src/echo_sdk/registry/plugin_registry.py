"""Plugin registry for discovering and managing plugins."""

from typing import Any, Dict, List, Optional, Type

from ..base.loggable import Loggable
from ..base.plugin import BasePlugin
from .contracts import PluginContract


class PluginRegistry(Loggable):
    """Central registry for plugin discovery and management.

    This registry provides the bridge between Echo core system
    and plugins, enabling discovery without direct imports.
    """

    def __init__(self):
        super().__init__()
        self._plugins: Dict[str, PluginContract] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}

    def register(self, plugin_class: Type[BasePlugin]) -> None:
        """Register a plugin class.

        Args:
            plugin_class: Plugin class that implements BasePlugin

        Raises:
            ValueError: If plugin registration fails
        """
        try:
            contract = PluginContract(plugin_class)

            if not contract.is_valid():
                from ..utils.validation import validate_plugin_structure

                errors = validate_plugin_structure(plugin_class)
                raise ValueError(f"Plugin {plugin_class.__name__} failed validation: {errors}")

            metadata = contract.get_metadata()
            plugin_name = metadata.name

            if plugin_name in self._plugins:
                existing_metadata = self._plugins[plugin_name].get_metadata()
                existing_version = existing_metadata.version
                new_version = metadata.version
                self.logger.warning(
                    f"Plugin '{plugin_name}' is already registered "
                    f"(existing: v{existing_version}, new: v{new_version}). "
                    f"Replacing with new version."
                )

            self._plugins[plugin_name] = contract
            self._plugin_classes[plugin_name] = plugin_class

            self.logger.info(f"Registered plugin: {plugin_name} v{metadata.version}")

        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")
            raise ValueError(f"Plugin registration failed: {e}") from e

    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin.

        Args:
            plugin_name: Name of the plugin to unregister

        Returns:
            bool: True if plugin was unregistered, False if not found
        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            del self._plugin_classes[plugin_name]
            self.logger.info(f"Unregistered plugin: {plugin_name}")
            return True
        return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginContract]:
        """Get a plugin contract by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Optional[PluginContract]: Plugin contract if found, None otherwise
        """
        return self._plugins.get(plugin_name)

    def discover_all(self) -> List[PluginContract]:
        """Discover all registered plugins.

        Returns:
            List[PluginContract]: List of all registered plugin contracts
        """
        return list(self._plugins.values())

    def get_plugin_names(self) -> List[str]:
        """Get names of all registered plugins.

        Returns:
            List[str]: List of plugin names
        """
        return list(self._plugins.keys())

    def get_plugins_by_capability(self, capability: str) -> List[PluginContract]:
        """Get plugins that support a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List[PluginContract]: Plugins supporting the capability
        """
        matching_plugins = []
        for contract in self._plugins.values():
            metadata = contract.get_metadata()
            if capability in metadata.capabilities:
                matching_plugins.append(contract)
        return matching_plugins

    def get_plugins_by_type(self, agent_type: str) -> List[PluginContract]:
        """Get plugins by agent type.

        Args:
            agent_type: Type of agent ("specialized", "general", "utility")

        Returns:
            List[PluginContract]: Plugins of the specified type
        """
        matching_plugins = []
        for contract in self._plugins.values():
            metadata = contract.get_metadata()
            if metadata.agent_type == agent_type:
                matching_plugins.append(contract)
        return matching_plugins

    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all registered plugins.

        Returns:
            Dict[str, Dict[str, any]]: Health status for each plugin
        """
        health_results = {}
        for plugin_name, contract in self._plugins.items():
            try:
                status = contract.health_check()
                health_results[plugin_name] = status
            except Exception as e:
                health_results[plugin_name] = {"healthy": False, "error": str(e)}
                self.logger.error(f"Health check failed for plugin {plugin_name}: {e}")
        return health_results

    def clear(self) -> None:
        """Clear all registered plugins."""
        self._plugins.clear()
        self._plugin_classes.clear()
        self.logger.info("Cleared all plugins from registry")

    def __len__(self) -> int:
        """Get number of registered plugins.

        Returns:
            int: Number of registered plugins
        """
        return len(self._plugins)

    def __contains__(self, plugin_name: str) -> bool:
        """Check if a plugin is registered.

        Args:
            plugin_name: Name of the plugin

        Returns:
            bool: True if plugin is registered, False otherwise
        """
        return plugin_name in self._plugins


_global_registry = PluginRegistry()


def register_plugin(plugin_class: Type[BasePlugin]) -> None:
    """Register a plugin with the global registry.

    This is the main entry point for plugins to register themselves.

    Args:
        plugin_class: Plugin class that implements BasePlugin
    """
    _global_registry.register(plugin_class)


def discover_plugins() -> List[PluginContract]:
    """Discover all registered plugins from the global registry.

    This is the main entry point for the Echo core system to
    discover available plugins.

    Returns:
        List[PluginContract]: List of all registered plugin contracts
    """
    return _global_registry.discover_all()


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance.

    Returns:
        PluginRegistry: The global registry instance
    """
    return _global_registry
