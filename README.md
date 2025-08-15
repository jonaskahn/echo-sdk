# Echo SDK

A bridge library for developing plugins for the ECHO multi-agent system.

## 🎯 Purpose

- **Clean Interfaces**: Well-defined contracts for plugin development
- **Zero Core Dependencies**: Plugins only depend on the SDK, not the core system
- **Independent Distribution**: Plugins can be distributed as standalone packages
- **Version Management**: SDK versioning with compatibility checks
- **Testing Isolation**: Test plugins without running the core system
- **Auto-Registration**: Automatic plugin discovery through global registry

## 🚀 Quick Start

### Development Setup

You have two options for setting up echo-sdk development:

#### Option 1: Shared Echo-Dev Environment (Recommended)

Use the shared environment that works across all 3 Echo projects:

```bash
# Clone the ECHO project
git clone <repo-url>
cd echo

# Setup shared echo-dev environment (one time)
source ./bin/echo-bin.sh setup

# Daily activation
source ./bin/echo-bin.sh activate

# Now work on echo-sdk
cd echo_sdk
pytest                    # Run tests
pip install -e .          # Install in editable mode
```

#### Option 2: Individual Environment

Set up echo-sdk in its own environment:

```bash
# Clone the ECHO project
git clone <repo-url>
cd echo

# Install SDK in individual environment
cd echo_sdk
poetry install

# Or with pip
pip install -e .
```

### Plugin Development Installation

For plugin developers who want to use the SDK:

```bash
# Install from PyPI (when published)
pip install echo-sdk

# Or install from git repository
pip install git+https://github.com/jonaskahn/echo.git#subdirectory=echo_sdk
```

### Creating a Plugin

1. **Create plugin package structure:**

```
your_plugin_name/
├── __init__.py       # Auto-registration
├── plugin.py         # Plugin metadata and factory
├── agent.py          # Agent implementation
└── tools.py          # Tool functions
```

2. **Define your plugin class (`plugin.py`):**

```python
from echo_sdk import BasePlugin, PluginMetadata, BasePluginAgent


class YourPlugin(BasePlugin):
    @staticmethod
    def get_metadata() -> PluginMetadata:
        return PluginMetadata(
            name="your_plugin_name",
            version="1.0.0",
            description="Your plugin description",
            capabilities=["capability1", "capability2"],
            llm_requirements={
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 1024
            },
            dependencies=["echo-sdk>=1.0.0"],
            sdk_version=">=1.0.0"
        )

    @staticmethod
    def create_agent() -> BasePluginAgent:
        from .agent import YourAgent
        return YourAgent(YourPlugin.get_metadata())
```

3. **Implement your agent (`agent.py`):**

```python
from typing import List
from echo_sdk import BasePluginAgent
from echo_sdk.base.metadata import PluginMetadata


class YourAgent(BasePluginAgent):
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)

    def get_tools(self) -> List:
        from .tools import your_tools
        return your_tools

    def get_system_prompt(self) -> str:
        return "You are YourAgent specialized in..."
```

4. **Define your tools (`tools.py`):**

```python
from echo_sdk import tool


@tool
def your_tool_function(param1: str) -> str:
    """Tool function description."""
    # Implement your tool logic
    return f"Processed: {param1}"


your_tools = [your_tool_function]
```

5. **Register your plugin (`__init__.py`):**

```python
from echo_sdk import register_plugin
from .plugin import YourPlugin

# Auto-register when plugin package is imported
register_plugin(YourPlugin)
```

## 📚 Core Concepts

### Plugin Interface (`BasePlugin`)

Every plugin must implement the `BasePlugin` interface:

- `get_metadata()`: Returns `PluginMetadata` with name, version, capabilities, and LLM requirements
- `create_agent()`: Factory method for creating agent instances
- `validate_dependencies()`: Optional dependency validation
- `get_config_schema()`: Optional configuration schema
- `health_check()`: Optional health check implementation

### Agent Interface (`BasePluginAgent`)

Every agent must implement the `BasePluginAgent` interface:

- `get_tools()`: Returns list of LangChain tools
- `get_system_prompt()`: Returns system prompt for the LLM
- `bind_model()`: Binds tools to an LLM model (inherited)
- `create_agent_node()`: Creates LangGraph node function (inherited)
- `should_continue()`: Decides whether to call tools or return to coordinator (inherited)

### Plugin Registry

The SDK provides a global registry for plugin discovery:

- `register_plugin(plugin_class)`: Register a plugin class with the global registry
- `discover_plugins()`: Discover all registered plugins (used by core system)
- `get_plugin_registry()`: Access the global registry instance

### Plugin Contracts (`PluginContract`)

The bridge between core system and plugins:

- Wraps plugin classes for standardized interaction
- Provides validation and health check interfaces
- Enables communication without direct imports

## 🔧 Advanced Features

### Plugin Validation

The SDK includes comprehensive validation:

