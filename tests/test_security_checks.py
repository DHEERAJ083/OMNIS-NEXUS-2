import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from omnis_nexus_server import _validate_command, CONFIG

class TestSecurity(unittest.TestCase):
    def setUp(self):
        # Reset config for testing
        CONFIG["command_whitelist_enabled"] = False
        CONFIG["blocked_commands"] = ["rm -rf", "del /s", "format"]
        CONFIG["allowed_commands"] = ["ls", "echo"]

    def test_global_blocks(self):
        """Test that CRITICAL_BLOCKS works regardless of config."""
        self.assertFalse(_validate_command("rm -rf /"))
        self.assertFalse(_validate_command("foo; rm -rf /"))
        self.assertFalse(_validate_command("format c:"))

    def test_blacklist_mode(self):
        """Test configurable blacklist."""
        CONFIG["command_whitelist_enabled"] = False
        self.assertTrue(_validate_command("ls -la"))
        self.assertFalse(_validate_command("del /s *"))
        # Test fuzzy matching bypass attempt
        self.assertFalse(_validate_command("del  /s")) 

    def test_whitelist_mode(self):
        """Test strict whitelist mode."""
        CONFIG["command_whitelist_enabled"] = True
        self.assertTrue(_validate_command("ls"))
        self.assertTrue(_validate_command("echo hello"))
        self.assertFalse(_validate_command("cat secret.txt")) # Not in allowed list

if __name__ == '__main__':
    unittest.main()
