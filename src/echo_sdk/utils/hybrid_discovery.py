"""Hybrid plugin discovery supporting both pip-installable and directory-based plugins."""

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

from ..base.loggable import Loggable
from ..registry.plugin_registry import get_plugin_registry
from .plugin_discovery import PluginDiscoveryManager


class HybridPluginDiscovery(Loggable):
    """Hybrid plugin discovery system supporting pip and directory-based plugins."""

    def __init__(self):
        super().__init__()
        self.pip_discovery = PluginDiscoveryManager()
        self._loaded_directories: Set[str] = set()
        self._imported_modules: Set[str] = set()

    def reset(self):
        """Reset the hybrid discovery manager state."""
        self.pip_discovery.reset()
        self._loaded_directories.clear()
        self._imported_modules.clear()

    def discover_all_plugins(self, force_reimport: bool = False) -> Dict[str, Any]:
        """Discover plugins from all enabled sources."""
        results = self._initialize_discovery_results()

        self.logger.info("Starting hybrid plugin discovery...")

        self._discover_pip_plugins(results, force_reimport)
        self._discover_directory_plugins_if_enabled(results, force_reimport)

        results["total_plugins"] = len(get_plugin_registry())
        self.logger.info(f"Hybrid discovery completed: {results['total_plugins']} total plugins")

        return results

    @staticmethod
    def _initialize_discovery_results() -> Dict[str, Any]:
        """Initialize discovery results structure."""
        return {"pip_plugins": 0, "directory_plugins": 0, "total_plugins": 0, "sources": [], "errors": []}

    def _discover_pip_plugins(self, results: Dict[str, Any], force_reimport: bool):
        """Discover pip-installable plugins."""
        try:
            pip_count = self.pip_discovery.discover_pip_plugins(force_reimport)
            results["pip_plugins"] = pip_count
            results["sources"].append("pip")
            self.logger.info(f"Discovered {pip_count} pip-installable plugins")
        except Exception as e:
            error_msg = f"Failed to discover pip plugins: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)

    def _discover_directory_plugins_if_enabled(self, results: Dict[str, Any], force_reimport: bool):
        """Discover directory-based plugins if enabled."""
        if not self._is_directory_discovery_enabled():
            self.logger.debug("Directory-based plugin discovery is disabled")
            return

        try:
            dir_count = self._discover_directory_plugins(force_reimport)
            results["directory_plugins"] = dir_count
            results["sources"].append("directories")
            self.logger.info(f"Discovered {dir_count} directory-based plugins")
        except Exception as e:
            error_msg = f"Failed to discover directory plugins: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)

    @staticmethod
    def _is_directory_discovery_enabled() -> bool:
        """Check if directory-based plugin discovery is enabled."""
        return os.getenv("ECHO_ENABLE_DIRECTORY_PLUGINS", "").lower() in ("true", "1", "yes", "on")

    def _get_plugin_directories(self) -> List[str]:
        """Get list of directories to search for plugins."""
        directories = []

        plugin_dirs_env = os.getenv("ECHO_PLUGIN_DIRS", "")
        if plugin_dirs_env:
            directories.extend(self._parse_plugin_directories(plugin_dirs_env))

        default_dir = os.getenv("ECHO_PLUGIN_DIR", "./plugins")
        if default_dir and os.path.exists(default_dir):
            directories.append(default_dir)

        return self._validate_directories(directories)

    @staticmethod
    def _parse_plugin_directories(plugin_dirs_env: str) -> List[str]:
        """Parse plugin directories from environment variable."""
        separators = [",", ";"]
        dirs = plugin_dirs_env
        for sep in separators:
            if sep in dirs:
                dirs = dirs.replace(sep, ",")
        return [d.strip() for d in dirs.split(",") if d.strip()]

    def _validate_directories(self, directories: List[str]) -> List[str]:
        """Validate and filter plugin directories."""
        validated_dirs = []
        for directory in directories:
            abs_dir = os.path.abspath(directory)
            if os.path.exists(abs_dir) and os.path.isdir(abs_dir):
                validated_dirs.append(abs_dir)
            else:
                self.logger.warning(f"Plugin directory does not exist: {directory}")
        return validated_dirs

    def _discover_directory_plugins(self, force_reimport: bool = False) -> int:
        """Discover plugins from configured directories."""
        directories = self._get_plugin_directories()
        if not directories:
            self.logger.info("No plugin directories configured or found")
            return 0

        self.logger.info(f"Searching for plugins in directories: {directories}")

        discovered_count = 0
        for directory in directories:
            if not force_reimport and directory in self._loaded_directories:
                continue

            try:
                count = self._load_plugins_from_directory(directory)
                discovered_count += count
                self._loaded_directories.add(directory)
                pass
            except Exception as e:
                self.logger.error(f"Failed to load plugins from {directory}: {e}")

        return discovered_count

    def _load_plugins_from_directory(self, directory: str) -> int:
        """Load plugins from a specific directory."""
        directory_path = Path(directory)
        loaded_count = 0

        abs_dir = str(directory_path.absolute())
        if abs_dir not in sys.path:
            sys.path.insert(0, abs_dir)

        for item in directory_path.iterdir():
            if self._is_plugin_module(item):
                try:
                    module_name = item.stem if item.is_file() else item.name

                    if module_name in self._imported_modules:
                        continue

                    if self._import_plugin_module(item, module_name):
                        loaded_count += 1
                        self._imported_modules.add(module_name)
                        pass

                except Exception as e:
                    self.logger.warning(f"Failed to import plugin from {item}: {e}")

        return loaded_count

    def _is_plugin_module(self, path: Path) -> bool:
        """Check if a path represents a plugin module."""
        if path.is_file():
            return path.suffix == ".py" and path.name != "__init__.py" and not path.name.startswith("_")
        elif path.is_dir():
            return (path / "__init__.py").exists() and not path.name.startswith("_") and path.name != "__pycache__"
        return False

    def _import_plugin_module(self, path: Path, module_name: str) -> bool:
        """Import a plugin module and check if it registers plugins."""
        try:
            initial_count = len(get_plugin_registry())

            if path.is_file():
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            else:
                spec = importlib.util.spec_from_file_location(module_name, path / "__init__.py")
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

            final_count = len(get_plugin_registry())
            return final_count > initial_count

        except Exception as e:
            self.logger.warning(f"Failed to import module {module_name} from {path}: {e}")
            return False

    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get comprehensive discovery statistics."""
        pip_stats = self.pip_discovery.get_registry_stats()

        return {
            **pip_stats,
            "directory_discovery_enabled": self._is_directory_discovery_enabled(),
            "configured_directories": self._get_plugin_directories(),
            "loaded_directories": sorted(self._loaded_directories),
            "imported_modules": sorted(self._imported_modules),
            "discovery_sources": self._get_active_sources(),
        }

    def _get_active_sources(self) -> List[str]:
        """Get list of active plugin discovery sources."""
        sources = ["pip"]
        if self._is_directory_discovery_enabled():
            sources.append("directories")
        return sources


_hybrid_discovery = HybridPluginDiscovery()


def auto_discover_all_plugins(force_reimport: bool = False) -> Dict[str, Any]:
    """Automatically discover plugins from all enabled sources."""
    return _hybrid_discovery.discover_all_plugins(force_reimport)


def get_hybrid_discovery_stats() -> Dict[str, Any]:
    """Get comprehensive statistics about hybrid plugin discovery."""
    return _hybrid_discovery.get_discovery_stats()


def is_directory_discovery_enabled() -> bool:
    """Check if directory-based plugin discovery is enabled."""
    return _hybrid_discovery._is_directory_discovery_enabled()


def get_configured_plugin_directories() -> List[str]:
    """Get list of configured plugin directories."""
    return _hybrid_discovery._get_plugin_directories()


def reset_hybrid_discovery():
    """Reset the hybrid discovery manager state."""
    _hybrid_discovery.reset()
