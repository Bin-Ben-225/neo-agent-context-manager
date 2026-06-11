from __future__ import annotations

IGNORED_DIRS = {
    ".git",
    ".agent",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    "target",
    ".cache",
    ".pytest_cache",
    "__pycache__",
    "logs",
    "output",
    "samples",
}

IGNORED_PREFIXES = ("assets/raw",)

FORBIDDEN_PATHS = [
    ".agent/",
    ".venv/",
    "venv/",
    "node_modules/",
    "build/",
    "dist/",
    "target/",
    ".cache/",
    ".pytest_cache/",
    "__pycache__/",
]

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".html",
    ".css",
}

DEFAULT_PROFILE = "low-memory"
MAX_LARGE_FILE_BYTES = 128_000
