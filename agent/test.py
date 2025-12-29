from tools import get_open_windows, launch_app, switch_workspace
import time

print("--- GHOST SHELL AUTOMATION TEST ---")

# 1. See what is open
print("\n[1] Checking current windows...")
print(get_open_windows())

# 2. Switch workspace (Let's go to workspace 3 to keep it clean)
print("\n[2] Switching to Workspace 3...")
switch_workspace(3)
time.sleep(1) # Wait for animation

# 3. Launch an app
print("\n[3] Launching Kitty Terminal...")
launch_app("kitty")

# 4. Verify it worked
time.sleep(2) # Give it time to open
print("\n[4] Re-checking windows...")
print(get_open_windows())

print("\n--- TEST COMPLETE ---")
