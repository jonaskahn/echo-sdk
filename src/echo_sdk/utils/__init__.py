"""Utility functions for Echo plugins."""

from .helpers import check_compatibility, format_plugin_info, get_sdk_version
from .hybrid_discovery import (
    auto_discover_all_plugins,
    get_configured_plugin_directories,
    get_hybrid_discovery_stats,
    is_directory_discovery_enabled,
    reset_hybrid_discovery,
)
from .plugin_discovery import (
    auto_discover_plugins,
    get_plugin_discovery_stats,
    list_installed_plugin_packages,
    reset_discovery_manager,
)
from .validation import validate_plugin_structure, validate_tools

__all__ = [
    # Validation
    "validate_plugin_structure",
    "validate_tools",
    # Helpers
    "get_sdk_version",
    "check_compatibility",
    "format_plugin_info",
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
]
