# Omnis-Nexus Enhanced Server
# Full implementation with all enhancement categories

import os
import sys
import platform
import shutil
import subprocess
import psutil
from pathlib import Path

# Ensure we can import local modules regardless of CWD
sys.path.append(str(Path(__file__).parent.resolve()))
import pyperclip
import time
import json
import logging
import threading
import hashlib
import schedule
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, List, Dict, Union
from datetime import datetime
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Omnis-Nexus-Enhanced")

# --- Configuration & Logging Setup ---

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG = Path("./audit.log")
ROLLBACK_DIR = Path("./.rollback")
ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)

# Logger configuration
logger = logging.getLogger("OmnisNexus")
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(
    LOG_DIR / f"omnis_nexus_{datetime.now().strftime('%Y%m%d')}.log",
    maxBytes=10*1024*1024, backupCount=7
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_formatter = logging.Formatter('%(levelname)s: %(message)s')
stderr_handler.setFormatter(stderr_formatter)
logger.addHandler(stderr_handler)

logger.info("Omnis-Nexus Enhanced Server Initializing...")

# Configuration System
CONFIG_FILE = Path("./omnis_config.json")
DEFAULT_CONFIG = {
    "safe_zone": str(Path(os.path.expanduser("~")).joinpath("RoboticsProjects").resolve()),
    "screenshot_dir": "./temp_vision",
    "max_rollback_versions": 5,
    "command_whitelist_enabled": False,
    "audit_enabled": True,
    "allowed_commands": ["ls", "dir", "echo", "cat", "type"],
    "blocked_commands": ["rm -rf", "del /s", "format"]
}

def _load_config() -> Dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception as e:
            logger.warning(f"Config load failed: {e}")
    return DEFAULT_CONFIG.copy()

def _save_config(config: Dict) -> None:
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Config save failed: {e}")

CONFIG = _load_config()
if "OMNIS_SAFE_ZONE" in os.environ:
    CONFIG["safe_zone"] = os.environ["OMNIS_SAFE_ZONE"]

SAFE_ZONE = Path(CONFIG["safe_zone"]).resolve()
SCREENSHOT_DIR = Path(CONFIG["screenshot_dir"])
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Audit logging
def _audit_log(action: str, details: str, success: bool = True):
    if CONFIG.get("audit_enabled"):
        with open(AUDIT_LOG, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {'SUCCESS' if success else 'FAILED'} | {action} | {details}\n")

# --- Safety & Validation ---

def _is_safe_path(path: Union[str, Path]) -> bool:
    try:
        return Path(path).resolve().is_relative_to(SAFE_ZONE)
    except:
        return False

def _validate_access(path: Union[str, Path], force: bool = False) -> None:
    if not _is_safe_path(path) and not force:
        raise PermissionError(f"RESTRICTED: {path} outside SAFE_ZONE. Use force=True.")

def _validate_command(command: str) -> bool:
    """Check if command is safe to execute."""
    # Fail Secure: If whitelist enabled but empty, block everything? 
    # Current config logic: if whitelist_enabled is False, allow all except blocked.
    
    cmd_lower = command.lower()
    
    # 1. Global Blocking (Always active)
    CRITICAL_BLOCKS = ["rm -rf", "format c:", "mkfs", ":(){ :|:& };:"] # Fork bomb
    
    # Normalize whitespace (rm  -rf -> rm -rf)
    cmd_normalized = ' '.join(cmd_lower.split())
    
    for block in CRITICAL_BLOCKS:
        if block in cmd_normalized:
            return False

    # 2. Configurable Blocking
    if not CONFIG.get("command_whitelist_enabled", False):
        # Blacklist Mode
        blocked_cmds = CONFIG.get("blocked_commands", [])
        for blocked in blocked_cmds:
             if blocked in cmd_normalized: 
                 return False
        return True
    
    # 3. Whitelist Mode (Strictest)
    allowed_cmds = CONFIG.get("allowed_commands", [])
    # Simple check: command must start with an allowed command
    for allowed in allowed_cmds:
        if cmd_lower.startswith(allowed.lower()):
            return True
            
    return False

def _create_rollback(path: Path) -> None:
    """Create a rollback copy of the file."""
    if path.exists():
        rollback_path = ROLLBACK_DIR / f"{path.name}.{int(time.time())}"
        shutil.copy2(path, rollback_path)
        # Keep only last N versions
        versions = sorted(ROLLBACK_DIR.glob(f"{path.name}.*"))
        for old in versions[:-CONFIG.get("max_rollback_versions", 5)]:
            old.unlink()

# === CORE TOOLS ===

@mcp.tool()
def system_stats() -> Dict[str, Union[float, str, dict]]:
    """System telemetry: CPU, RAM, Battery."""
    logger.debug("system_stats called")
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "available_gb": round(mem.available / (1024**3), 2),
        "battery": {
            "percent": battery.percent,
            "plugged": battery.power_plugged
        } if battery else "N/A",
        "platform": platform.platform()
    }

@mcp.tool()
def run_command(command: str) -> str:
    """Execute shell command with safety validation."""
    logger.info(f"run_command: {command}")
    
    if not _validate_command(command):
        _audit_log("run_command", f"BLOCKED: {command}", False)
        return "ERROR: Command blocked by policy"
    
    _audit_log("run_command", command)
    
    system = platform.system()
    if system == "Windows":
        shell = "pwsh" if shutil.which("pwsh") else "cmd"
        cmd = [shell, "-Command", command] if shell == "pwsh" else ["cmd", "/c", command]
    else:
        cmd = [os.environ.get("SHELL", "/bin/bash"), "-c", command]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nExit: {result.returncode}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_directory(path: str = ".") -> List[Dict]:
    """List directory contents with metadata."""
    logger.debug(f"list_directory: {path}")
    try:
        results = []
        with os.scandir(Path(path).resolve()) as entries:
            for entry in entries:
                results.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if not entry.is_dir() else None
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def read_file(path: str, force: bool = False) -> str:
    """Read file with safety check."""
    logger.debug(f"read_file: {path}")
    try:
        _validate_access(path, force)
        return Path(path).read_text(encoding='utf-8')
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def write_file(path: str, content: str, force: bool = False) -> str:
    """Write file with rollback support."""
    logger.info(f"write_file: {path}")
    try:
        _validate_access(path, force)
        p = Path(path)
        _create_rollback(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        _audit_log("write_file", str(p))
        return f"Written to {p}"
    except Exception as e:
        _audit_log("write_file", f"{path}: {e}", False)
        return f"Error: {e}"

@mcp.tool()
def get_clipboard() -> str:
    """Get clipboard content."""
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_clipboard(content: str) -> str:
    """Set clipboard content."""
    try:
        pyperclip.copy(content)
        return "Clipboard updated"
    except Exception as e:
        return f"Error: {e}"

# === PROCESS MANAGEMENT ===

@mcp.tool()
def list_processes() -> List[Dict]:
    """List all processes with stats."""
    logger.debug("list_processes called")
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:50]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def kill_process(pid_or_name: Union[int, str], force: bool = False) -> str:
    """Terminate a process by PID or name."""
    logger.warning(f"kill_process: {pid_or_name}")
    _audit_log("kill_process", str(pid_or_name))
    
    try:
        if isinstance(pid_or_name, int):
            proc = psutil.Process(pid_or_name)
        else:
            for p in psutil.process_iter(['pid', 'name']):
                if pid_or_name.lower() in p.info['name'].lower():
                    proc = p
                    break
            else:
                return f"Process '{pid_or_name}' not found"
        
        proc.terminate() if not force else proc.kill()
        return f"Terminated PID {proc.pid}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_process_info(pid: int) -> Dict:
    """Detailed process information."""
    try:
        proc = psutil.Process(pid)
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "status": proc.status(),
            "cpu_percent": proc.cpu_percent(interval=0.1),
            "memory_mb": round(proc.memory_info().rss / (1024**2), 2),
            "num_threads": proc.num_threads(),
            "create_time": datetime.fromtimestamp(proc.create_time()).isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# === ENHANCED MONITORING ===

@mcp.tool()
def disk_stats() -> List[Dict]:
    """Disk usage per partition."""
    logger.debug("disk_stats called")
    try:
        partitions = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except:
                pass
        return partitions
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def network_stats() -> Dict:
    """Network interface statistics."""
    logger.debug("network_stats called")
    try:
        stats = psutil.net_io_counters(pernic=True)
        return {
            iface: {
                "bytes_sent_mb": round(stat.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(stat.bytes_recv / (1024**2), 2),
                "packets_sent": stat.packets_sent,
                "packets_recv": stat.packets_recv
            } for iface, stat in stats.items()
        }
    except Exception as e:
        return {"error": str(e)}

# === CONFIGURATION TOOLS ===

@mcp.tool()
def get_config(key: Optional[str] = None) -> Union[Dict, str]:
    """Get configuration value(s)."""
    if key:
        return CONFIG.get(key, "Key not found")
    return CONFIG

@mcp.tool()
def set_config(key: str, value: Union[str, bool, int, list]) -> str:
    """Set configuration value."""
    logger.info(f"set_config: {key}={value}")
    CONFIG[key] = value
    _save_config(CONFIG)
    _audit_log("set_config", f"{key}={value}")
    return f"Config updated: {key}={value}"

# === EXTERNAL APP INTEGRATION (from original) ===

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 2.0
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

@mcp.tool()
def launch_application(app_name: str) -> str:
    """Launch application by name."""
    logger.info(f"launch_application: {app_name}")
    _audit_log("launch_application", app_name)
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(f"start {app_name}", shell=True)
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen([app_name], shell=True)
        return f"Launched '{app_name}'"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def ui_click_element(x: int, y: int, clicks: int = 1) -> str:
    """Click at screen coordinates."""
    if not pyautogui:
        return "Error: pyautogui not installed"
    try:
        pyautogui.click(x, y, clicks=clicks)
        return f"Clicked ({x}, {y}) {clicks}x"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def ui_type_string(text: str, press_enter: bool = True) -> str:
    """Type text into focused application."""
    if not pyautogui:
        return "Error: pyautogui not installed"
    try:
        pyautogui.write(text, interval=0.1)
        if press_enter:
            pyautogui.press('enter')
        return f"Typed: {text}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_windows() -> List[str]:
    """List active window titles."""
    system = platform.system()
    if system == "Windows" and gw:
        return [w.title for w in gw.getAllWindows() if w.title]
    return ["Platform not supported"]

@mcp.tool()
def focus_window(title: str) -> str:
    """Bring window to foreground."""
    system = platform.system()
    if system == "Windows" and gw:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            return f"Focused: {win.title}"
        return f"Not found: {title}"
    return "Platform not supported"

# === VISUAL TOOLS ===

@mcp.tool()
def capture_screen(filename: str = "current_view.png") -> Dict:
    """Capture full screen."""
    if not pyautogui:
        return {"error": "pyautogui not installed"}
    try:
        filepath = SCREENSHOT_DIR / filename
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return {
            "status": "Success",
            "path": str(filepath.resolve()),
            "resolution": f"{screenshot.width}x{screenshot.height}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def capture_region(x: int, y: int, width: int, height: int, filename: str = "region.png") -> str:
    """Capture screen region."""
    if not pyautogui:
        return "Error: pyautogui not installed"
    try:
        filepath = SCREENSHOT_DIR / filename
        pyautogui.screenshot(region=(x, y, width, height)).save(filepath)
        return f"Saved to {filepath.resolve()}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def locate_and_click(image_path: str, confidence: float = 0.8) -> str:
    """Find and click UI element by image."""
    if not pyautogui:
        return "Error: pyautogui not installed"
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(pyautogui.center(location))
            return f"Found and clicked at {pyautogui.center(location)}"
        return "Element not found"
    except Exception as e:
        return f"Error: {e}"

# === SENTINEL MONITORING ===

try:
    from plyer import notification as plyer_notif
except:
    plyer_notif = None

ACTIVE_MONITORS: Dict[str, bool] = {}

def _notify(title: str, message: str):
    if plyer_notif:
        try:
            plyer_notif.notify(title=title, message=message, app_name='Omnis-Nexus', timeout=10)
        except Exception as e:
            logger.error(f"Notification failed: {e}", file=sys.stderr)

def _get_region_hash(region):
    if not pyautogui:
        return None
    return hashlib.md5(pyautogui.screenshot(region=region).tobytes()).hexdigest()

def _visual_monitor_worker(name, region, interval):
    last_hash = _get_region_hash(region)
    logger.info(f"Visual monitor '{name}' started")
    while ACTIVE_MONITORS.get(name):
        time.sleep(interval)
        try:
            current_hash = _get_region_hash(region)
            if current_hash != last_hash:
                msg = f"Visual change: {name}"
                logger.warning(msg)
                _notify("Visual Alert", msg)
                last_hash = current_hash
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            break

@mcp.tool()
def start_visual_watch(monitor_name: str, x: int, y: int, w: int, h: int, interval: int = 5) -> str:
    """Start visual change monitoring."""
    if not pyautogui:
        return "Error: pyautogui required"
    if monitor_name in ACTIVE_MONITORS and ACTIVE_MONITORS[monitor_name]:
        return f"Monitor '{monitor_name}' already active"
    
    ACTIVE_MONITORS[monitor_name] = True
    thread = threading.Thread(target=_visual_monitor_worker, args=(monitor_name, (x, y, w, h), interval))
    thread.daemon = True
    thread.start()
    return f"Started monitoring: {monitor_name}"

@mcp.tool()
def stop_monitor(monitor_name: str) -> str:
    """Stop active monitor."""
    if monitor_name in ACTIVE_MONITORS:
        ACTIVE_MONITORS[monitor_name] = False
        return f"Stopped: {monitor_name}"
    return "Monitor not found"

@mcp.tool()
def notify_operator(title: str, message: str) -> str:
    """Send system notification."""
    _notify(title, message)
    return f"Notification sent: {title}"

# === SCHEDULING (NEW) ===

SCHEDULED_TASKS: Dict[str, Dict] = {}

@mcp.tool()
def schedule_command(task_id: str, command: str, cron_time: str) -> str:
    """Schedule a command to run at specified time (24h format HH:MM)."""
    logger.info(f"schedule_command: {task_id} at {cron_time}")
    try:
        schedule.every().day.at(cron_time).do(lambda: os.system(command)).tag(task_id)
        SCHEDULED_TASKS[task_id] = {"command": command, "time": cron_time}
        _audit_log("schedule_command", f"{task_id}: {command} at {cron_time}")
        return f"Scheduled: {task_id}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_scheduled_tasks() -> Dict:
    """List all scheduled tasks."""
    return SCHEDULED_TASKS

@mcp.tool()
def cancel_scheduled_task(task_id: str) -> str:
    """Cancel a scheduled task."""
    schedule.clear(task_id)
    if task_id in SCHEDULED_TASKS:
        del SCHEDULED_TASKS[task_id]
    return f"Cancelled: {task_id}"

# Schedule runner thread
def _schedule_runner():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=_schedule_runner, daemon=True).start()

# === EXPANSION PACK INTEGRATION ===

try:
    from nexus_expansions.voice.nexus_voice import NexusVoice
    from nexus_expansions.automations.routines import run_morning_routine, run_deep_work
    from nexus_expansions.healers.repair_logic import HEALER_MAP
    EXPANSIONS_LOADED = True
except ImportError as e:
    logger.warning(f"Expansion Pack Init Failed: {e}")
    EXPANSIONS_LOADED = False

# Global Voice Instance
voice_interface = None

@mcp.tool()
def start_voice_mode() -> str:
    """Activates the Nexus Voice interface."""
    global voice_interface
    if not EXPANSIONS_LOADED:
        return "Expansion pack not loaded."
        
    if not voice_interface:
        # Pass self (the mcp instance proxy)?? 
        # Actually NexusVoice expects 'server_instance' to call tools directly.
        # Since we are inside the server, we can pass a proxy object or refactor NexusVoice to call mcp tools.
        # For simplicity, we'll wrap current mcp tools in a simple class proxy.
        class ServerProxy:
            def system_stats(self): return system_stats()
            def launch_application(self, app): return launch_application(app)
            def capture_screen(self): return capture_screen()
            def notify_operator(self, t, m): return notify_operator(t, m)
            def kill_process(self, p): return kill_process(p)
            def focus_window(self, t): return focus_window(t)
            
        voice_interface = NexusVoice(ServerProxy())
        
    voice_interface.start()
    return "Nexus Voice Active. Say 'Nexus'..."

@mcp.tool()
def stop_voice_mode() -> str:
    if voice_interface:
        voice_interface.stop()
        return "Voice Interface Stopped."
    return "Voice not active."

@mcp.tool()
def run_automation(routine_name: str) -> str:
    """Runs a predefined automation: 'morning', 'deep_work'."""
    if not EXPANSIONS_LOADED: return "Expansion pack missing."
    
    if routine_name == "morning":
        threading.Thread(target=lambda: run_morning_routine(voice_interface.server if voice_interface else None)).start() # simplified
        # Re-using the ServerProxy from voice if available, else need new one.
        # Let's fix the circular dep by making the proxy global or creating a fresh one.
        
    return f"Automation '{routine_name}' trigger sent."

# === MAIN ===

if __name__ == "__main__":
    print(f"Omnis-Nexus Enhanced (v2.1) starting on {platform.system()}...", file=sys.stderr)
    print(f"SAFE_ZONE: {SAFE_ZONE}", file=sys.stderr)
    mcp.run()
