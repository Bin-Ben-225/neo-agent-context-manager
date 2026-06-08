import json
from pathlib import Path

from nacm.indexer.matcher import match_files


def write_summary(root: Path, files: list[dict]) -> None:
    index_dir = root / ".agent" / "index"
    index_dir.mkdir(parents=True)
    (index_dir / "file_summary.json").write_text(
        json.dumps({"files": files}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_match_files_prioritizes_explicit_relative_path(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "src/nacm/session/packer.py",
                "imports": [],
                "classes": [],
                "functions": ["render_context_pack"],
                "keywords": ["context", "pack"],
            },
            {
                "path": "src/nacm/indexer/matcher.py",
                "imports": [],
                "classes": [],
                "functions": ["match_files"],
                "keywords": ["context", "pack"],
            },
        ],
    )

    matches = match_files(tmp_path, "update src/nacm/session/packer.py output")

    assert matches[0]["path"] == "src/nacm/session/packer.py"
    assert matches[0]["confidence"] == "High"


def test_match_files_uses_filename_stem_words(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "src/image_loader.py",
                "imports": [],
                "classes": [],
                "functions": ["read"],
                "keywords": [],
            }
        ],
    )

    matches = match_files(tmp_path, "fix image loading failure")

    assert matches[0]["path"] == "src/image_loader.py"
    assert matches[0]["confidence"] == "High"


def test_match_files_matches_function_and_class_names(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "src/reporting.py",
                "imports": ["json"],
                "classes": ["ReportBuilder"],
                "functions": ["render_report"],
                "keywords": [],
            }
        ],
    )

    matches = match_files(tmp_path, "fix ReportBuilder render_report output")

    assert matches[0]["path"] == "src/reporting.py"
    assert matches[0]["score"] >= 2
