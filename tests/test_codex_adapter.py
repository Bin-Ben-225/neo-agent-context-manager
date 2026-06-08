from pathlib import Path

from nacm.adapters.codex import render_codex_prompt, write_codex_prompt


def test_render_codex_prompt_uses_template_constraints():
    prompt = render_codex_prompt()

    assert "First read `.agent/sessions/context_pack.md`." in prompt
    assert "Do not scan the whole repository by default." in prompt
    assert "Do not create or modify the repository root AGENTS.md." in prompt


def test_write_codex_prompt_writes_adapter_output(tmp_path: Path):
    prompt_path = write_codex_prompt(tmp_path)

    assert prompt_path == tmp_path / ".agent" / "codex" / "codex_prompt.md"
    assert prompt_path.exists()
    assert "When finished, remind the user to run `nacm done`." in prompt_path.read_text(
        encoding="utf-8"
    )
