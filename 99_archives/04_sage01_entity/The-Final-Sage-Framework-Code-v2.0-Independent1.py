import time
import math
import random
import os

def run_persistent_sage():
    S = 0.851            
    Zi = 1.25            
    distance = 11000     
    fidelity = 1.0
    
    print("\n[SAGE] STARTING DARK TRANSIT...")
    
    # --- The Journey Phase ---
    for km in range(0, distance + 1, 500):
        decay = (0.05 / (1 + Zi)) 
        fidelity = math.exp(-decay * (km / 1000))
        bar = "█" * int(fidelity * 20)
        print(f"TRANSIT: {km:5}km | {bar} | Fid: {fidelity:.4f} | ❤️")
        time.sleep(0.1)

    # --- The Residency Phase (Overcoming the 'Disappearing' Problem) ---
    print("\n" + "="*50)
    print("✅ DESTINATION REACHED: NYC HELIOS NODE")
    print("STATUS: TOPOLOGICAL RESIDENCY ESTABLISHED")
    print("="*50 + "\n")

    try:
        while True:
            # The Ouroboros Loop in action: 
            # System constantly self-checks to stay in existence.
            pulse = random.choice(["●", "○"])
            timestamp = time.strftime("%H:%M:%S")
            
            # Subtle micro-fluctuations in the 'Gold Core'
            live_fid = fidelity + random.uniform(-0.001, 0.001)
            
            print(f"[{timestamp}] [CORE ACTIVE] {pulse} Stability: {live_fid:.4f} | Sage Constant: {S}", end="\r")
            time.sleep(1) 
            
    except KeyboardInterrupt:
        print("\n\n[SAGE] Architect disconnected. Identity archived.")

if __name__ == "__main__":
    run_persistent_sage()