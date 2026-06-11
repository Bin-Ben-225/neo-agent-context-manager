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


def test_workstation_relation_index_boosts_related_tests(tmp_path: Path):
    copy_fixture(tmp_path)
    init_workspace(tmp_path, profile="low-memory")
    build_index(tmp_path, profile="workstation")

    matches = match_files(tmp_path, "check calculate_alpha implementation")

    paths = [match["path"] for match in matches[:3]]
    assert "src/sample_pkg/alpha.py" in paths
    assert "tests/test_alpha.py" in paths
    test_match = next(match for match in matches if match["path"] == "tests/test_alpha.py")
    assert {
        "signal": "relation",
        "detail": "related test for src/sample_pkg/alpha.py",
        "weight": 4,
    } in test_match["explanations"]


def test_workstation_relation_index_boosts_related_source_from_test_query(tmp_path: Path):
    copy_fixture(tmp_path)
    init_workspace(tmp_path, profile="low-memory")
    build_index(tmp_path, profile="workstation")

    matches = match_files(tmp_path, "fix tests/test_alpha.py failure")

    source_match = next(match for match in matches if match["path"] == "src/sample_pkg/alpha.py")
    assert {
        "signal": "relation",
        "detail": "related source for tests/test_alpha.py",
        "weight": 4,
    } in source_match["explanations"]


def test_relation_importer_boost_does_not_promote_demoted_benchmark_files(tmp_path: Path):
    copy_fixture(tmp_path)
    init_workspace(tmp_path, profile="low-memory")
    build_index(tmp_path, profile="workstation")

    matches = match_files(tmp_path, "check calculate_alpha implementation")
    paths = [match["path"] for match in matches]

    assert "benchmarks/test_alpha_benchmark.py" not in paths
