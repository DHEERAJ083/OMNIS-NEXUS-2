# Omnis-Nexus Project Architecture & Diagrams

This document visualizes the structure and validation flow of the Omnis-Nexus system.

## 1. High-Level System Architecture

This diagram illustrates how Omnis-Nexus fits into the broader ecosystem, bridging the gap between the LLM (Claude) and the Operating System.

```mermaid
graph TD
    subgraph "User Layer"
        User[User / Operator]
        Voice[Mic / Voice Input]
    end

    subgraph "Interface Layer"
        Claude[Claude Desktop / LLM]
        MCP[Omnis-Nexus MCP Server]
    end

    subgraph "Core Logic (Omnis Nexus)"
        Server[omnis_nexus_server.py]
        Config[Config & Security<br/>(config.json / Env)]
        
        subgraph "Expansion Pack"
            NexusVoice[Nexus Voice Module]
            Auto[Automation Routines]
            Healer[Sentinel Healers]
        end
    end

    subgraph "OS Abstraction Layer"
        Shell[Shell / Terminal]
        FS[File System]
        Input[Mouse / Keyboard]
        Vision[Screen Capture]
        Proc[Process Manager]
    end

    %% Connections
    User -->|Text Prompts| Claude
    User -->|Voice Commands "Nexus..."| Voice
    Voice -->|Audio| NexusVoice
    
    Claude <-->|JSON-RPC 2.0| MCP
    MCP --> Server
    
    Server -->|Imports| NexusVoice
    Server -->|Imports| Auto
    Server -->|Imports| Healer
    Server -.->|Reads| Config

    Server -->|Execute| Shell
    Server -->|Read/Write| FS
    Server -->|Control| Input
    Server -->|See| Vision
    Server -->|Manage| Proc
    NexusVoice -->|Triggers| Auto
```

## 2. Component Structure (Container Diagram)

A detailed look at the internal components of the Omnis-Nexus Python codebase.

```mermaid
classDiagram
    class OmnisNexusServer {
        +list_tools()
        +call_tool()
        +_validate_command()
        +run_command()
        +read_file()
        +write_file()
    }
    
    class NexusVoice {
        -queue: SpeechQueue
        +start_voice_mode()
        +pyaudio_listen()
        +pyttsx3_speak()
    }

    class Automations {
        +run_morning_routine()
        +run_deep_work()
    }

    class Healers {
        +check_battery_critical()
        +restart_stuck_process()
    }

    class SecurityLayer {
        +SAFE_ZONE: Path
        +BLACKLIST: List
        +verify_path()
        +audit_log()
    }

    OmnisNexusServer *-- SecurityLayer : enforces
    OmnisNexusServer *-- NexusVoice : integrates
    OmnisNexusServer *-- Automations : executes
    OmnisNexusServer *-- Healer : triggers
```

## 3. Operational Workflow (Sequence Diagram)

Example: **"Morning Routine"** execution flow via Voice Command.

```mermaid
sequenceDiagram
    participant U as User
    participant V as Nexus Voice
    participant S as MCP Server
    participant A as Automations
    participant OS as Operating System

    U->>V: "Nexus, start morning routine"
    activate V
    V->>V: STT (Speech to Text)
    V->>V: Match Keyword "morning routine"
    
    V->>S: Trigger run_automation("morning")
    activate S
    S->>S: Validate Automation Request
    
    S->>A: execute_routine("morning")
    activate A
    
    par Launch Apps
        A->>OS: subprocess.run("chrome.exe")
        A->>OS: subprocess.run("outlook.exe")
    and Check Health
        A->>S: system_stats()
        S-->>A: {CPU: 12%, Battery: 98%}
    end
    
    A-->>S: Success
    deactivate A
    
    S-->>V: Automation Complated
    deactivate S
    
    V->>U: TTS "Morning routine initialized."
    deactivate V
```
