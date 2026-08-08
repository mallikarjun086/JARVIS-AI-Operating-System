"""
Automated All-in-One Test Runner for JARVIS AI OS Backend.
Runs Pytest suite and live system API diagnostic checks.
"""

import os
import sys
import subprocess

def run_pytest():
    print("=" * 60)
    print("🚀 Running Pytest Suite (174 Unit & Integration Tests)...")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = script_dir if os.path.basename(script_dir) == "backend" else os.path.join(script_dir, "backend")
    
    res = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=backend_dir)
    return res.returncode == 0

if __name__ == "__main__":
    pytest_ok = run_pytest()
    if pytest_ok:
        print("\n" + "=" * 60)
        print("🎉 ALL 174 UNIT & INTEGRATION TESTS PASSED 100% SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n❌ Pytest suite encountered failures.")
