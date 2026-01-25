import sys
import os
import inspect

# Add current directory to path so we can import the server
sys.path.append(os.getcwd())

try:
    print("Attempting to import omnis_nexus_server...")
    import omnis_nexus_server
    print("Successfully imported omnis_nexus_server.")
except ImportError as e:
    print(f"FAILED to import omnis_nexus_server: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR during import: {e}")
    sys.exit(1)

# Check for expected tools
expected_tools = [
    "system_stats",
    "run_command",
    "list_directory",
    "read_file",
    "write_file",
    "get_clipboard",
    "set_clipboard",
    "launch_application",
    "ui_click_element",
    "ui_type_string",
    "list_windows",
    "focus_window",
    "visual_search_click",
    "capture_screen",
    "capture_region",
    "locate_and_click",
    "start_visual_watch",
    "start_log_watch",
    "start_hardware_watch",
    "stop_monitor",
    "notify_operator"
]

print("\nVerifying registered tools...")
# In FastMCP, tools are decorated functions. We can check if the functions exist in the module.
# (Accessing internal mcp registry might differ based on version, so checking module attributes is safer for now)

missing_tools = []
for tool in expected_tools:
    if hasattr(omnis_nexus_server, tool):
        print(f"  [OK] {tool}")
    elif hasattr(omnis_nexus_server.mcp, "_tools") and tool in [t.name for t in omnis_nexus_server.mcp._tools]:
         # Fallback: check if it's in the FastMCP object's tool registry directly if not exposed as function
         print(f"  [OK] {tool} (found in registry)")
    else:
        # Note: If decorators wrap functions, they should still appear in the module or registry.
        # Let's check the module's functions.
        found = False
        for name, obj in inspect.getmembers(omnis_nexus_server):
            if name == tool:
                print(f"  [OK] {tool}")
                found = True
                break
        if not found:
            print(f"  [MISSING] {tool}")
            missing_tools.append(tool)

if missing_tools:
    print(f"\nFAILED: Missing tools: {missing_tools}")
    sys.exit(1)
else:
    print("\nALL TOOLS VERIFIED.")

# Check dependencies
print("\nChecking critical dependencies...")
try:
    import fastmcp
    import psutil
    import pyperclip
    import pyautogui
    import cv2 # opencv-python
    import PIL # Pillow
    import plyer
    print("  [OK] All modules importable.")
except ImportError as e:
    print(f"  [FAILED] Missing dependency: {e}")
    sys.exit(1)

print("\nVERIFICATION SUCCESS: Build is complete and integrity checked.")
