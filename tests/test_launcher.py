"""
Test for Blender Launcher
"""

import unittest
from unittest.mock import MagicMock, patch
import os
from sys import path

# Ensure we can find the core module
path.append(".")
from core.launcher import launch_blender, get_default_blender_path

class TestLauncher(unittest.TestCase):
    
    @patch('time.sleep') # 1. Patch sleep so test runs instantly
    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_blender_success(self, mock_exists, mock_popen, mock_sleep):
        # --- Setup Mocks ---
        mock_exists.return_value = True
        
        # Create a mock process instance that Popen will return
        mock_process = MagicMock()
        
        # CRITICAL FIX: poll() returning None means "Process is still running"
        mock_process.poll.return_value = None 
        
        # CRITICAL FIX: communicate() must return (stdout, stderr) tuple just in case
        mock_process.communicate.return_value = ('Output', 'Errors')
        
        # Assign the mock process to Popen
        mock_popen.return_value = mock_process
        
        # --- Execution ---
        config = {
            'blender_path': '/mock/blender',
        }
        
        process = launch_blender(config)
        
        # --- Assertions ---
        self.assertIsNotNone(process, "Process should not be None on success")
        self.assertEqual(process, mock_process)
        
        # Check Popen was called
        mock_popen.assert_called_once()
        
        # Check arguments passed to Popen
        # call_args[0] are positional args, call_args[0][0] is the first arg (the command list)
        cmd_list = mock_popen.call_args[0][0]
        self.assertEqual(cmd_list[0], '/mock/blender')

    @patch('time.sleep')
    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_blender_crash_immediately(self, mock_exists, mock_popen, mock_sleep):
        """Test the scenario where Blender starts but crashes instantly (e.g. missing DLL)"""
        mock_exists.return_value = True
        
        mock_process = MagicMock()
        # Simulate crash: poll() returns an error code (e.g., 1) instead of None
        mock_process.poll.return_value = 1 
        # Simulate the logs captured from the crash
        mock_process.communicate.return_value = ('', 'Critical Error: Missing Lib')
        
        mock_popen.return_value = mock_process
        
        process = launch_blender({'blender_path': '/mock/blender'})
        
        # Expecting None because the launcher detects the crash
        self.assertIsNone(process, "Process should be None if it crashes immediately")

    @patch('os.path.exists')
    def test_launch_blender_not_found(self, mock_exists):
        # Mock paths NOT existing
        mock_exists.return_value = False
        
        config = {
            'blender_path': '/nonexistent/blender',
        }
        
        process = launch_blender(config)
        self.assertIsNone(process)

    def test_get_default_path(self):
        # Just ensure it runs without error
        path = get_default_blender_path()
        # Result depends on system, so just check it returns string or None
        if path:
            self.assertIsInstance(path, str)

if __name__ == '__main__':
    unittest.main()