"""Template plugin for ECHO multi-agent system.

This template demonstrates how to create a ECHO plugin using the SDK.
Auto-registers the plugin when imported.
"""

from echo_sdk import register_plugin

from .plugin import TemplatePlugin

# Auto-register when plugin package is imported
register_plugin(TemplatePlugin)
