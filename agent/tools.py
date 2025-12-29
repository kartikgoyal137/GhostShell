import time 
from client import GhostClient

client = GhostClient()

def get_open_windows():
    """
    Fetches the current list of all open windows and their workspace IDs.
    Returns a formatted string listing window titles and locations.
    Use this to see what is currently on the screen.
    """
    state = client.get_state()
    if "error" in state:
        return f"Error connecting to GhostShell: {state['error']}"
    
    windows = state.get("windows", {})
    if not windows:
        return "No windows are currently open."
    
    report = []
    for address, win in windows.items():
        workspace_name = win.get('workspace', {}).get('Name', 'Unknown')
        title = win.get('title', 'Unknown Title')
        report.append(f"- {title} (on Workspace {workspace_name})")

    return "\n".join(report)

def launch_app(name: str):
    """
    Launches a new application on the current workspace.
    Args:
        name: The name of the executable (e.g., 'firefox', 'kitty', 'spotify').
    """
    cmd = f"dispatch exec {name}"
    return client.send_command(cmd)

def switch_workspace(id: int):
    """
    Switches the active monitor to a specific workspace number.
    Args:
        id: The integer ID of the workspace (e.g., 1, 2, 9).
    """
    cmd = f"dispatch workspace {id}"
    return client.send_command(cmd)

def close_active_window():
    """
    Closes the window that currently has focus. 
    Use this to close the active application.
    """
    return client.send_command("dispatch killactive")

def control_media(action: str):
    """
    Controls media playback.
    Args:
        action: One of 'play', 'pause', 'next', 'previous', 'stop'.
    """
    valid_actions = ['play', 'pause', 'next', 'previous', 'stop']
    if action not in valid_actions:
        return f"Invalid action. Use: {valid_actions}"
    
    cmd = f"playerctl {action}"
    return client.send_command(cmd)
