import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from tools import get_open_windows, launch_app, switch_workspace, close_active_window, control_media
from langchain_community.chat_models import ChatOllama
load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

tools = [get_open_windows, launch_app, switch_workspace, close_active_window, control_media]
llm = ChatOllama(model="llama3", temperature=0)
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def brain_node(state: AgentState):
    system_prompt = SystemMessage(content=(
        "You are Ghost Shell, an advanced AI Desktop Orchestrator. "
        "Your goal is to help the user manage their Linux workspace efficiently. "
        "You have control over windows and workspaces via the provided tools. "
        "Always check the state (get_open_windows) before moving things. "
        "If a user asks for a workflow, break it down into steps."
    ))
    
    messages = state["messages"]
    full_conversation = [system_prompt] + messages
    response = llm_with_tools.invoke(full_conversation)

    return {"messages": [response]}

 
tool_node = ToolNode(tools)

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    
    return END

builder = StateGraph(AgentState)

builder.add_node("agent", brain_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",  
        END: END           
    }
)

builder.add_edge("tools", "agent")

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
