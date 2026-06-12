from pathlib import Path
import tomllib


ROOT = Path(__file__).parents[1]


def test_release_version_matches_changelog():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert pyproject["project"]["version"] == "0.1.0a4"
    assert "## 0.1.0a4" in changelog
    assert "Project-local UserPromptSubmit hook installer" in changelog
