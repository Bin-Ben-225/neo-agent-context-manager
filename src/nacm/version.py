from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib


PACKAGE_NAME = "neo-agent-context-manager"
FALLBACK_VERSION = "0.1.0a5"


def package_version() -> str:
    source_version = pyproject_version()
    if source_version:
        return source_version
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return FALLBACK_VERSION


def pyproject_version() -> str:
    for parent in Path(__file__).resolve().parents:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            try:
                data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError:
                return ""
            project = data.get("project", {})
            value = project.get("version") if isinstance(project, dict) else ""
            return str(value) if value else ""
    return ""
