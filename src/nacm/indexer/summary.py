from __future__ import annotations

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
        "keywords": [],
        "summary_skipped": False,
    }
    if size > MAX_LARGE_FILE_BYTES or path.suffix.lower() not in SOURCE_EXTENSIONS:
        return {**base, "summary_skipped": True}

    head = path.read_bytes()[: max_head_kb * 1024].decode("utf-8", errors="ignore")
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
