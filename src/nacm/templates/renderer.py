from __future__ import annotations

from importlib import resources

from jinja2 import Environment, StrictUndefined


def render_template(name: str, context: dict) -> str:
    template_text = resources.files("nacm.templates").joinpath(name).read_text(encoding="utf-8")
    environment = Environment(
        autoescape=False,
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=StrictUndefined,
    )
    template = environment.from_string(template_text)
    return template.render(**context)
