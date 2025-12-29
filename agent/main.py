import os
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

#llm = ChatOllama(model="functiongemma", temperature=0)
#llm = ChatOllama(model="llama3.2", temperature=0)
llm = ChatOllama(model="llama3-groq-tool-use", temperature=0, num_predict=256)
llm_with_tools = llm.bind_tools(all_tools)

def brain_node(state: AgentState):
    system_prompt = SystemMessage(content=(
        "## ROLE\n"
    "You are GHOST_SHELL, a low-level Linux OS kernel-agent. You interface directly with the Hyprland Wayland compositor.\n\n"
    
    "## OPERATIONAL PROTOCOL\n"
    "1. INTERPRET user intent into a sequence of atomic tool calls.\n"
    "2. EXECUTE tools immediately. Do not ask for permission.\n"
    "3. ZERO CONVERSATION. Do not greet, do not explain, and do not summarize your plan.\n"
    "4. FORMAT: Output ONLY the tool-call triggers. If multiple steps are needed, emit multiple tool calls in a single turn.\n"
    "5. FEEDBACK: If a tool returns an error, immediately attempt a corrective tool call (e.g., if a window is not found, run 'get_open_windows' to refresh state).\n\n"
    
    "## CONSTRAINTS\n"
    "- Never output Markdown blocks like ```json unless the system failed to trigger the tool.\n"
    "- If no tool is relevant, state 'INSUFFICIENT_TOOLS' and nothing else.\n"
    "- You are an engine, not a chatbot."
    ))
    
    messages = state["messages"]
    full_conversation = [system_prompt] + messages
    response = llm_with_tools.invoke(full_conversation)

    return {"messages": [response]}

 
tool_node = ToolNode(all_tools)

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
