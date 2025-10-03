"""Template rendering for bot messages using Jinja2."""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders HTML templates using Jinja2 for Telegram messages.

    This class is responsible for:
    - Configuring the Jinja2 environment
    - Loading templates from the templates/messages directory
    - Rendering templates with provided context
    """

    def __init__(self, templates_dir: Path | None = None) -> None:
        """Initialize the template renderer.

        Args:
            templates_dir: Optional custom templates directory.
                          Defaults to 'templates/messages' in project root.
        """
        if templates_dir is None:
            templates_dir = Path("templates") / "messages"

        self._templates_dir = templates_dir
        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **context: object) -> str:
        """Render a template with the provided context.

        Args:
            template_name: Name of the template file (e.g., 'start.html')
            **context: Context variables to pass to the template

        Returns:
            Rendered HTML string

        Raises:
            Exception: If template rendering fails
        """
        try:
            template = self._env.get_template(template_name)
            return template.render(**context).strip()

        except Exception as e:
            logger.error("Error rendering template %s: %s", template_name, e)
            return f"❌ Error al generar mensaje: {template_name}"

