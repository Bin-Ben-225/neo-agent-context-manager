from __future__ import annotations

import ast
import re
from pathlib import Path

from nacm.constants import MAX_LARGE_FILE_BYTES, SOURCE_EXTENSIONS

IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)
CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
FUNCTION_RE = re.compile(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)|^\s*(?:function|const)\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


def summarize_file(path: Path, max_head_kb: int) -> dict:
    size = path.stat().st_size
    base = {
        "size": size,
        "extension": path.suffix.lower(),
        "imports": [],
        "classes": [],
        "functions": [],
        "methods": [],
        "test_functions": [],
        "exports": [],
        "doc_keywords": [],
        "keywords": [],
        "summary_skipped": False,
    }
    if size > MAX_LARGE_FILE_BYTES or path.suffix.lower() not in SOURCE_EXTENSIONS:
        return {**base, "summary_skipped": True}

    head = path.read_bytes()[: max_head_kb * 1024].decode("utf-8-sig", errors="ignore")
    if path.suffix.lower() == ".py":
        return {**base, **summarize_python(head)}
    imports = sorted({match.group(1) or match.group(2) for match in IMPORT_RE.finditer(head)})
    classes = sorted(set(CLASS_RE.findall(head)))
    functions = sorted({left or right for left, right in FUNCTION_RE.findall(head)})
    keywords = sorted({word.lower() for word in WORD_RE.findall(head)})[:40]
    return {
        **base,
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "keywords": keywords,
    }


def summarize_python(source: str) -> dict:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return summarize_with_regex(source)

    imports: set[str] = set()
    classes: set[str] = set()
    functions: set[str] = set()
    methods: set[str] = set()
    test_functions: set[str] = set()
    exports: set[str] = set()
    doc_parts: list[str] = []

    module_doc = ast.get_docstring(tree)
    if module_doc:
        doc_parts.append(module_doc)

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.update(import_names(node))
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
            class_doc = ast.get_docstring(node)
            if class_doc:
                doc_parts.append(class_doc)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(f"{node.name}.{child.name}")
                    if child.name.startswith("test_"):
                        test_functions.add(child.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
            if node.name.startswith("test_"):
                test_functions.add(node.name)
            function_doc = ast.get_docstring(node)
            if function_doc:
                doc_parts.append(function_doc)
        elif isinstance(node, ast.Assign):
            exports.update(export_names(node))

    keywords = sorted({word.lower() for word in WORD_RE.findall(source)})[:40]
    doc_keywords = sorted({word.lower() for word in WORD_RE.findall(" ".join(doc_parts))})[:20]
    return {
        "imports": sorted(imports),
        "classes": sorted(classes),
        "functions": sorted(functions),
        "methods": sorted(methods),
        "test_functions": sorted(test_functions),
        "exports": sorted(exports),
        "doc_keywords": doc_keywords,
        "keywords": keywords,
    }


def summarize_with_regex(source: str) -> dict:
    imports = sorted({match.group(1) or match.group(2) for match in IMPORT_RE.finditer(source)})
    classes = sorted(set(CLASS_RE.findall(source)))
    functions = sorted({left or right for left, right in FUNCTION_RE.findall(source)})
    keywords = sorted({word.lower() for word in WORD_RE.findall(source)})[:40]
    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "methods": [],
        "test_functions": [name for name in functions if name.startswith("test_")],
        "exports": [],
        "doc_keywords": [],
        "keywords": keywords,
    }


def import_names(node: ast.Import | ast.ImportFrom) -> set[str]:
    if isinstance(node, ast.Import):
        return {alias.name for alias in node.names}
    module = node.module or ""
    return {f"{module}.{alias.name}" if module else alias.name for alias in node.names}


def export_names(node: ast.Assign) -> set[str]:
    if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
        return set()
    if isinstance(node.value, (ast.List, ast.Tuple)):
        return {
            item.value
            for item in node.value.elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        }
    return set()
