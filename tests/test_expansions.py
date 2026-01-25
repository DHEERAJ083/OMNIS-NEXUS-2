import sys
sys.path.append(".")

print("Testing Expansion Pack Imports...")

try:
    import nexus_expansions.voice.nexus_voice
    print("  [PASS] Voice Module Found")
    
    import nexus_expansions.automations.routines
    print("  [PASS] Automation Routines Found")
    
    import nexus_expansions.healers.repair_logic
    print("  [PASS] Healer Logic Found")
    
    print("\nSimulating Server Proxy for Voice...")
    
    class MockServer:
        def system_stats(self): return {"cpu_percent": 10, "battery": {"percent": 90}}
        def launch_application(self, app): print(f"  > Launching {app}")
        def capture_screen(self): print("  > Click!")
        def notify_operator(self, t, m): print(f"  > Notify: {t} - {m}")
        def focus_window(self, t): print(f"  > Focus {t}")
        def kill_process(self, p): print(f"  > Kill {p}")

    voice = nexus_expansions.voice.nexus_voice.NexusVoice(MockServer())
    print("  [PASS] Voice Class Instantiated")
    
    # Test routine execution
    print("\nTesting 'Morning Routine' simulation...")
    nexus_expansions.automations.routines.run_morning_routine(MockServer())
    
    print("\n[SUCCESS] All Expansion Tests Passed!")

except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Runtime Error: {e}")
    sys.exit(1)
