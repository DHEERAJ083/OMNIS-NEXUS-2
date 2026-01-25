import unittest
from unittest.mock import MagicMock
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from nexus_expansions.automations.routines import run_morning_routine, run_deep_work

class TestRoutines(unittest.TestCase):
    def setUp(self):
        self.mock_server = MagicMock()
        self.mock_server.system_stats.return_value = {
            "battery": {"percent": 100, "plugged": True},
            "cpu_percent": 10
        }

    def test_morning_routine(self):
        run_morning_routine(self.mock_server)
        
        # Verify launch calls
        self.mock_server.launch_application.assert_any_call("chrome")
        self.mock_server.launch_application.assert_any_call("outlook")
        self.mock_server.focus_window.assert_called_with("Outlook")

    def test_deep_work_routine(self):
        run_deep_work(self.mock_server)
        
        # Verify kill calls
        self.mock_server.kill_process.assert_any_call("discord")
        self.mock_server.kill_process.assert_any_call("steam")
        # Verify music
        self.mock_server.launch_application.assert_called_with("spotify")

if __name__ == '__main__':
    unittest.main()
