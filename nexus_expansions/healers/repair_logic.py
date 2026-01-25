def handle_battery_critical(server, percent):
    """
    Healer: Low Battery
    Action: Notify and kill high resource, non-essential apps if possible.
    """
    print(f"[Healer] Handling Critical Battery ({percent}%)")
    
    # 1. Immediate Notification
    server.notify_operator("SENTINEL HEALER", f"Battery Critical ({percent}%). Connecting to emergency power recommended.")
    
    # 2. Conservation (Mock - in real system, disable visual effects, lower brightness)
    # server.run_command("powercfg /setactive SCHEME_MAX") # Windows Power Saver

def handle_high_cpu_process(server, process_name, pid):
    """
    Healer: Runaway Process
    Action: Restart the process.
    """
    print(f"[Healer] Detected runaway process: {process_name} (PID: {pid})")
    
    # 1. Attempt graceful termination
    server.kill_process(pid)
    
    # 2. Wait and Restart
    # server.launch_application(process_name) 
    server.notify_operator("SENTINEL HEALER", f"Restarted stuck process: {process_name}")

HEALER_MAP = {
    "battery_critical": handle_battery_critical,
    "high_cpu": handle_high_cpu_process
}
