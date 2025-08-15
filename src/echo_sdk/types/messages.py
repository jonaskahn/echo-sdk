"""Message types for ECHO plugins."""

# Re-export LangChain message types for convenience
# This allows plugins to import message types from the SDK
# instead of directly from langchain_core
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    ChatMessage,
)

MessageTypes = {
    "BaseMessage": BaseMessage,
    "HumanMessage": HumanMessage,
    "AIMessage": AIMessage,
    "SystemMessage": SystemMessage,
    "ToolMessage": ToolMessage,
    "ChatMessage": ChatMessage,
}

__all__ = [
    "BaseMessage",
    "HumanMessage",
    "AIMessage",
    "SystemMessage",
    "ToolMessage",
    "ChatMessage",
    "MessageTypes",
]
