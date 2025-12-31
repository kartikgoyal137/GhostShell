import subprocess
from src.core.client import GhostClient
import os
from duckduckgo_search import DDGS

client = GhostClient()

IPC_NOISE_PATTERNS = [
    "Hyprland IPC didn't respond in time",
    "Couldn't read (6)",
    "Resource temporarily unavailable"
]


def web_search(query: str):
    """
    Performs a web search using DuckDuckGo and returns the top 5 results.
    Args:
        query (str): The search term (e.g., 'python install poetry', 'weather in Tokyo').
    """
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        
        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")
            
        return "\n".join(formatted)
    except Exception as e:
        return f"Search failed: {e}"

def list_files(directory: str = "."):
    """
    Lists files and directories in the specified path.
    host username is 'kartik'
    Args:
        directory (str): The path to list. Defaults to current directory.
    """
    try:
        files = os.listdir(directory)
        return f"Contents of {directory}:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing directory: {e}"

def read_file(filepath: str):
    """
    Reads the contents of a specific file.
    Args:
        filepath (str): The full path to the file.
    """
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

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
        report.append(f"- [ID: {address}] {title} (on Workspace {workspace_name})")
 
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

def close_window(address: str):
    """
    Fetch the list of open windows and find the address of the window which the user has asked to close. Then call this function with that address
    """
    result = client.send_command(f"dispatch closewindow address:{address}")
    
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

def move_window_to_workspace(address: str, workspace_id: int):
    """
    Moves a specific open window to a target workspace.
    Args:
        address (str): The window ID/Address (get this from get_open_windows).
        workspace_id (int): The target workspace number.
    """
    cmd = f"dispatch movetoworkspacesilent {workspace_id},address:{address}"
    result = client.send_command(cmd)
    
    success, output = _validate_ipc(result)
    if not success:
        return f"Failed to move window. Error: {output}"
    
    return f"Moved window {address} to workspace {workspace_id}."

def pin_window(address: str = None):
    """
    Pins a window (floats it and makes it visible on ALL workspaces).
    fetch the address of the window asked by the user and pass it to this function.
    Args:
        address (str):  window address.
    """
    target = f"address:{address}" if address else "activewindow"
    client.send_command(f"dispatch setfloating {target}") 
    cmd = f"dispatch pin {target}"
    result = client.send_command(cmd)
    
    success, output = _validate_ipc(result)
    return "Window pinned (visible on all workspaces)." if success else f"Failed: {output}"

all_tools = [get_open_windows, launch_app, switch_workspace, close_window, control_media, get_media_info, list_files, read_file, web_search, move_window_to_workspace, pin_window]
