from pathlib import Path
import tomllib


ROOT = Path(__file__).parents[1]


def test_release_version_matches_changelog():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert pyproject["project"]["version"] == "0.1.0a5"
    assert "## 0.1.0a5" in changelog
    assert "benchmark reporting with commit, version, and timing fields" in changelog
