from pathlib import Path

from nacm.templates.renderer import render_template


def test_render_codex_prompt_template_contains_required_constraints():
    output = render_template("codex_prompt.md.j2", {})

    assert "First read `.agent/sessions/context_pack.md`." in output
    assert "Do not scan the whole repository by default." in output
    assert "Do not create or modify the repository root AGENTS.md." in output
    assert "When finished, remind the user to run `nacm done`." in output


def test_render_context_pack_template_includes_file_summary_and_no_match_guidance():
    output = render_template(
        "context_pack.md.j2",
        {
            "task": "fix src/images.py image loading failure",
            "matched": [
                {
                    "path": "src/images.py",
                    "score": 12,
                    "confidence": "High",
                    "imports": [],
                    "classes": [],
                    "functions": ["load_image"],
                    "keywords": ["load_image", "path"],
                    "reasons": ["explicit path"],
                }
            ],
            "confidence_groups": {
                "High": [
                    {
                        "path": "src/images.py",
                        "score": 12,
                        "confidence": "High",
                        "summary_lines": ["  - Functions: load_image"],
                    }
                ],
                "Medium": [],
                "Low": [],
            },
            "forbidden_paths": [".agent/", "dist/"],
        },
    )

    assert "fix src/images.py image loading failure" in output
    assert "`src/images.py` (score: 12)" in output
    assert "Functions: load_image" in output
    assert "No relevant files matched this task." not in output


def test_context_pack_template_no_match_guidance():
    output = render_template(
        "context_pack.md.j2",
        {
            "task": "repair billing webhook retry",
            "matched": [],
            "confidence_groups": {"High": [], "Medium": [], "Low": []},
            "forbidden_paths": [".agent/"],
        },
    )

    assert "No relevant files matched this task." in output
    assert "Use a scoped search before reading additional files." in output


def test_template_files_are_packaged():
    template_dir = Path(__file__).parents[1] / "src" / "nacm" / "templates"

    assert (template_dir / "codex_prompt.md.j2").exists()
    assert (template_dir / "context_pack.md.j2").exists()
