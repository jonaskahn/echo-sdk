"""Validation utilities for ECHO plugins."""

import inspect
from langchain_core.tools import BaseTool
from typing import List, Type, Any

from ..base.agent import BasePluginAgent
from ..base.metadata import PluginMetadata
from ..base.plugin import BasePlugin


def validate_plugin_structure(plugin_class: Type[BasePlugin]) -> List[str]:
    """Validate that a plugin class implements the required interface.

    Args:
        plugin_class: Plugin class to validate

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []

    # Check that it's a class
    if not inspect.isclass(plugin_class):
        errors.append("Plugin must be a class")
        return errors

    # Check inheritance
    if not issubclass(plugin_class, BasePlugin):
        errors.append("Plugin must inherit from BasePlugin")

    # Check required methods exist
    if not hasattr(plugin_class, "get_metadata"):
        errors.append("Plugin must implement get_metadata() method")
    elif not callable(getattr(plugin_class, "get_metadata")):
        errors.append("get_metadata must be callable")

    if not hasattr(plugin_class, "create_agent"):
        errors.append("Plugin must implement create_agent() method")
    elif not callable(getattr(plugin_class, "create_agent")):
        errors.append("create_agent must be callable")

    # Validate metadata if possible
    if not errors:
        try:
            metadata = plugin_class.get_metadata()
            if not isinstance(metadata, PluginMetadata):
                errors.append("get_metadata() must return PluginMetadata instance")
            else:
                metadata_errors = validate_metadata(metadata)
                errors.extend(metadata_errors)
        except Exception as e:
            errors.append(f"Error calling get_metadata(): {e}")

    # Validate agent creation if possible
    if not errors:
        try:
            agent = plugin_class.create_agent()
            if not isinstance(agent, BasePluginAgent):
                errors.append("create_agent() must return BasePluginAgent instance")
            else:
                agent_errors = validate_agent(agent)
                errors.extend(agent_errors)
        except Exception as e:
            errors.append(f"Error calling create_agent(): {e}")

    return errors


def validate_metadata(metadata: PluginMetadata) -> List[str]:
    """Validate plugin metadata.

    Args:
        metadata: Plugin metadata to validate

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []

    # Required fields
    if not metadata.name or not metadata.name.strip():
        errors.append("Plugin name cannot be empty")

    if not metadata.version or not metadata.version.strip():
        errors.append("Plugin version cannot be empty")

    if not metadata.description or not metadata.description.strip():
        errors.append("Plugin description cannot be empty")

    if not metadata.capabilities:
        errors.append("Plugin must define at least one capability")

    # Validate agent type
    valid_types = {"specialized", "general", "utility"}
    if metadata.agent_type not in valid_types:
        errors.append(f"Invalid agent_type: {metadata.agent_type}. Must be one of {valid_types}")

    # Validate version format (basic check)
    if metadata.version and not _is_valid_version(metadata.version):
        errors.append(f"Invalid version format: {metadata.version}")

    return errors


def validate_agent(agent: BasePluginAgent) -> List[str]:
    """Validate a plugin agent.

    Args:
        agent: Plugin agent to validate

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []

    # Check required methods
    if not hasattr(agent, "get_tools") or not callable(agent.get_tools):
        errors.append("Agent must implement get_tools() method")

    if not hasattr(agent, "get_system_prompt") or not callable(agent.get_system_prompt):
        errors.append("Agent must implement get_system_prompt() method")

    # Validate tools if possible
    try:
        tools = agent.get_tools()
        tool_errors = validate_tools(tools)
        errors.extend(tool_errors)
    except Exception as e:
        errors.append(f"Error calling get_tools(): {e}")

    # Validate system prompt if possible
    try:
        prompt = agent.get_system_prompt()
        if not isinstance(prompt, str):
            errors.append("get_system_prompt() must return a string")
        elif not prompt.strip():
            errors.append("System prompt cannot be empty")
    except Exception as e:
        errors.append(f"Error calling get_system_prompt(): {e}")

    return errors


def validate_tools(tools: List[Any]) -> List[str]:
    """Validate a list of tools.

    Args:
        tools: List of tools to validate

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(tools, list):
        errors.append("Tools must be provided as a list")
        return errors

    if not tools:
        errors.append("Agent must provide at least one tool")
        return errors

    tool_names = set()
    for i, tool in enumerate(tools):
        # Check if it's a Tool instance (BaseTool covers both Tool and StructuredTool)
        if not isinstance(tool, BaseTool):
            errors.append(f"Tool {i} is not a LangChain Tool instance")
            continue

        # Check tool name
        if not hasattr(tool, "name") or not tool.name:
            errors.append(f"Tool {i} must have a name")
            continue

        # Check for duplicate names
        if tool.name in tool_names:
            errors.append(f"Duplicate tool name: {tool.name}")
        else:
            tool_names.add(tool.name)

        # Check tool description
        if not hasattr(tool, "description") or not tool.description:
            errors.append(f"Tool '{tool.name}' must have a description")

    return errors


def _is_valid_version(version: str) -> bool:
    """Check if version string follows semantic versioning pattern.

    Args:
        version: Version string to validate

    Returns:
        bool: True if version is valid, False otherwise
    """
    import re

    # Basic semantic versioning pattern (major.minor.patch)
    pattern = r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?$"
    return bool(re.match(pattern, version))
