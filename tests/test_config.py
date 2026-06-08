from pathlib import Path

from nacm.config import Profile, load_profile


def test_load_profile_returns_low_memory_defaults_when_file_is_missing(tmp_path: Path):
    profile = load_profile(tmp_path, "low-memory")

    assert profile == Profile(
        name="low-memory",
        max_context_chars=30000,
        max_files_in_context=8,
        max_file_head_kb=16,
        max_tree_depth=3,
    )


def test_load_profile_reads_custom_values_from_agent_profile(tmp_path: Path):
    profile_dir = tmp_path / ".agent" / "profiles"
    profile_dir.mkdir(parents=True)
    (profile_dir / "workstation.toml").write_text(
        "\n".join(
            [
                "max_context_chars = 90000",
                "max_files_in_context = 20",
                "max_file_head_kb = 24",
                "max_tree_depth = 6",
                "",
            ]
        ),
        encoding="utf-8",
    )

    profile = load_profile(tmp_path, "workstation")

    assert profile.name == "workstation"
    assert profile.max_context_chars == 90000
    assert profile.max_files_in_context == 20
    assert profile.max_file_head_kb == 24
    assert profile.max_tree_depth == 6
