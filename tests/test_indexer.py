import json
from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def test_index_build_skips_ignored_dirs_and_uses_posix_paths(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        "import os\n\nclass App:\n    pass\n\ndef run():\n    return True\n",
        encoding="utf-8",
    )
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").write_text("def ignored(): pass\n", encoding="utf-8")
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    paths = {item["path"] for item in summary["files"]}
    assert "src/app.py" in paths
    assert "node_modules/ignored.py" not in paths
    app_summary = next(item for item in summary["files"] if item["path"] == "src/app.py")
    assert "os" in app_summary["imports"]
    assert "App" in app_summary["classes"]
    assert "run" in app_summary["functions"]


def test_index_build_skips_python_cache_dirs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src" / "__pycache__").mkdir(parents=True)
    (tmp_path / "src" / "__pycache__" / "app.cpython-311.pyc").write_bytes(b"cache")
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    paths = {item["path"] for item in summary["files"]}
    assert "src/app.py" in paths
    assert "src/__pycache__/app.cpython-311.pyc" not in paths


def test_index_build_skips_large_file_content_summary(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "large.txt").write_text("x" * 200_000, encoding="utf-8")
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    large = next(item for item in summary["files"] if item["path"] == "large.txt")
    assert large["summary_skipped"] is True


def test_index_build_extracts_symbols_from_utf8_bom_file(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "images.py").write_bytes(
        b"\xef\xbb\xbfdef load_image(path):\n    return path\n"
    )
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    image_summary = next(item for item in summary["files"] if item["path"] == "src/images.py")
    assert "load_image" in image_summary["functions"]


def test_index_build_extracts_python_imports_methods_tests_and_exports(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "service.py").write_text(
        '"""Service helpers for rendering reports."""\n'
        "import json\n"
        "from pathlib import Path\n\n"
        "__all__ = ['ReportService']\n\n"
        "class ReportService:\n"
        "    def render_report(self):\n"
        "        return json.dumps({})\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_service.py").write_text(
        "def test_render_report():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    service = next(item for item in summary["files"] if item["path"] == "src/service.py")
    tests = next(item for item in summary["files"] if item["path"] == "tests/test_service.py")
    assert "json" in service["imports"]
    assert "pathlib.Path" in service["imports"]
    assert "ReportService.render_report" in service["methods"]
    assert "ReportService" in service["exports"]
    assert "service" in service["doc_keywords"]
    assert "test_render_report" in tests["test_functions"]
