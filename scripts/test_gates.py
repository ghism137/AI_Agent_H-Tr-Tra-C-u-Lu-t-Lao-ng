import os
import json
import subprocess
from pathlib import Path

def test_gate3_fails():
    print("Testing Gate 3...")
    # First, run the build script normally. Wait, the build script should fail because operations.json currently has "review_status": "pending" for the new operations!
    result = subprocess.run(
        ["python", "scripts/build_phase1_stage.py"],
        capture_output=True,
        text=True
    )
    
    if "Materialization failed" in result.stdout or "Materialization failed" in result.stderr:
        print("FAIL: Expected Gate 3 to fail gracefully, but it crashed. Oh wait, Gate 3 failing should stop the build.")
    
    with open("data/registry/build_status.json", "r", encoding="utf-8") as f:
        status = json.load(f)
        
    print(f"Gate 3 Status: {status.get('gate3')}")
    if status.get("gate3") == "FAIL":
        print("PASS: Gate 3 correctly failed when operations are pending.")
    else:
        print("ERROR: Gate 3 did not fail as expected.")

if __name__ == "__main__":
    test_gate3_fails()
