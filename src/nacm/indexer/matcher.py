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
    relations = load_relation_index(root)
    explicit_paths = extract_path_mentions(task_text)
    keywords = extract_query_keywords(task_text, explicit_paths)
    semantic_keywords = extract_semantic_keywords(task_text, explicit_paths)
    common_path_terms = common_path_tokens(files)
    scored = []
    for item in files:
        path = item["path"].lower()
        path_name = Path(item["path"]).name.lower()
        stem_words = set(extract_keywords(Path(item["path"]).stem.replace("_", " ").replace("-", " ")))
        score = 0
        explanations: list[dict] = []
        for mention in explicit_paths:
            if mention == path or mention == path_name or path.endswith(f"/{mention}"):
                score += add_explanation(explanations, "explicit path", mention, 12)
            elif path_name == Path(mention).name:
                score += add_explanation(explanations, "explicit filename", Path(mention).name, 6)
        for keyword in keywords:
            if keyword in path and keyword not in common_path_terms:
                score += add_explanation(explanations, "path", keyword, 3)
            if keyword in stem_words:
                score += add_explanation(explanations, "filename", keyword, 3)
            symbol_explanation = symbol_match_explanation(keyword, item)
            if symbol_explanation:
                explanations.append(symbol_explanation)
                score += symbol_explanation["weight"]
            elif summary_match(keyword, item):
                score += add_explanation(explanations, "summary", keyword, 1)
        positive_score = score
        quality_explanations = file_quality_explanations(item, semantic_keywords)
        explanations.extend(quality_explanations)
        score += sum(explanation["weight"] for explanation in quality_explanations)
        if score > 0 or (score == 0 and positive_score > 0):
            scored.append(
                {
                    **item,
                    "score": score,
                    "confidence": _confidence(score),
                    "reasons": explanation_reasons(explanations),
                    "explanations": explanations,
                }
            )
    apply_relation_boosts(scored, relations)
    scored.sort(key=lambda item: (-item["score"], item["path"]))
    return scored[:limit]


def load_relation_index(root: Path) -> dict:
    relation_path = agent_dir(root) / "index" / "relation_index.json"
    if not relation_path.exists():
        return {}
    return json.loads(relation_path.read_text(encoding="utf-8"))


def apply_relation_boosts(scored: list[dict], relations: dict) -> None:
    if not relations:
        return
    by_path = {item["path"]: item for item in scored}
    initially_matched = set(by_path)
    for source, tests in relations.get("source_tests", {}).items():
        if source in initially_matched:
            for test_path in tests:
                if test_path in by_path:
                    add_scored_explanation(
                        by_path[test_path],
                        "relation",
                        f"related test for {source}",
                        4,
                    )
        for test_path in tests:
            if test_path in initially_matched and source in by_path:
                add_scored_explanation(
                    by_path[source],
                    "relation",
                    f"related source for {test_path}",
                    4,
                )
    for module, importers in relations.get("importers", {}).items():
        source = relations.get("modules", {}).get(module)
        if source and source in initially_matched:
            for importer in importers:
                if importer in by_path and importer != source and not has_quality_penalty(by_path[importer]):
                    add_scored_explanation(by_path[importer], "relation", f"importer of {module}", 2)


def add_scored_explanation(item: dict, signal: str, detail: str, weight: int) -> None:
    explanation = {"signal": signal, "detail": detail, "weight": weight}
    if explanation in item.get("explanations", []):
        return
    item.setdefault("explanations", []).append(explanation)
    item["score"] += weight
    item["confidence"] = _confidence(item["score"])
    item["reasons"] = explanation_reasons(item["explanations"])


def has_quality_penalty(item: dict) -> bool:
    return any(
        explanation["signal"] == "quality" and explanation["weight"] < 0
        for explanation in item.get("explanations", [])
    )


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


def extract_semantic_keywords(task_text: str, explicit_paths: set[str]) -> list[str]:
    scrubbed = task_text
    for mention in explicit_paths:
        scrubbed = scrubbed.replace(mention, " ")
        scrubbed = scrubbed.replace(mention.replace("/", "\\"), " ")
    return dedupe_keywords(extract_keywords(scrubbed))


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
    explanation = symbol_match_explanation(keyword, item)
    return explanation["weight"] if explanation else 0


def symbol_match_explanation(keyword: str, item: dict) -> dict | None:
    lowered = keyword.lower()
    symbol_values = [*item.get("functions", []), *item.get("classes", []), *item.get("exports", [])]
    for value in symbol_values:
        text = str(value)
        if lowered == text.lower():
            return {"signal": "symbol", "detail": text, "weight": 5}
    for value in item.get("methods", []):
        text = str(value)
        short_name = text.rsplit(".", 1)[-1]
        if lowered in {text.lower(), short_name.lower()}:
            return {"signal": "method", "detail": short_name, "weight": 5}
    for value in item.get("test_functions", []):
        text = str(value)
        if lowered == text.lower():
            return {"signal": "test", "detail": text, "weight": 5}
        if text.lower() == f"test_{lowered}":
            return {"signal": "test", "detail": text, "weight": 4}
    for value in [*item.get("functions", []), *item.get("methods", [])]:
        text = str(value)
        short_name = text.rsplit(".", 1)[-1]
        if short_name.lower().endswith(f"_{lowered}"):
            return {"signal": "symbol", "detail": short_name, "weight": 3}
    return None


def summary_match(keyword: str, item: dict) -> bool:
    haystack = " ".join(
        str(value)
        for field in ("imports", "keywords", "doc_keywords")
        for value in item.get(field, [])
    ).lower()
    return keyword in haystack


def add_explanation(explanations: list[dict], signal: str, detail: str, weight: int) -> int:
    explanations.append({"signal": signal, "detail": detail, "weight": weight})
    return weight


def explanation_reasons(explanations: list[dict]) -> list[str]:
    reasons = []
    for explanation in explanations:
        signal = explanation["signal"]
        detail = explanation["detail"]
        weight = explanation["weight"]
        if weight < 0:
            reasons.append(f"{signal}:{detail}")
        elif signal in {"explicit path", "explicit filename"}:
            reasons.append(signal)
        else:
            reasons.append(f"{signal}:{detail}")
    return sorted(set(reasons))


def file_quality_adjustment(item: dict, query_keywords: list[str] | None = None) -> int:
    return sum(explanation["weight"] for explanation in file_quality_explanations(item, query_keywords))


def file_quality_explanations(item: dict, query_keywords: list[str] | None = None) -> list[dict]:
    path = Path(item["path"])
    suffix = path.suffix.lower()
    parts = {part.lower() for part in path.parts}
    query_words = set(query_keywords or [])
    explanations = []
    if suffix in LOW_VALUE_EXTENSIONS:
        explanations.append({"signal": "quality", "detail": f"{suffix} file demoted", "weight": -6})
    if parts & LOW_VALUE_PATH_PARTS:
        explanations.append({"signal": "quality", "detail": "localization path demoted", "weight": -6})
    if "benchmark" in path.stem.lower() and not (query_words & {"benchmark", "benchmarks", "性能"}):
        explanations.append(
            {
                "signal": "quality",
                "detail": "benchmark file demoted for non-benchmark task",
                "weight": -6,
            }
        )
    return explanations


def _confidence(score: int) -> str:
    if score >= 5:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"
