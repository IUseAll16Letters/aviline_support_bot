from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from constants import TEMPLATES


env = Environment(
    loader=FileSystemLoader(TEMPLATES),
    autoescape=select_autoescape(['html'])
)


def render_template(template_name: str, values: dict[str, Any] | None = None, **kwargs):
    template = env.get_template(template_name)

    if values:
        rendered_template = template.render(values, **kwargs)
    else:
        rendered_template = template.render(**kwargs)

    return rendered_template
