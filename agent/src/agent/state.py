from typing import Annotated, TypedDict, Dict, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    windows: Dict[str, Any]
    workspaces: Dict[str, Any]
    last_error: str | None
    iterations: int
