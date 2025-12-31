import logging
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama

from src.core.client import GhostClient
from src.core.preferences import PreferenceManager
from src.agent.state import AgentState
from src.tools import all_tools


llm = ChatOllama(model="rnj-1:8b", temperature=0, num_predict=512)
llm_with_tools = llm.bind_tools(all_tools)
pref_manager = PreferenceManager()

def sync_os_state(state: AgentState):

    client = GhostClient()
    raw_state = client.get_state()
    current_iter = state.get("iterations", 0)
    
    new_state = {
        "windows": raw_state.get("windows", {}),
        "workspaces": raw_state.get("workspaces", {}),
        "last_error": None,
        "iterations": current_iter + 1
    }

    if "error" in raw_state:
            new_state["last_error"] = f"DAEMON_ERROR: {raw_state['error']}"
    
    return new_state

def brain_node(state: AgentState):

    windows = state.get("windows", {})
    if windows:
        win_list = [
            f"- [{w.get('class', 'App')}] {w.get('title', 'Unknown')} "
            f"(ID: {addr}, Workspace: {w.get('workspace', {}).get('Name', '?')})" 
            for addr, w in windows.items()
        ]
        formatted_windows = "\n".join(win_list)
    else:
        formatted_windows = "No active windows found."

    error_context = ""
    if state.get("last_error"):
        error_context = (
            f"<previous_error>\n"
            f"{state['last_error']}\n"
            f"INSTRUCTION: The last operation failed. Analyze the error and try a different approach.\n"
            f"</previous_error>"
        )

    preferences_context = pref_manager.get_system_prompt_addition()

    SYSTEM_PROMPT = (
        "You are GhostShell, an intelligent OS agent on LINUX on Hyprland compositor.\n"
        "Your goal is to execute user commands efficiently using the available tools.\n\n"
        
        f"{preferences_context}\n\n"
       
        "<system_state>\n"
        f"Active Windows:\n{formatted_windows}\n"
        "</system_state>\n\n"
        
        f"{error_context}\n\n"

        "<protocols>\n"
        "1. AMBIGUITY CHECK: If request is vague, ask for clarification.\n"
        "2. ATOMICITY: Perform actions one step at a time.\n"
        "</protocols>"
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}
