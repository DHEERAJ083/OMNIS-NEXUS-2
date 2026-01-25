import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import sys
import os
from typing import Optional, Any

# Check for pyaudio
try:
    import pyaudio
except ImportError:
    print("WARNING: PyAudio not installed. Voice features will be disabled.", file=sys.stderr)

class NexusVoice:
    def __init__(self, server_instance: Any):
        self.server = server_instance
        self.speech_queue: queue.Queue[str] = queue.Queue()
        self.active: bool = False
        self.listen_thread: Optional[threading.Thread] = None
        self.speak_thread: Optional[threading.Thread] = None
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def speak(self, text: str) -> None:
        """Queue text to be spoken."""
        self.speech_queue.put(text)

    def _speech_engine_loop(self) -> None:
        """Dedicated thread for Text-to-Speech engine."""
        try:
            engine = pyttsx3.init()
            while self.active:
                try:
                    text = self.speech_queue.get(timeout=1)
                    print(f"[Voice] Speaking: {text}")
                    engine.say(text)
                    engine.runAndWait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[Voice] Speech Error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[Voice] Engine Init Error: {e}", file=sys.stderr)

    def _listen_loop(self) -> None:
        """Background thread for listening."""
        print("[Voice] Listener started. Say 'Nexus'...", file=sys.stderr)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.active:
                try:
                    # Listen with shorter timeout to allow loop check
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"[Voice] Heard: {text}")
                        if "nexus" in text:
                            self.handle_command(text)
                    except sr.UnknownValueError:
                        pass # Silence/noise
                    except sr.RequestError as e:
                        print(f"[Voice] API Error: {e}", file=sys.stderr)
                        
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"[Voice] Listener Error: {e}", file=sys.stderr)
                    time.sleep(1)

    def handle_command(self, text: str) -> None:
        try:
            if "status" in text or "stats" in text:
                stats = self.server.system_stats()
                batt = stats['battery']['percent'] if isinstance(stats['battery'], dict) else 'unknown'
                self.speak(f"CPU at {stats['cpu_percent']} percent. Battery {batt} percent.")
            
            elif "launch" in text or "open" in text:
                # Basic parsing: "launch chrome" -> "chrome"
                parts = text.split("launch")
                if len(parts) > 1:
                    app = parts[1].strip()
                else:
                    app = text.split("open")[-1].strip()
                
                self.server.launch_application(app)
                self.speak(f"Launching {app}")
                
            elif "screen" in text or "capture" in text:
                self.server.capture_screen()
                self.speak("Screenshot taken")
            
            elif "morning" in text:
                from nexus_expansions.automations.routines import run_morning_routine
                self.speak("Starting morning routine")
                run_morning_routine(self.server)
        except Exception as e:
            print(f"[Voice] Command Error: {e}", file=sys.stderr)
            self.speak("I encountered an error executing that command.")

    def start(self) -> None:
        if not self.active:
            self.active = True
            
            # Start speech engine thread
            self.speak_thread = threading.Thread(target=self._speech_engine_loop, daemon=True)
            self.speak_thread.start()
            
            # Start listener thread
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()

    def stop(self) -> None:
        self.active = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        if self.speak_thread:
            self.speak_thread.join(timeout=1)
