"""Helper utilities for ECHO plugins."""

import re
from typing import Dict, Any

from .. import __version__


def get_sdk_version() -> str:
    """Get the current SDK version.

    Returns:
        str: SDK version string
    """
    return __version__


def check_compatibility(plugin_sdk_version: str, current_sdk_version: str = None) -> bool:
    """Check if a plugin's SDK version requirement is compatible with current SDK.

    Args:
        plugin_sdk_version: Plugin's SDK version requirement (e.g., ">=1.0.0")
        current_sdk_version: Current SDK version (defaults to actual version)

    Returns:
        bool: True if compatible, False otherwise
    """
    if current_sdk_version is None:
        current_sdk_version = get_sdk_version()

    try:
        return _check_version_constraint(plugin_sdk_version, current_sdk_version)
    except Exception:
        # If we can't parse the version constraint, assume incompatible
        return False


def _check_version_constraint(constraint: str, version: str) -> bool:
    """Check if a version satisfies a constraint.

    Args:
        constraint: Version constraint (e.g., ">=1.0.0", "~1.2.0", "1.0.0")
        version: Version to check

    Returns:
        bool: True if version satisfies constraint, False otherwise
    """
    # Parse constraint
    constraint = constraint.strip()

    # Exact match
    if constraint == version:
        return True

    # Greater than or equal
    if constraint.startswith(">="):
        required_version = constraint[2:].strip()
        return _compare_versions(version, required_version) >= 0

    # Greater than
    if constraint.startswith(">"):
        required_version = constraint[1:].strip()
        return _compare_versions(version, required_version) > 0

    # Less than or equal
    if constraint.startswith("<="):
        required_version = constraint[2:].strip()
        return _compare_versions(version, required_version) <= 0

    # Less than
    if constraint.startswith("<"):
        required_version = constraint[1:].strip()
        return _compare_versions(version, required_version) < 0

    # Compatible release (tilde)
    if constraint.startswith("~"):
        required_version = constraint[1:].strip()
        return _is_compatible_release(version, required_version)

    # Default to exact match
    return constraint == version


def _compare_versions(version1: str, version2: str) -> int:
    """Compare two version strings.

    Args:
        version1: First version
        version2: Second version

    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """

    def normalize_version(version_string):
        """Convert version string to comparable tuple."""
        parts = re.split(r"[-.]", version_string)
        normalized = []
        for part in parts:
            if part.isdigit():
                normalized.append(int(part))
            else:
                normalized.append(part)
        return normalized

    version1_parts = normalize_version(version1)
    version2_parts = normalize_version(version2)

    # Pad shorter version with zeros
    max_length = max(len(version1_parts), len(version2_parts))
    version1_parts += [0] * (max_length - len(version1_parts))
    version2_parts += [0] * (max_length - len(version2_parts))

    for part1, part2 in zip(version1_parts, version2_parts):
        if isinstance(part1, int) and isinstance(part2, int):
            if part1 < part2:
                return -1
            elif part1 > part2:
                return 1
        else:
            # String comparison for pre-release identifiers
            str1, str2 = str(part1), str(part2)
            if str1 < str2:
                return -1
            elif str1 > str2:
                return 1

    return 0


def _is_compatible_release(version: str, base_version: str) -> bool:
    """Check if version is a compatible release with base_version.

    Compatible release means same major.minor but patch can be higher.

    Args:
        version: Version to check
        base_version: Base version for compatibility

    Returns:
        bool: True if compatible, False otherwise
    """
    try:
        version_parts = [int(x) for x in version.split(".")]
        base_parts = [int(x) for x in base_version.split(".")]

        if len(version_parts) < 2 or len(base_parts) < 2:
            return False

        if version_parts[0] != base_parts[0] or version_parts[1] != base_parts[1]:
            return False

        if len(version_parts) >= 3 and len(base_parts) >= 3:
            return version_parts[2] >= base_parts[2]

        return True
    except (ValueError, IndexError):
        return False


def format_plugin_info(metadata: Dict[str, Any]) -> str:
    """Format plugin metadata for display.

    Args:
        metadata: Plugin metadata dictionary

    Returns:
        str: Formatted plugin information
    """
    name = metadata.get("name", "Unknown")
    version = metadata.get("version", "Unknown")
    description = metadata.get("description", "No description")
    capabilities = metadata.get("capabilities", [])

    info_lines = [
        f"Plugin: {name} v{version}",
        f"Description: {description}",
    ]

    if capabilities:
        info_lines.append(f"Capabilities: {', '.join(capabilities)}")

    return "\n".join(info_lines)
