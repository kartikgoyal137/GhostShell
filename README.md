# Agentic desktop workflow orchestrator for Hyprland
## GhostShell is an intelligent assistant designed to automate and manage your Hyprland desktop environment. It uses a LangGraph-based Python agent to make decisions and a Go-based daemon to communicate directly with your OS via Unix sockets.

### Prerequisites
- Linux with **Hyprland**
- Go (>= 1.20)
- Python (>= 3.10)
- Ollama installed

### Run
```bash
go run main.go
python3 main.py
```
---

## Architecture
- **Go Backend**
  - Interfaces directly with Hyprland IPC
  - Maintains live window/workspace state
  - Exposes system actions via an internal API

- **Python Agent**
  - Performs reasoning and task planning
  - Converts user intent into executable system actions
  - Supports iterative correction and re-planning

