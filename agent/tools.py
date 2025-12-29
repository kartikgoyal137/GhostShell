import time 
from client import GhostClient
import subprocess

client = GhostClient()

def send_notification(message: str):
    """
    Sends a visual notification popup to the desktop using Hyprland's notify system.
    Args:
        message: The text to display in the notification.
    """
    cmd = f"dispatch notify 1 10000 'rgb(ff1ea3)' '{message}'"
    return client.send_command(cmd)

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
    Returns the new playback status so the agent knows the action succeeded.
    Args:
        action: 'play', 'pause',  'next', 'previous'
    """
    
    subprocess.run(["playerctl", action])
    
    
    try:
        new_status = subprocess.check_output(["playerctl", "status"], text=True).strip()
        return f"Action '{action}' successful. Current status: {new_status}"
    except:
        return f"Action '{action}' sent, but no active player found."
    

def get_media_info():
    """
    Returns the current player status and metadata (Artist - Title).
    Use this to check if music is already playing before starting it.
    """
    try:
        status = subprocess.check_output(["playerctl", "status"], text=True).strip()
        metadata = subprocess.check_output(
            ["playerctl", "metadata", "--format", "{{ artist }} - {{ title }}"], 
            text=True
        ).strip()
        return f"Status: {status} | Now Playing: {metadata}"
    except:
        return "No media player is currently active."

all_tools = [send_notification, get_open_windows, launch_app, switch_workspace, close_active_window, control_media, get_media_info]

