from __future__ import annotations


def copy_text(text: str) -> tuple[bool, str | None]:
    try:
        import pyperclip

        pyperclip.copy(text)
        return True, None
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)
