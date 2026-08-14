# test_api.py - Main Test Suite Runner for WeatherSense AI
import unittest
import sys
import os

if __name__ == "__main__":
    # Discover and run all test modules in the 'tests' directory
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(not result.wasSuccessful())
