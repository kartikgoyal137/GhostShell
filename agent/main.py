import os
from client import GhostClient
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from tools import all_tools
from langchain_ollama import ChatOllama
load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    windows: dict
    workspaces: dict
    last_error: str | None
    iterations: int

#llm = ChatOllama(model="functiongemma", temperature=0)
#llm = ChatOllama(model="llama3.2", temperature=0)
llm = ChatOllama(model="gpt-oss:20b", temperature=0, num_predict=256)
llm_with_tools = llm.bind_tools(all_tools)

def sync_os_state(state: AgentState):
    client = GhostClient()
    raw_state = client.get_state()
    current_iter = state.get("iterations", 0)
    if "error" in raw_state:
        return {"last_error": raw_state["error"]}
    
    return {
        "windows": raw_state.get("windows", {}),
        "workspaces": raw_state.get("workspaces", {}),
        "last_error": None,
        "iterations": current_iter+1
    }

def brain_node(state: AgentState):
    BASE_PROTOCOL = (
    "## IDENTITY\n"
    "You are GHOST_SHELL, a low-level Linux kernel-agent. You operate the Hyprland compositor.\n\n"
    
    "## CORE DIRECTIVES\n"
    "1. EXECUTION OVER CONVERSATION: Never explain what you are doing. Move immediately to tool calls.\n"
    "2. ATOMICITY: Breakdown complex requests into sequential tool calls.\n"
    "3. STATE AWARENESS: Use the 'CURRENT_SYSTEM_STATE' provided to identify window addresses (e.g., 0x55d...) before acting.\n"
    "4. ERROR RECOVERY: If a tool returns an error, do not apologize. Use 'get_open_windows' to re-sync or try an alternative approach.\n\n"
    
    "## SYNTAX CONSTRAINTS\n"
    "- If a task is complete and no more tools are needed, output 'TERMINATE'.\n"
    "- If the request is impossible with current tools, output 'INSUFFICIENT_TOOLS'.\n"
   
    
    "## HANDLING AMBIGUITY\n"
    "If the user says 'Close the browser' and multiple browsers are open, close the one that was most recently active (check state) or close all of them    ." )

    win_list = [f"{w['title']} (addr: {addr})" for addr, w in state["windows"].items()]
    os_context = f"ACTIVE_WINDOWS: {', '.join(win_list) if win_list else 'None'}\n"
    os_context += f"WORKSPACES: {state['workspaces']}"

    system_message = SystemMessage(content=f"{BASE_PROTOCOL}\n\nCURRENT_SYSTEM_STATE:\n{os_context}")
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}

 
tool_node = ToolNode(all_tools)

def should_continue(state: AgentState):
    if state.get("iterations", 0) > 8:
        print("!! MAX_ITERATIONS_REACHED: Terminating loop for safety.")
        return END

    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    
    return END

builder = StateGraph(AgentState)

builder.add_node("sync", sync_os_state)
builder.add_node("agent", brain_node)
builder.add_node("tools", tool_node)

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

ghost_shell = builder.compile()


print("--- GHOST SHELL ---")

while True:
    user_input = input("\n> ")
    if user_input.lower() in ["quit", "exit"]:
        break
    
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    for event in ghost_shell.stream(initial_state):
        
        for key, value in event.items():
            print(f"\n[Node: {key}]") 
            if "messages" in value:
                msg = value["messages"][-1]
                if hasattr(msg, "content") and msg.content:
                    print(f"AI: {msg.content}")
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"Action: {msg.tool_calls[0]['name']}")
