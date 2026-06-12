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


def test_publish_validation_script_checks_python_release_artifacts():
    script = (ROOT / "scripts" / "validate-publish.ps1").read_text(encoding="utf-8")
    checklist = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")
    distribution = (ROOT / "docs" / "distribution.md").read_text(encoding="utf-8")

    assert "twine" in script
    assert "check" in script
    assert "py -3.11 -m twine --version" in script
    assert "write-release-manifest.ps1" in script
    assert "neo_agent_context_manager-*.whl" in script
    assert "neo_agent_context_manager-*.tar.gz" in script
    assert ".\\scripts\\validate-publish.ps1" in checklist
    assert "validate-publish.ps1" in distribution


def test_install_validation_uses_current_pipx_uninstall_syntax():
    script = (ROOT / "scripts" / "validate-install.ps1").read_text(encoding="utf-8")

    assert "pipx uninstall neo-agent-context-manager --yes" not in script
    assert "pipx uninstall neo-agent-context-manager" in script
    assert ".local\\bin\\nacm.exe" in script
    assert "& $nacm --version" in script
