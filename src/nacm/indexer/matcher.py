from __future__ import annotations

import json
import re
from pathlib import Path

from nacm.utils.paths import agent_dir

WORD_RE = re.compile(r"[\w\u4e00-\u9fff]{2,}")


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
    scored = []
    for item in files:
        haystacks = [
            item["path"].lower(),
            " ".join(item.get("imports", [])).lower(),
            " ".join(item.get("classes", [])).lower(),
            " ".join(item.get("functions", [])).lower(),
            " ".join(item.get("keywords", [])).lower(),
        ]
        score = 0
        for keyword in keywords:
            if keyword in haystacks[0]:
                score += 3
            if any(keyword in haystack for haystack in haystacks[1:]):
                score += 1
        if score:
            scored.append({**item, "score": score, "confidence": _confidence(score)})
    scored.sort(key=lambda item: (-item["score"], item["path"]))
    return scored[:limit]


def _confidence(score: int) -> str:
    if score >= 3:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"
