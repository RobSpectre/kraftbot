"""
Pydantic models for KraftBot agent data structures.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel, Field


@dataclass
class AgentDependencies:
    """Dependencies for the agent - can include database connections, API clients, etc."""

    user_id: str
    session_id: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AgentResponse(BaseModel):
    """Simplified response from the agent - let Logfire handle all observability"""

    response: str = Field(description="The main response to the user")
