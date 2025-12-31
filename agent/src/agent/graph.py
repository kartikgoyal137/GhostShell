from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from src.agent.state import AgentState
from src.agent.nodes import sync_os_state, brain_node
from src.tools import all_tools

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    if state.get("iterations", 0) > 10:
        return END

    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        return "tools"
    
    return END

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("sync", sync_os_state)
    builder.add_node("agent", brain_node)
    builder.add_node("tools", ToolNode(all_tools))

    builder.add_edge(START, "sync")
    builder.add_edge("sync", "agent")

    builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  
            END: END           
        }
    )

    builder.add_edge("tools", "sync")
    memory = MemorySaver()

    return builder.compile(checkpointer=memory)
