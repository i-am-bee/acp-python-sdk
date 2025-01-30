"""Resource template functionality."""

import inspect
import re
from typing import Any, Callable

from pydantic import BaseModel, Field, TypeAdapter, validate_call

from mcp.server.fastmcp.resources.types import FunctionResource, Resource


class AgentTemplate(BaseModel):
    """A template for creating agents."""

    name: str = Field(description="Name of the agent")
    description: str | None = Field(description="Description of what the agent does")
    fn: Callable = Field(exclude=True)
    parameters: dict = Field(description="JSON schema for function parameters")

    @classmethod
    def from_function(
        cls,
        fn: Callable,
        name: str | None = None,
        description: str | None = None,
    ) -> "AgentTemplate":
        """Create a template from a function."""
        func_name = name or fn.__name__
        if func_name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")

        # Get schema from TypeAdapter - will fail if function isn't properly typed
        parameters = TypeAdapter(fn).json_schema()

        # ensure the arguments are properly cast
        fn = validate_call(fn)

        return cls(
            name=func_name,
            description=description or fn.__doc__ or "",
            fn=fn,
            parameters=parameters,
        )

    async def create_agent(self, uri: str, params: dict[str, Any]) -> Resource:
        """Create a resource from the template with the given parameters."""
        try:
            # Call function and check if result is a coroutine
            result = self.fn(**params)
            if inspect.iscoroutine(result):
                result = await result

            return FunctionResource(
                uri=uri,  # type: ignore
                name=self.name,
                description=self.description,
                fn=lambda: result,  # Capture result in closure
            )
        except Exception as e:
            raise ValueError(f"Error creating resource from template: {e}")