```python
from echo_sdk.utils import validate_plugin_structure

errors = validate_plugin_structure(MyPlugin)
if errors:
    print("Plugin validation failed:", errors)
```

### Version Compatibility

Check SDK compatibility:

```python
from echo_sdk.utils import check_compatibility

is_compatible = check_compatibility(">=1.0.0", "1.2.0")
```

### Health Checks

Implement custom health checks:

```python
class MyPlugin(BasePlugin):
    @staticmethod
    def health_check():
        return {
            "healthy": True,
            "details": "All systems operational"
        }
```

## 📦 Package Structure

```
echo_sdk/
├── base/
│   ├── agent.py          # BasePluginAgent interface implementation
│   ├── plugin.py         # BasePlugin interface
│   └── metadata.py       # PluginMetadata, ModelConfig dataclasses
├── tools/
│   ├── decorators.py     # @tool decorator (re-exports LangChain tool)
│   └── registry.py       # Tool registry for managing plugin tools
├── registry/
│   ├── contracts.py      # PluginContract wrapper class
│   └── plugin_registry.py # Global plugin registry and discovery
├── types/
│   ├── state.py          # AgentState TypedDict for state management
│   └── messages.py       # LangChain message type re-exports
├── utils/
│   ├── validation.py     # Plugin structure and tool validation
│   └── helpers.py        # Version compatibility and utility functions
└── examples/
    └── template_plugin/  # Complete plugin template for reference
```

## 🧪 Testing

Test your plugins in isolation using SDK contracts:

```python
import pytest
from echo_sdk import PluginContract, discover_plugins
from echo_sdk.utils import validate_plugin_structure


def test_my_plugin():
    # Test plugin structure
    errors = validate_plugin_structure(MyPlugin)
    assert not errors, f"Plugin validation failed: {errors}"

    # Test plugin contract
    contract = PluginContract(MyPlugin)
    assert contract.is_valid()

    # Test metadata
    metadata = contract.get_metadata()
    assert metadata.name == "my_plugin"
    assert metadata.version

    # Test agent creation
    agent = contract.create_agent()
    tools = agent.get_tools()
    assert len(tools) > 0

    # Test health check
    health = contract.health_check()
    assert health.get("healthy", False)


def test_plugin_discovery():
    # Test that plugin is discoverable via SDK
    plugins = discover_plugins()
    plugin_names = [p.name for p in plugins]
    assert "my_plugin" in plugin_names
```

## 📋 Plugin Template

The SDK includes a complete plugin template at `examples/template_plugin/` with:

- **Proper Project Structure**: Standard plugin package layout
- **Complete Implementation**: All required methods and interfaces
- **Documentation**: Comprehensive docstrings and examples
- **Validation Examples**: Dependency and health check implementations
- **Tool Examples**: Multiple tool types and patterns

Study this template to understand best practices for SDK-based plugin development.

## 🔒 Security Features

The SDK provides security boundaries and validation:

- **Plugin Structure Validation**: Comprehensive validation of plugin interfaces and implementations
- **Dependency Checking**: Validates plugin dependencies and SDK version compatibility
- **Safe Tool Execution**: Tool validation and type checking for safe execution
- **Version Compatibility**: Semantic version checking and compatibility enforcement
- **Health Monitoring**: Plugin health checks and failure detection
- **Contract Isolation**: Clean boundaries between core system and plugins

## 📈 Version Compatibility

The SDK uses semantic versioning and provides compatibility checking:

```python
from echo_sdk.utils import check_compatibility, get_sdk_version

# Check if plugin's SDK requirement is compatible
is_compatible = check_compatibility(">=0.0.1", get_sdk_version())

# Plugin metadata should specify SDK requirements
PluginMetadata(
    name="my_plugin",
    sdk_version=">=0.1.0",  # SDK version requirement
    langchain_version=">=0.1.0",  # LangChain requirement
    # ...
)
```

## 🔗 Related Components

- **[ECHO Core](https://github.com/jonaskahn/echo)**: Core multi-agent orchestration system
- **[ECHO Plugins](https://github.com/jonaskahn/echo-plugins)**: Example plugins and templates using this SDK

### Contribution Process

When contributing to the SDK:

1. **Fork and Branch**: Create a feature branch from main
2. **Setup Environment**: Use shared environment (recommended) or individual setup
3. **Follow Standards**: Use existing code style and patterns
4. **Add Tests**: Include tests for new features or bug fixes
5. **Quality Checks**: Run `pytest`, `black`, `mypy`, etc.
6. **Update Documentation**: Keep README and docstrings current
7. **Test Compatibility**: Ensure existing plugins still work
8. **Submit PR**: Create a pull request with clear description

### Development Commands

```bash
# With shared environment active
pytest              # Run tests
black src/          # Format code
mypy src/           # Type checking
ruff check src/     # Linting

# Test plugin compatibility
pytest examples/template_plugin/
```

## 📄 License

MIT License - see main project LICENSE file for details.
