"""Template rendering for bot messages using Jinja2."""

import logging
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError,
    select_autoescape,
)

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
            TemplateNotFound: If template file doesn't exist
            TemplateSyntaxError: If template has syntax errors
            UndefinedError: If template references undefined variables
        """
        try:
            template = self._env.get_template(template_name)
            return template.render(**context).strip()

        except TemplateNotFound:
            logger.error("Template not found: %s", template_name)
            return "❌ Internal server error"

        except TemplateSyntaxError as e:
            logger.error("Template syntax error in %s: %s", template_name, e)
            return "❌ Internal server error"

        except UndefinedError as e:
            logger.error("Undefined variable in template %s: %s", template_name, e)
            return "❌ Internal server error"

        except Exception as e:
            # Fallback for unexpected errors - log with full traceback
            logger.error(
                "Unexpected error rendering template %s: %s",
                template_name,
                e,
                exc_info=True,
            )
            return "❌ Internal server error"

