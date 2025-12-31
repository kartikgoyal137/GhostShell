import subprocess
from src.core.client import GhostClient

client = GhostClient()

IPC_NOISE_PATTERNS = [
    "Hyprland IPC didn't respond in time",
    "Couldn't read (6)",
    "Resource temporarily unavailable"
]

def _validate_ipc(result: dict) -> tuple[bool, str]:
    output = result.get('shell_output', result.get('output', '')).strip()
    
    if any(pattern in output for pattern in IPC_NOISE_PATTERNS):
        return True, output

    if "error" in result and "shell_output" not in result:
        return False, result['error']

    if "error" in result:
        return False, output

    return True, output

def get_open_windows():
    """
    Retrieves a list of all currently open windows across all workspaces.
    Returns a formatted string containing window titles, IDs, and workspace locations.
    Use this to verify window states or find the ID of a specific application.
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
        app_class = win.get('class', 'Unknown App')
        report.append(f"- {title} (on Workspace {workspace_name})")

    return "\n".join(report)

def launch_app(name: str):
    """
    Launches a specified application on the current active workspace.
    
    Args:
        name (str): The binary name of the application to launch (e.g., 'firefox', 'code', 'kitty').
    """
    cmd = f"dispatch exec {name}"
    result = client.send_command(cmd)
    
    success, output = _validate_ipc(result)
    if not success:
        return f"Failed to launch '{name}'. Error: {output}"
    
    return f"Launched '{name}' successfully."

def switch_workspace(id: int):
    """
    Switches the active view to the specified workspace ID.
    
    Args:
        id (int): The target workspace number (e.g., 1, 2, 10).
    """
    cmd = f"dispatch workspace {id}"
    result = client.send_command(cmd)
    
    success, output = _validate_ipc(result)
    if not success:
        return f"Failed to switch to workspace {id}. Error: {output}"
        
    return f"Switched to workspace {id}"

def close_active_window():
    """
    Closes the window that currently holds focus on the active workspace.
    Equivalent to pressing Alt+F4 or the window close button.
    """
    result = client.send_command("dispatch killactive")
    
    success, output = _validate_ipc(result)
    if not success:
        return f"Failed to close window. Error: {output}"
        
    return "Active window closed."

def control_media(action: str):
    """
    Controls the system-wide media player (Spotify, VLC, Browser, etc.).
    
    Args:
        action (str): The command to execute. Must be one of: 'play', 'pause', 'next', 'previous'.
    """
    try:
        subprocess.run(["playerctl", action], check=False)
        new_status = subprocess.check_output(["playerctl", "status"], text=True).strip()
        return f"Action '{action}' successful. Current status: {new_status}"
    except Exception as e:
        return f"Action '{action}' sent, but failed or no player found. Error: {str(e)}"

def get_media_info():
    """
    Retrieves metadata about the currently playing media.
    Returns a string with the playback status (Playing/Paused) and the 'Artist - Title' format.
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

all_tools = [get_open_windows, launch_app, switch_workspace, close_active_window, control_media, get_media_info]
