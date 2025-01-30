from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp.agents.templates import AgentTemplate
from mcp.server.fastmcp.exceptions import AgentError
from mcp.server.fastmcp.utilities.logging import get_logger

if TYPE_CHECKING:
    from mcp.server.fastmcp.server import Context

logger = get_logger(__name__)


class AgentManager:
    """Manages FastMCP agents."""

    def __init__(self, warn_on_duplicate_agents: bool = True):
        self._templates: dict[str, AgentTemplate] = {}
        self.warn_on_duplicate_agents = warn_on_duplicate_agents

    def get_template(self, name: str) -> AgentTemplate | None:
        """Get agent by name."""
        return self._templates.get(name)

    def list_templates(self) -> list[AgentTemplate]:
        """List all registered agent templates."""
        return list(self._templates.values())

    def add_template(
        self,
        fn: Callable,
        name: str | None = None,
        description: str | None = None,
    ) -> AgentTemplate:
        """Add a template to the server."""
        template = AgentTemplate.from_function(fn, name=name, description=description)
        existing = self._templates.get(template.name)
        if existing:
            if self.warn_on_duplicate_agents:
                logger.warning(f"Agent already exists: {template.name}")
            return existing
        self._templates[template.name] = template
        return template

    async def run_agent(
        self, name: str, arguments: dict, context: "Context | None" = None
    ) -> Any:
        """Call a agent by name with arguments."""
        template = self.get_template(name)
        if not template:
            raise AgentError(f"Unknown agent: {name}")

        return await template.fn(arguments, context=context)
