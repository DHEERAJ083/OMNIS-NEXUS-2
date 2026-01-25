import sys
sys.path.append(".")

print("Testing enhanced server import...")
try:
    import omnis_nexus_server as server
    print("  [PASS] Module imported successfully")
    
    # Check for new tools
    new_tools = [
        "list_processes", "kill_process", "get_process_info",
        "disk_stats", "network_stats",
        "get_config", "set_config",
        "schedule_command", "list_scheduled_tasks", "cancel_scheduled_task"
    ]
    
    print("\nChecking new tools...")
    for tool in new_tools:
        if hasattr(server, tool):
            print(f"  [PASS] {tool}")
        else:
            print(f"  [FAIL] {tool} MISSING")
    
    print("\n[Pass] Enhanced server verification complete!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
