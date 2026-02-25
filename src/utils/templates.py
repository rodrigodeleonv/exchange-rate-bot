"""Template rendering utilities using Jinja2."""

import logging
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_jinja_env() -> Environment:
    """Get cached Jinja2 environment."""
    templates_dir = Path("templates") / "messages"
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(template_name: str, **context: object) -> str:
    """Render a template with the provided context.

    Args:
        template_name: Name of the template file (e.g., 'start.html')
        **context: Context variables to pass to the template

    Returns:
        Rendered HTML string
    """
    try:
        env = get_jinja_env()
        template = env.get_template(template_name)
        return template.render(**context).strip()
    except Exception as e:
        logger.error("Error rendering template %s: %s", template_name, e, exc_info=True)
        return "❌ Internal server error"
