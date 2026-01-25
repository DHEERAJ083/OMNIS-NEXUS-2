import time

def run_morning_routine(server):
    """
    Morning Routine:
    1. Check Battery
    2. Open essential apps (Browser, Email)
    3. Focus Email
    """
    print("[Automation] Running Morning Routine...")
    try:
        # 1. Check Health
        stats = server.system_stats()
        if isinstance(stats['battery'], dict) and stats['battery']['percent'] < 50 and not stats['battery']['plugged']:
             server.notify_operator("Morning Ritual", "Plug in your laptop! Battery is low.")
        
        # 2. Launch Apps
        # Use generic names that work with 'start' command on Windows
        server.launch_application("chrome") 
        time.sleep(2)
        server.launch_application("outlook") 
        time.sleep(5) # Wait for load
        
        # 3. Focus
        server.focus_window("Outlook")
        
        server.notify_operator("Morning Ritual", "System ready for the day.")
    except Exception as e:
        print(f"[Automation] Morning Routine failed: {e}")
        server.notify_operator("Automation Error", f"Morning routine encountered an error: {e}")

def run_deep_work(server):
    """
    Deep Work Mode:
    1. Set Do Not Disturb (Simulation)
    2. Close distractions
    3. Play Focus Music (e.g. Spotify)
    """
    print("[Automation] Engaging Deep Work Mode...")
    try:
        # 1. Kill Distractions (Case insensitive)
        distractions = ["discord", "steam", "whatsapp", "teams"]
        for d in distractions:
            server.kill_process(d)
            
        # 2. Launch Music
        server.launch_application("spotify")
        
        server.notify_operator("Deep Work", "Distractions eliminated. Focus.")
    except Exception as e:
        print(f"[Automation] Deep Work failed: {e}")
        server.notify_operator("Automation Error", f"Deep Work routine encountered an error: {e}")
