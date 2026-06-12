from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_distribution_doc_covers_supported_install_channels():
    doc = (ROOT / "docs" / "distribution.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "GitHub Release" in doc
    assert "pipx install" in doc
    assert "uv tool install" in doc
    assert "Homebrew" in doc
    assert "WinGet" in doc
    assert "PyPI" in doc
    assert "release-manifest.json" in doc
    assert "Distribution" in readme


def test_release_manifest_script_records_artifact_metadata():
    script = (ROOT / "scripts" / "write-release-manifest.ps1").read_text(encoding="utf-8")
    checklist = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")

    assert "Get-FileHash" in script
    assert "SHA256" in script
    assert "Length" in script
    assert "neo-agent-context-manager" in script
    assert "release-manifest.json" in script
    assert ".\\scripts\\write-release-manifest.ps1" in checklist
