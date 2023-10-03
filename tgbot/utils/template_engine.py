__all__ = ("render_template", )

from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from config.settings import TG_BOT_TEMPLATES


env = Environment(
    loader=FileSystemLoader(TG_BOT_TEMPLATES),
    autoescape=select_autoescape(['html']),
)


def render_template(template_name: str, values: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    template = env.get_template(template_name)

    if values:
        rendered_template = template.render(values, **kwargs)
    else:
        rendered_template = template.render(**kwargs)

    return rendered_template
