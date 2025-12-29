import time 
from client import GhostClient

client = GhostClient()

def get_open_windows():
    state = client.get_state()
    if "error" in state:
        return f"Error connecting to GhostShell: {state['error']}"
    
    windows = state.get("windows", {})
    if not windows:
        return "No windows are currently open."
    
    report = []
    for address, win in windows.items():
        report.append(f"- {win['title']} (on Workspace {win['workspace']['Name']})")

    return "\n".join(report)

def launch_app(name):
    cmd = f"dispatch exec {name}"
    return client.send_command(cmd)

def switch_workspace(id):
    cmd = f"dispatch workspace {id}"
    return client.send_command(cmd)

def close_active_window():
    return client.send_command("dispatch killactive")

