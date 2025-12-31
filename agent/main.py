import sys
import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agent.graph import build_graph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GhostShell")

def main():
    load_dotenv()
    
    logger.info("Initializing Ghost Shell...")
    
    try:
        ghost_shell = build_graph()
    except Exception as e:
        logger.critical(f"Failed to compile agent graph: {e}")
        sys.exit(1)
    
    print("\n GHOST SHELL ")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit"]:
                logger.info("Shutting down...")
                break

            initial_state = {
                "messages": [HumanMessage(content=f"User Request: {user_input}")],
                "windows": {},
                "workspaces": {},
                "last_error": None,
                "iterations": 0
            }

            logger.info(f"Processing request: {user_input}")
            
            for event in ghost_shell.stream(initial_state):
                for node_name, node_state in event.items():
                    if node_name == "agent":
                        last_msg = node_state["messages"][-1]
                        
                        if last_msg.tool_calls:
                            for tc in last_msg.tool_calls:
                                print(f"  [ACTION] {tc['name']} args={tc['args']}")
                        elif last_msg.content:
                            print(f"  [AI] {last_msg.content}")

                    if node_name == "tools":
                        last_msg = node_state["messages"][-1]
                        logger.debug(f"Tool Output: {last_msg.content}")
                        print(f"  [SYSTEM] {last_msg.content}")

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break
        except Exception as e:
            logger.error(f"Runtime Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
