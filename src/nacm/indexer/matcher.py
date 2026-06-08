from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from nacm.utils.paths import agent_dir

WORD_RE = re.compile(r"[\w\u4e00-\u9fff]{2,}")
PATH_RE = re.compile(r"[\w./\\-]+\.[A-Za-z0-9]+")
STOP_WORDS = {
    "the",
    "and",
    "with",
    "fix",
    "src",
    "py",
    "python",
    "test",
    "tests",
    "相关",
    "逻辑",
    "检查",
    "文件",
    "格式化",
}
LOW_VALUE_EXTENSIONS = {".po", ".typed", ".mo", ".pot"}
LOW_VALUE_PATH_PARTS = {"locale", "locales", "lc_messages"}


def extract_keywords(text: str) -> list[str]:
    words = [word.lower() for word in WORD_RE.findall(text)]
    return [word for word in words if word not in STOP_WORDS]


def match_files(root: Path, task_text: str, limit: int = 8) -> list[dict]:
    summary_path = agent_dir(root) / "index" / "file_summary.json"
    if not summary_path.exists():
        return []
    files = json.loads(summary_path.read_text(encoding="utf-8")).get("files", [])
    explicit_paths = extract_path_mentions(task_text)
    keywords = extract_query_keywords(task_text, explicit_paths)
    common_path_terms = common_path_tokens(files)
    scored = []
    for item in files:
        path = item["path"].lower()
        path_name = Path(item["path"]).name.lower()
        stem_words = set(extract_keywords(Path(item["path"]).stem.replace("_", " ").replace("-", " ")))
        haystacks = [
            path,
            " ".join(item.get("imports", [])).lower(),
            " ".join(item.get("classes", [])).lower(),
            " ".join(item.get("functions", [])).lower(),
            " ".join(item.get("keywords", [])).lower(),
        ]
        score = 0
        reasons = []
        for mention in explicit_paths:
            if mention == path or mention == path_name or path.endswith(f"/{mention}"):
                score += 12
                reasons.append("explicit path")
            elif path_name == Path(mention).name:
                score += 6
                reasons.append("explicit filename")
        for keyword in keywords:
            if keyword in path and keyword not in common_path_terms:
                score += 3
                reasons.append(f"path:{keyword}")
            if keyword in stem_words:
                score += 3
                reasons.append(f"filename:{keyword}")
            symbol_score = symbol_match_score(keyword, item)
            if symbol_score:
                score += symbol_score
                reasons.append(f"symbol:{keyword}")
            elif keyword in haystacks[4] or keyword in haystacks[1]:
                score += 1
                reasons.append(f"summary:{keyword}")
        score += file_quality_adjustment(item, keywords)
        if score > 0:
            scored.append(
                {
                    **item,
                    "score": score,
                    "confidence": _confidence(score),
                    "reasons": sorted(set(reasons)),
                }
            )
    scored.sort(key=lambda item: (-item["score"], item["path"]))
    return scored[:limit]


def extract_path_mentions(text: str) -> set[str]:
    return {match.replace("\\", "/").lower().strip("./") for match in PATH_RE.findall(text)}


def extract_query_keywords(task_text: str, explicit_paths: set[str]) -> list[str]:
    scrubbed = task_text
    path_stems = []
    for mention in explicit_paths:
        scrubbed = scrubbed.replace(mention, " ")
        scrubbed = scrubbed.replace(mention.replace("/", "\\"), " ")
        path_stems.extend(extract_keywords(Path(mention).stem.replace("_", " ").replace("-", " ")))
    keywords = extract_keywords(scrubbed)
    return dedupe_keywords([*keywords, *path_stems])


def dedupe_keywords(words: list[str]) -> list[str]:
    seen = set()
    result = []
    for word in words:
        if word not in seen:
            seen.add(word)
            result.append(word)
    return result


def common_path_tokens(files: list[dict]) -> set[str]:
    counter: Counter[str] = Counter()
    for item in files:
        path = Path(item["path"])
        tokens = set()
        for part in path.parts:
            tokens.update(extract_keywords(Path(part).stem.replace("_", " ").replace("-", " ")))
        counter.update(tokens)
    threshold = max(3, len(files) // 3)
    return {token for token, count in counter.items() if count >= threshold}


def symbol_match_score(keyword: str, item: dict) -> int:
    functions = [str(value).lower() for value in item.get("functions", [])]
    classes = [str(value).lower() for value in item.get("classes", [])]
    if keyword in functions or keyword in classes:
        return 5
    if any(symbol == f"test_{keyword}" for symbol in functions):
        return 4
    if any(symbol.endswith(f"_{keyword}") for symbol in functions):
        return 3
    return 0


def file_quality_adjustment(item: dict, query_keywords: list[str] | None = None) -> int:
    path = Path(item["path"])
    suffix = path.suffix.lower()
    parts = {part.lower() for part in path.parts}
    query_words = set(query_keywords or [])
    adjustment = 0
    if suffix in LOW_VALUE_EXTENSIONS:
        adjustment -= 6
    if parts & LOW_VALUE_PATH_PARTS:
        adjustment -= 6
    if "benchmark" in path.stem.lower() and not (query_words & {"benchmark", "benchmarks", "性能"}):
        adjustment -= 6
    return adjustment


def _confidence(score: int) -> str:
    if score >= 5:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"
