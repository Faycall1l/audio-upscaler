#!/usr/bin/env python3
"""
Test Runner for Audio Upscaler

This script runs all tests for the Audio Upscaler project.
"""

import unittest
import sys
import os

if __name__ == '__main__':
    # Add the parent directory to the path so we can import the tests
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Discover and run all tests
    test_suite = unittest.defaultTestLoader.discover(
        start_dir=os.path.dirname(__file__),
        pattern='test_*.py'
    )
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful())
