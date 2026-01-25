# Omnis-Nexus MCP Server

**Omnis-Nexus** is a high-performance, cross-platform hardware abstraction layer and system control server for LLMs (Claude, Gemini, etc.), built on the Model Context Protocol (MCP).

## Features

- **Core System**: CPU/RAM/Battery telemetry, shell command execution, filesystem access.
- **Process Management**: List, kill, and inspect processes.
- **Visual Perception**: Screen capture, region monitoring, and visual search (click-by-image).
- **Application Control**: Launch apps, manage windows, type/click automation.
- **Sentinel Monitoring**: Background watchers for UI changes, log files, and hardware health.
- **Safety**: "Sandbox Guard" file protection, rollback capability, audit logging.
- **Automation**: Cron-style task scheduling.

## Installation

1.  **Prerequisites**: Python 3.10+
2.  **Setup**:
    ```powershell
    ./setup.ps1  # Windows
    # OR
    ./setup.sh   # macOS/Linux
    ```

## Configuration

The server can be configured via `omnis_config.json` or `OMNIS_SAFE_ZONE` environment variable.

## Usage

Connect via your MCP Client (e.g., Claude Desktop). See `docs/TOOL_REFERENCE.md` for a full list of available tools.

## Structure

- `omnis_nexus_server.py`: Main server entry point.
- `docs/`: Documentation and references.
- `tests/`: Verification scripts.
- `logs/`: Application logs.
- `.rollback/`: File operation backups (safety feature).
