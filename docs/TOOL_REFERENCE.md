# Omnis-Nexus Enhanced - Tool Reference

## Core System Tools
- `system_stats()` - CPU, RAM, Battery telemetry
- `run_command(command)` - Execute shell commands (validated)
- `list_directory(path)` - List directory contents
- `read_file(path, force)` - Read files (safe zone enforced)
- `write_file(path, content, force)` - Write files (with rollback)
- `get_clipboard()` / `set_clipboard(content)` - Clipboard access

## Configuration
- `get_config(key)` - Get config value(s)
- `set_config(key, value)` - Update configuration
- **Config File**: `omnis_config.json`
- **Env Override**: `OMNIS_SAFE_ZONE`

## Process Management
- `list_processes()` - Top 50 processes by CPU
- `kill_process(pid_or_name, force)` - Terminate process
- `get_process_info(pid)` - Detailed process stats

## Enhanced Monitoring
- `disk_stats()` - Per-partition disk usage
- `network_stats()` - Network interface metrics

## Application Control
- `launch_application(app_name)` - Start apps
- `ui_click_element(x, y, clicks)` - Click at coordinates
- `ui_type_string(text, press_enter)` - Type into focused app
- `list_windows()` - Active window titles
- `focus_window(title)` - Bring window to front

## Visual Tools
- `capture_screen(filename)` - Full screenshot
- `capture_region(x, y, w, h, filename)` - Region capture
- `locate_and_click(image_path, confidence)` - Visual search & click

## Sentinel Monitoring
- `start_visual_watch(name, x, y, w, h, interval)` - Monitor UI regions
- `stop_monitor(name)` - Stop active monitor
- `notify_operator(title, message)` - System notifications

## Automation (NEW)
- `schedule_command(task_id, command, cron_time)` - Schedule commands (HH:MM format)
- `list_scheduled_tasks()` - View scheduled tasks
- `cancel_scheduled_task(task_id)` - Cancel schedule

## Safety Features
- Command whitelist/blacklist (configurable in `omnis_config.json`)
- File rollback (last 5 versions in `.rollback/`)
- Audit logging (`audit.log`)
- Safe zone enforcement (default: `~/RoboticsProjects`)

## Logs
- **Application Logs**: `./logs/omnis_nexus_YYYYMMDD.log` (rotating, 7 days)
- **Audit Trail**: `./audit.log` (all destructive operations)

## Total Tools: ~31
