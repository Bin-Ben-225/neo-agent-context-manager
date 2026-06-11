import shutil
from pathlib import Path

from nacm.indexer.matcher import match_files
from nacm.indexer.scanner import build_index
from nacm.workspace import init_workspace


FIXTURE = Path(__file__).parent / "fixtures" / "python_quality_project"


def copy_fixture(dst: Path) -> None:
    shutil.copytree(FIXTURE, dst, dirs_exist_ok=True)


def test_python_quality_fixture_keeps_core_source_and_tests_first(tmp_path: Path):
    copy_fixture(tmp_path)
    init_workspace(tmp_path, profile="low-memory")
    build_index(tmp_path, profile="low-memory")

    matches = match_files(tmp_path, "check alpha calculation formatting and tests")

    assert [match["path"] for match in matches[:2]] == [
        "src/sample_pkg/alpha.py",
        "tests/test_alpha.py",
    ]
    assert "src/sample_pkg/locale/en/LC_MESSAGES/sample.po" not in [
        match["path"] for match in matches
    ]


def test_python_quality_fixture_can_target_benchmarks_when_requested(tmp_path: Path):
    copy_fixture(tmp_path)
    init_workspace(tmp_path, profile="low-memory")
    build_index(tmp_path, profile="low-memory")

    matches = match_files(tmp_path, "benchmark alpha calculation performance")

    assert matches[0]["path"] == "benchmarks/test_alpha_benchmark.py"
