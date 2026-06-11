from __future__ import annotations

from pathlib import Path


def build_relation_index(files: list[dict]) -> dict:
    modules = {
        module_name(item["path"]): item["path"]
        for item in files
        if item["path"].endswith(".py") and module_name(item["path"])
    }
    importers = {module: [] for module in modules}
    source_tests: dict[str, list[str]] = {}
    test_sources: dict[str, list[str]] = {}

    for item in files:
        path = item["path"]
        imports = {str(value) for value in item.get("imports", [])}
        for module, source_path in modules.items():
            if module in imports or any(imported.startswith(f"{module}.") for imported in imports):
                importers.setdefault(module, []).append(path)
                if is_test_path(path) and not is_test_path(source_path) and not source_path.endswith("__init__.py"):
                    source_tests.setdefault(source_path, []).append(path)
                    test_sources.setdefault(path, []).append(source_path)

    for test_item in [item for item in files if is_test_path(item["path"])]:
        stem_source = source_for_test_stem(test_item["path"], modules)
        if stem_source:
            source_tests.setdefault(stem_source, []).append(test_item["path"])
            test_sources.setdefault(test_item["path"], []).append(stem_source)

    return {
        "modules": dict(sorted(modules.items())),
        "importers": sort_mapping(importers),
        "source_tests": sort_mapping(source_tests),
        "test_sources": sort_mapping(test_sources),
    }


def render_relation_index(relations: dict) -> str:
    lines = ["# Relation Index", "", "## Source To Tests", ""]
    if relations["source_tests"]:
        for source, tests in relations["source_tests"].items():
            lines.append(f"- `{source}`: {', '.join(f'`{test}`' for test in tests)}")
    else:
        lines.append("- None")
    lines.extend(["", "## Module Importers", ""])
    wrote_importer = False
    for module, importers in relations["importers"].items():
        if importers:
            lines.append(f"- `{module}`: {', '.join(f'`{path}`' for path in importers)}")
            wrote_importer = True
    if not wrote_importer:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def module_name(path_text: str) -> str:
    path = Path(path_text)
    if path.suffix != ".py":
        return ""
    parts = list(path.with_suffix("").parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts or any(part in {"tests", "test"} for part in parts):
        return ""
    return ".".join(parts)


def is_test_path(path_text: str) -> bool:
    parts = Path(path_text).parts
    return "tests" in parts or Path(path_text).name.startswith("test_")


def source_for_test_stem(test_path: str, modules: dict[str, str]) -> str:
    stem = Path(test_path).stem
    if stem.startswith("test_"):
        source_name = stem.removeprefix("test_")
        for module, source_path in modules.items():
            if module.rsplit(".", 1)[-1] == source_name:
                return source_path
    return ""


def sort_mapping(mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    return {key: sorted(set(values)) for key, values in sorted(mapping.items()) if values}
