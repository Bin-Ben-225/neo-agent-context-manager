from __future__ import annotations

import json
import re
from pathlib import Path

from nacm.utils.paths import agent_dir

WORD_RE = re.compile(r"[\w\u4e00-\u9fff]{2,}")
PATH_RE = re.compile(r"[\w./\\-]+\.[A-Za-z0-9]+")


def extract_keywords(text: str) -> list[str]:
    words = [word.lower() for word in WORD_RE.findall(text)]
    stop = {"the", "and", "with", "fix", "修复"}
    return [word for word in words if word not in stop]


def match_files(root: Path, task_text: str, limit: int = 8) -> list[dict]:
    summary_path = agent_dir(root) / "index" / "file_summary.json"
    if not summary_path.exists():
        return []
    files = json.loads(summary_path.read_text(encoding="utf-8")).get("files", [])
    keywords = extract_keywords(task_text)
    explicit_paths = extract_path_mentions(task_text)
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
                score += 8
                reasons.append("explicit path")
        for keyword in keywords:
            if keyword in haystacks[0]:
                score += 3
                reasons.append(f"path:{keyword}")
            if keyword in stem_words:
                score += 3
                reasons.append(f"filename:{keyword}")
            if any(keyword in haystack for haystack in haystacks[1:]):
                score += 1
                reasons.append(f"summary:{keyword}")
        if score:
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


def _confidence(score: int) -> str:
    if score >= 3:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"
