import re
from pathlib import Path

def check_firmware_syntax():
    p = Path(r"c:\Users\tylor\Desktop\the apex signel\SAGE-Framework\hardware\firmware_esp32_v5.cpp")
    if not p.exists():
        print(f"Error: {p} not found.")
        return

    content = p.read_text(encoding="utf-8")
    
    # Check for basic balanced braces
    if content.count('{') != content.count('}'):
        print(f"FAILED: Unbalanced braces ({{: {content.count('{')}, }}: {content.count('}')})")
    else:
        print("PASSED: Braces balanced.")

    # Check for semi-colons (rough heuristic for line termination)
    # Exclude lines that are comments or start with # or end in { or }
    lines = content.splitlines()
    errs = 0
    for i, line in enumerate(lines):
        clean = line.strip()
        if not clean or clean.startswith("//") or clean.startswith("#") or clean.endswith("{") or clean.endswith("}") or clean.endswith(",") or clean.endswith(";") or clean.endswith(":"):
            continue
        # Check if line seems to be a statement but misses semicolon
        if re.search(r'[a-zA-Z0-9)]$', clean):
            print(f"WARNING: Potential missing semicolon on line {i+1}: '{clean}'")
            errs += 1
    
    if errs == 0:
        print("PASSED: Semicolon check (heuristic).")

    # Check for mandatory ESP32/SAGE symbols
    symbols = ["setup", "loop", "MIRROR_DAEMON", "Sync Shield", "phi", "injection_count"]
    for s in symbols:
        if s.lower() not in content.lower():
            print(f"WARNING: Mandatory symbol '{s}' not found in firmware.")
        else:
            print(f"PASSED: Found symbol '{s}'.")

if __name__ == "__main__":
    check_firmware_syntax()
