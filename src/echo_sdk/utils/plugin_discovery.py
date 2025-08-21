"""Plugin discovery utilities for pip-installable Echo plugins."""

import importlib.metadata
import importlib.util
from typing import List, Set

from ..base.loggable import Loggable
from ..registry.plugin_registry import discover_plugins, get_plugin_registry


class PluginDiscoveryManager(Loggable):
    """Manages discovery and import of pip-installed Echo plugins."""

    def __init__(self):
        super().__init__()
        self._imported_packages: Set[str] = set()

    def reset(self):
        """Reset the discovery manager state."""
        self._imported_packages.clear()

    def discover_pip_plugins(self, force_reimport: bool = False) -> int:
        """Discover and import all pip-installed Echo plugins."""
        self.logger.info("Starting pip plugin discovery...")

        imported_count = 0
        for distribution in importlib.metadata.distributions():
            if not self._is_echo_plugin(distribution):
                continue

            package_name = distribution.metadata["Name"]
            module_name = package_name.replace("-", "_")

            if not force_reimport and module_name in self._imported_packages:
                continue

            if self._try_import_plugin_module(module_name, package_name):
                imported_count += 1

        self.logger.info(f"Imported {imported_count} plugin packages")
        return imported_count

    def _is_echo_plugin(self, distribution: importlib.metadata.Distribution) -> bool:
        """Check if a distribution is an Echo plugin."""
        try:
            project_name = distribution.metadata["Name"].lower()
        except (KeyError, AttributeError):
            return False

        if not self._has_echo_plugin_naming(project_name):
            return False

        if self._is_sdk_package(project_name):
            return False

        return self._depends_on_echo_sdk(distribution)

    @staticmethod
    def _has_echo_plugin_naming(project_name: str) -> bool:
        """Check if project name follows Echo plugin naming convention."""
        return "echo" in project_name and "plugin" in project_name

    @staticmethod
    def _is_sdk_package(project_name: str) -> bool:
        """Check if project is the SDK itself."""
        return project_name in ("echo-sdk", "echo-sdk")

    @staticmethod
    def _depends_on_echo_sdk(distribution: importlib.metadata.Distribution) -> bool:
        """Check if distribution depends on echo-sdk."""
        try:
            # Get requirements from distribution metadata
            requires = distribution.metadata.get_all("Requires-Dist")
            if not requires:
                return False

            requirements = [req.split(";")[0].strip().lower() for req in requires]
            return any("echo-sdk" in req for req in requirements)
        except Exception:
            return False

    def _try_import_plugin_module(self, module_name: str, package_name: str) -> bool:
        """Attempt to import a plugin module."""
        if not self._module_exists(module_name):
            self.logger.warning(f"Plugin package {package_name} not found as module {module_name}")
            return False

        try:
            __import__(module_name)
            self._imported_packages.add(module_name)
            return True
        except ImportError as e:
            self.logger.warning(f"Failed to import plugin {package_name}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error importing {package_name}: {e}")

        return False

    @staticmethod
    def _module_exists(module_name: str) -> bool:
        """Check if a module exists without importing it."""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False

    def get_installed_plugin_packages(self) -> List[str]:
        """Get list of installed Echo plugin package names."""
        return [dist.metadata["Name"] for dist in importlib.metadata.distributions() if self._is_echo_plugin(dist)]

    def get_registry_stats(self) -> dict:
        """Get statistics about the plugin registry."""
        registry = get_plugin_registry()
        plugins = discover_plugins()

        capabilities = self._extract_capabilities(plugins)
        agent_types = self._extract_agent_types(plugins)

        return {
            "total_plugins": len(registry),
            "plugin_names": registry.get_plugin_names(),
            "unique_capabilities": sorted(capabilities),
            "agent_types": sorted(agent_types),
            "installed_packages": self.get_installed_plugin_packages(),
            "imported_packages": sorted(self._imported_packages),
        }

    @staticmethod
    def _extract_capabilities(plugins) -> set:
        """Extract all capabilities from plugins."""
        capabilities = set()
        for plugin in plugins:
            metadata = plugin.get_metadata()
            capabilities.update(metadata.capabilities)
        return capabilities

    @staticmethod
    def _extract_agent_types(plugins) -> set:
        """Extract all agent types from plugins."""
        return {plugin.get_metadata().agent_type for plugin in plugins}


_discovery_manager = PluginDiscoveryManager()


def auto_discover_plugins(force_reimport: bool = False) -> int:
    """Automatically discover and import all pip-installed Echo plugins."""
    return _discovery_manager.discover_pip_plugins(force_reimport)


def reset_discovery_manager():
    """Reset the discovery manager state."""
    _discovery_manager.reset()


def get_plugin_discovery_stats() -> dict:
    """Get statistics about plugin discovery and registry."""
    return _discovery_manager.get_registry_stats()


def list_installed_plugin_packages() -> List[str]:
    """Get list of installed Echo plugin package names."""
    return _discovery_manager.get_installed_plugin_packages()
