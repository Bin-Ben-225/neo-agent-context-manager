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


def test_match_files_keeps_filesize_task_focused_on_source_and_tests(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "src/humanize/filesize.py",
                "imports": ["math"],
                "classes": [],
                "functions": ["naturalsize"],
                "keywords": ["filesize", "naturalsize", "bytes"],
            },
            {
                "path": "tests/test_filesize.py",
                "imports": ["humanize", "pytest"],
                "classes": [],
                "functions": ["test_naturalsize"],
                "keywords": ["filesize", "naturalsize", "assert"],
            },
            {
                "path": "src/humanize/locale/ar/LC_MESSAGES/humanize.po",
                "imports": [],
                "classes": [],
                "functions": [],
                "keywords": [],
            },
            {
                "path": "src/humanize/py.typed",
                "imports": [],
                "classes": [],
                "functions": [],
                "keywords": [],
            },
        ],
    )

    matches = match_files(tmp_path, "检查 src/humanize/filesize.py 中 naturalsize 的文件大小格式化逻辑")

    assert [match["path"] for match in matches[:2]] == [
        "src/humanize/filesize.py",
        "tests/test_filesize.py",
    ]
    assert "src/humanize/locale/ar/LC_MESSAGES/humanize.po" not in [
        match["path"] for match in matches
    ]
    assert "src/humanize/py.typed" not in [match["path"] for match in matches]


def test_match_files_promotes_exact_time_api_symbols_to_high_confidence(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "src/humanize/time.py",
                "imports": ["datetime"],
                "classes": ["Unit"],
                "functions": ["naturalday", "naturaltime", "naturaldate"],
                "keywords": ["time", "date"],
            },
            {
                "path": "tests/test_time.py",
                "imports": ["humanize", "pytest"],
                "classes": [],
                "functions": ["test_naturalday", "test_naturaltime"],
                "keywords": ["time", "date"],
            },
            {
                "path": "tests/test_benchmarks.py",
                "imports": ["humanize"],
                "classes": [],
                "functions": ["test_naturalday"],
                "keywords": ["benchmark"],
            },
        ],
    )

    matches = match_files(tmp_path, "检查 naturaltime naturalday 相关日期时间格式化逻辑")

    assert [match["path"] for match in matches[:2]] == [
        "src/humanize/time.py",
        "tests/test_time.py",
    ]
    assert matches[0]["confidence"] == "High"
    assert matches[1]["confidence"] == "High"


def test_match_files_demotes_benchmarks_for_non_benchmark_tasks(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "tests/test_time.py",
                "imports": ["humanize", "pytest"],
                "classes": [],
                "functions": ["test_naturalday", "test_naturaltime"],
                "keywords": ["time", "date"],
            },
            {
                "path": "tests/test_benchmarks.py",
                "imports": ["humanize"],
                "classes": [],
                "functions": ["test_naturalday", "test_naturaltime"],
                "keywords": ["benchmark", "time"],
            },
        ],
    )

    matches = match_files(tmp_path, "检查 naturaltime naturalday 相关日期时间格式化逻辑")

    assert [match["path"] for match in matches[:2]] == [
        "tests/test_time.py",
        "tests/test_benchmarks.py",
    ]


def test_match_files_avoids_project_root_term_polluting_locale_files(tmp_path: Path):
    write_summary(
        tmp_path,
        [
            {
                "path": "src/humanize/number.py",
                "imports": [],
                "classes": [],
                "functions": ["intcomma", "intword"],
                "keywords": ["number"],
            },
            {
                "path": "tests/test_number.py",
                "imports": ["humanize"],
                "classes": [],
                "functions": ["test_intcomma", "test_intword"],
                "keywords": ["number"],
            },
            {
                "path": "src/humanize/locale/ca_ES/LC_MESSAGES/humanize.po",
                "imports": [],
                "classes": [],
                "functions": [],
                "keywords": [],
            },
        ],
    )

    matches = match_files(tmp_path, "检查 humanize number intcomma intword 相关逻辑和测试")

    assert [match["path"] for match in matches[:2]] == [
        "src/humanize/number.py",
        "tests/test_number.py",
    ]
    assert "src/humanize/locale/ca_ES/LC_MESSAGES/humanize.po" not in [
        match["path"] for match in matches
    ]
